# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

import types

from xhtml import xhtml_to_html
from xhtml import XHTMLAsHTMLMiddleware

from ibofobi.utils.test.BeautifulSoup import BeautifulSoup
def xhtml_to_soup(doc):
    bs = BeautifulSoup()
    bs.feed(xhtml_to_html(DOCUMENT_TEMPLATE % doc))
    return bs

DOCUMENT_TEMPLATE = '''<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<title>Some Test(tm)</title>
</head>
<body>%s</body>
</html>
'''

def test_normal_element():
    soup = xhtml_to_soup("<p class='test'>Test</p>")
    assert soup.p['class'] == 'test'
    assert soup.p.string == 'Test'

def test_attr():
    soup = xhtml_to_soup("<a href='a&amp;b'>Test</a>")
    assert soup.a['href'] == 'a&amp;b'
    assert soup.a.string == 'Test'

def test_empty_element():
    assert xhtml_to_html(DOCUMENT_TEMPLATE % '<br />').find('<body><br></body>') > -1

def test_cdata():
    soup = xhtml_to_soup('<![CDATA[ <This is CDATA> ]]>')
    assert soup.body.string.strip() == '&lt;This is CDATA&gt;', soup.body

def test_entitydefs():
    assert xhtml_to_soup('&#65;').body.string == 'A'
    for entitydef in ['&amp;', '&oslash;']:
        soup = xhtml_to_soup(entitydef)
        text = soup.body.string.strip()
        assert text == entitydef, text

def test_strip_non_html():
    soup = xhtml_to_soup('<xml:foo />')
    assert not soup.body.string
    try:
        soup.html['xml:lang']
    except:
        pass
    else:
        raise AssertionError
    try:
        soup.html['xmlns']
    except:
        pass
    else:
        raise AssertionError
    assert soup.html['lang'] == 'en'

def test_middleware():
    class MockResponse(dict):
        pass
    
    request = types.ClassType('MockRequest', (), {})
    request.META = {'HTTP_ACCEPT': ''}
    response = MockResponse()
    response['Content-Type'] = 'application/xhtml+xml'
    response.content = DOCUMENT_TEMPLATE % ''
    response.has_header = response.has_key
    response = XHTMLAsHTMLMiddleware().process_response(request, response)

    assert response['Content-Type'] == 'text/html'
