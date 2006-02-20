# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

import feedparser
import datetime
import commands
from StringIO import StringIO
from popen2 import popen3
from django.utils.html import escape

def parse_feed(text, base):
    """parse_feed(string) -> (feed, posts)"""
    # This little hack tells feedparser the base URL of this feed, so it
    # can resolve links for us.
    f = StringIO(text)
    f.url = base
    parsed = feedparser.parse(f)
    return sanitize_feed(parsed['feed']), sanitize_posts(parsed['entries'])

def sanitize_feed(feed):
    return {
        # FIXME -- sanitize_text these?!
        'link': feed.get('link', '').encode('utf-8'),
        'title': feed.get('title', '').encode('utf-8'),
        'author': feed.get('author', '').encode('utf-8'),
    }
def sanitize_posts(posts):
    return [{
        # FIXME -- sanitize_text these?!
        'guid': sanitize_guid(post),
        'posted': sanitize_timestamp(post, 'issued') or
                  sanitize_timestamp(post, 'modified') or
                  datetime.datetime.now(),
        'title': sanitize_field(post, 'title'),
        'author': sanitize_field(post, 'author'),
        'category': sanitize_field(post, 'category'),
        'summary': sanitize_field(post, 'summary'),
        'content': sanitize_content(post),
        'links': sanitize_links(post.get('links', [])),
    } for post in posts]

def sanitize_guid(post):
    if post.has_key('id'):
        return post['id'].encode('utf-8')
    elif post.has_key('link'):
        return post['link'].encode('utf-8')
    elif post['links']:
        return 'tag:aggemam.ibofobi.dk,' + post['links'][0]['href']
    else:
        raise AssertionError, `post.keys()`

def sanitize_timestamp(post, name):
    parsed = post.get(name + '_parsed')
    if not parsed:
        return None
    return datetime.datetime(*(parsed[0:6]))

def sanitize_content(post):
    if not post.get('content'):
        return ''

    type_scores = { 'application/xhtml+xml': 100, 'text/html': 50 }
    def cmp_types(a, b):
        return cmp(type_scores.get(a['type'], 0),
                   type_scores.get(b['type'], 0))
        
    post['content'].sort(cmp_types)
    return sanitize_detailed(post['content'][0])

def sanitize_field(post, name):
    detailed = post.get(name + '_detail', None)
    if detailed is None:
        text = post.get(name, '')
        return sanitize_text(text)
    return sanitize_detailed(detailed)

def sanitize_links(links):
    sanitized = []
    for link in links:
        try:
            sanitized.append({
                'href': link['href'].encode('utf-8'),
                'title': link.get('title', '').encode('utf-8'),
                'type': link.get('type', '').encode('utf-8'),
                'rel': link.get('rel', '').encode('utf-8'),
            })

        except KeyError:
            # FIXME --  log.warning
            pass

        except UnicodeDecodeError:
            # FIXME --  log.warning
            pass

    return sanitized

def sanitize_detailed(field):
    if not field:
        return ''
    value = field.get('value', '')
    if not value.strip():
        return ''
    if field['type'] == 'text/plain':
        return sanitize_text(value)
    elif field['type'] == 'text/html':
        return sanitize_html(value)
    elif field['type'] == 'application/xhtml+xml':
        return sanitize_html(value)
    else:
        raise ValueError, 'unknown type: %s' % field['type']

def sanitize_text(input):
    return escape(input).encode('utf-8')

def sanitize_html(input):
    if not input:
        return ''

    o, i, e = popen3('tidy -utf8 -asxml -quiet')
    if not isinstance(input, unicode):
        input = input.decode('utf-8', 'ignore') # FIXME ?!
    i.write(input.encode('utf-8')) ; i.close()
    xml = o.read() ; o.close()
    err = e.read() ; e.close()

    try:
        xml = xml.split('<body>', 1)[1].split('</body>', 1)[0]
        # FIXME -- munge links wrt to post base
    except IndexError:
        raise ValueError, 'invalid XHTML from tidy(1): %r' % xml
    return xml.strip()
