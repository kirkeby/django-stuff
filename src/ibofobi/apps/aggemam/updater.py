from django.models.aggemam import feeds
from django.models.aggemam import feedupdates
from django.models.aggemam import messages
from django.models.aggemam import posts
from django.models.aggemam import links

from django.core.db import db

import sys
import traceback
import socket

import datetime
import fetcher
import parser

ramp_up_factor = 0.5
back_off_factor = 1.25
max_update_interval = 24 * 60
min_update_interval = 60

def fetch_feeds():
    for feed in feeds.get_list(update__exact=True,
                               next_update__lt=datetime.datetime.now()):
        print feed.url

        if feed.get_feedupdate_count(processed__exact=False):
            print 'skipping because of unprocessed updates'
            continue

        try:
            f = fetcher.Fetcher(feed.url)

            try:
                latest_update = feedupdates.get_latest(feed__id__exact=feed.id,
                                                       processed__exact=True,
                                                       result__exact='ok')
                if latest_update.http_etag:
                    f.request_headers['If-None-Match'] = latest_update.http_etag
                if latest_update.http_last_mod:
                    f.request_headers['If-Modified-Since'] = latest_update.http_last_mod

            except feedupdates.FeedUpdateDoesNotExist:
                latest_update = None
    
            try:
                f.fetch()
            except socket.error:
                fu = feedupdates.FeedUpdate(feed=feed, processed=False)
                fu.result = 'er'
                fu.save()

                continue

            if latest_update and f.body == latest_update.http_content:
                # not modified
                f.status = 304
                f.body = ''

            fu = feedupdates.FeedUpdate(feed=feed, processed=False)
            if f.status == 200:
                fu.result = 'ok'
            elif f.status == 304:
                fu.result = 'no'
            elif f.status == 404 or f.status == 410:
                fu.result = 'rm'
            elif f.status == 500:
                fu.result = 'er'
            else:
                fu.result = 'ot'

            fu.http_status_code = f.status
            fu.http_last_mod = f.parsed.get('Last-Modified')
            fu.http_etag = f.parsed.get('ETag')
            fu.http_headers = f.headers
            fu.http_content = f.body
            fu.save()

            #fu = feedupdates.get_object(pk=fu.id) # FIXME

            m = messages.Message(severity=3,
                                 short='Fetched feed %s' % feed,
                                 detailed=None)
            m.save()

            db.commit()

        except:
            db.rollback()
            
            traceback.print_exception(*(sys.exc_info()))

def process_updates():
    for update in feedupdates.get_list(processed__exact=False):
        print update

        try:
            feed = update.get_feed()

            if update.result == 'ok':
                new_posts = process_update_ok(feed, update)
            elif update.result == 'no':
                new_posts = 0
            elif update.result == 'rm':
                new_posts = 0
                feed.update = False
            elif update.result == 'er':
                new_posts = 0
                # FIXME -- set feed.update = False after N failed fetches?
            else:
                raise AssertionError, update.result

            if new_posts:
                feed.update_interval = int(feed.update_interval * ramp_up_factor)
            else:
                feed.update_interval = int(feed.update_interval * back_off_factor)
            feed.update_interval = max(feed.update_interval, min_update_interval)
            feed.update_interval = min(feed.update_interval, max_update_interval)

            i = datetime.timedelta(seconds=feed.update_interval * 60)
            feed.next_update = datetime.datetime.now() + i
            feed.save()

            update.processed = True
            update.save()

            db.commit()

        except:
            db.rollback()
        
            traceback.print_exception(*(sys.exc_info()))

def process_update_ok(feed, update):
    feed_prime, posts_prime = parser.parse_feed(update.http_content,
                                                feed.url)

    feed.title = feed_prime['title']
    feed.link = feed_prime['link']
    feed.save()

    new_posts = 0

    for p in posts_prime:
        if posts.get_count(guid__exact=p['guid']):
            continue

        post = posts.Post(feed=feed, guid=p['guid'])
        post.posted = p['posted']
        post.title = p['title']
        post.author = p['author'] or feed_prime['author']
        post.category = p['category']
        post.summary = p['summary']
        post.content = p['content']
        post.save()

        for l in p['links']:
            link = links.Link(post=post)
            link.href = l['href']
            link.type = l['type']
            link.title = l['title']
            link.save()

        new_posts = new_posts + 1

    m = messages.Message(severity=3,
                         short='Processed %s' % update,
                         detailed=None)
    m.save()

    return new_posts

if __name__ == '__main__':
    import sys

    if '--fetch' in sys.argv:
        fetch_feeds()
    if '--process-updates' in sys.argv:
        process_updates()
