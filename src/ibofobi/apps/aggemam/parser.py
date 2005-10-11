import feedparser
import datetime
import commands
from StringIO import StringIO
from popen2 import popen3

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
        'title': post.get('title', '').encode('utf-8'),
        'author': post.get('author', '').encode('utf-8'),
        'category': post.get('category', '').encode('utf-8'),
        'summary': post.get('summary', '').encode('utf-8'),
        'content': sanitize_content(post),
        'links': sanitize_links(post.get('links', [])),
    } for post in posts]

def sanitize_guid(post):
    return post['id'].encode('utf-8')

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
    return sanitize_field(post['content'][0])

def sanitize_links(links):
    return [ {
        'href': link['href'].encode('utf-8'),
        'title': link.get('title', '').encode('utf-8'),
        'type': link.get('type', '').encode('utf-8'),
        'rel': link.get('rel', '').encode('utf-8'),
    } for link in links ]

def sanitize_field(field):
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
    return abml.quote(input)

def sanitize_html(input):
    if not input:
        return ''

    o, i, e = popen3('tidy -utf8 -asxml -quiet')
    i.write(input.encode('utf-8')) ; i.close()
    xml = o.read() ; o.close()
    err = e.read() ; e.close()

    try:
        xml = xml.split('<body>', 1)[1].split('</body>', 1)[0]
        # FIXME -- munge links wrt to post base
    except IndexError:
        raise ValueError, 'invalid XHTML from tidy(1): %r' % xml
    return xml.strip()
