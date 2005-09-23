from django.models.aggemam import feeds
from django.models.aggemam import feedupdates
from django.models.aggemam import messages

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

        fu = feedupdates.get_object(pk=fu.id) # FIXME
        severity = 3
        short = 'Created feed-update %r' % fu
        detailed = None

    except:
        severity = 9
        short = 'Error updating feed %r' % feed
        e, v, t = sys.exc_info()
        detailed = '\n'.join(traceback.format_exception(e, v, t))

    messages.Message(severity=severity, short=short, detailed=detailed).save()

for update in feedupdates.get_list(processed__exact=False):
    print repr(update)

    try:
        update.processed = True
        update.save()

        p = parser.parse_feed(update.http_content)

        feed.title = p['title'].encode('utf8')
        feed.author = p['author'].encode('utf8')
        feed.link = p['link'].encode('utf8')
        feed.save()

        severity = 3
        short = 'Processed feed-update %r' % update
        detailed = None

    except:
        raise
        severity = 9
        short = 'Error processing feed-update %r' % update
        e, v, t = sys.exc_info()
        detailed = '\n'.join(traceback.format_exception(e, v, t))

    messages.Message(severity=severity, short=short, detailed=detailed).save()
