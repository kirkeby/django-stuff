from django.models.aggemam import feeds
from django.models.aggemam import feedupdates
from django.models.aggemam import messages
from django.models.aggemam import posts
from django.models.aggemam import links

from django.core.db import db

import sys
import traceback

import fetcher
import parser

for feed in feeds.get_list(update__exact=True):
    print feed.url

    if feed.get_feedupdate_count(processed__exact=False):
        print 'skipping because of unprocessed updates'
        continue

    try:
        f = fetcher.Fetcher(feed.url)
        f.fetch()

        fu = feedupdates.FeedUpdate(feed=feed, processed=False)
        if f.status == 200:
            fu.result = 'ok'
        elif f.status == 404 or f.status == 410:
            fu.result = 'rm'
        elif f.status == 500:
            fu.status = 'er'
        else:
            fu.status = 'ot'

        fu.http_status_code = f.status
        fu.http_last_mod = None
        fu.http_etag = None
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

for update in feedupdates.get_list(processed__exact=False):
    print repr(update)

    try:
        feed = update.get_feed()

        feed_prime, posts_prime = parser.parse_feed(update.http_content,
                                                    feed.url)

        feed.title = feed_prime['title']
        feed.link = feed_prime['link']
        feed.save()

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

        m = messages.Message(severity=3,
                             short='Processed %s' % update,
                             detailed=None)
        m.save()

        #update.processed = True
        update.save()

        db.commit()

    except:
        db.rollback()
    
        traceback.print_exception(*(sys.exc_info()))
