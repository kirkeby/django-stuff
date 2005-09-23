import feedparser

def parse_feed(text):
    parsed = feedparser.parse(text)
    v = parsed['version']
    if v == 'atom03':
        return sanitize_atom03(parsed)
    else:
        raise AssertionError, 'unknown version: %s' % v

def sanitize_atom03(parsed):
    return {
        # FIXME -- sanitize_text these?!
        'link': parsed['feed']['link'],
        'title': parsed['feed']['title'],
        'author': parsed['feed']['author'],
        'posts': sanitize_atom03_posts(parsed['entries']),
    }
def sanitize_atom03_posts(entries):
    posts = []
    for e in entries:
        pass
    return posts

###
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

    input = input.encode('utf8')
    argv = ['tidy', '-utf8', '-asxml', '-quiet']
    output, err = commands.filter(argv[0], argv, input)
    html = output.decode('utf8')

    try:
        xml = html.split('<body>', 1)[1].split('</body>', 1)[0]
        # FIXME -- munge links wrt to post base
    except IndexError:
        raise ValueError, 'invalid XHTML from tidy(1): %r' % html
    return xml.strip()
