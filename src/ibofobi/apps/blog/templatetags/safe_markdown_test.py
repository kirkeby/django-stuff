from safe_markdown import render

__render = render
def render(doc):
    return __render(doc).replace('\n', ' ').replace('  ', ' ').strip()

# Bare-bones tests
def test_empty():
    assert render('') == ''
def test_text():
    assert render('Hello, World!') == '<p>Hello, World!</p>'
def test_ampersand():
    assert render('One & Two') == '<p>One &amp; Two</p>'

# Paragraph tests
def test_paragraph():
    assert render('One,\nTwo') == '<p>One, Two</p>'
def test_paragraphs():
    assert render('One,\nTwo\n\nThree') == '<p>One, Two</p> <p>Three</p>'
def test_paragraphs():
    assert render('One,\nTwo\n\nThree\n\n') == '<p>One, Two</p> <p>Three</p>'
def test_paragraph_bq():
    assert render('One,\n> Two') == '<p>One,</p> <blockquote><p>Two</p></blockquote>'

# Blockquote tests
def test_blockquote():
    assert render('> Hello,') == '<blockquote><p>Hello,</p></blockquote>'
    assert render('> Hello,\n> World!') == '<blockquote><p>Hello, World!</p></blockquote>'
def test_blockquotes():
    assert render('> Hello,\n\n> World!') == '<blockquote><p>Hello,</p></blockquote> <blockquote><p>World!</p></blockquote>'
def test_nested_blockquotes():
    assert render('> Hello,\n> > World!') == '<blockquote><p>Hello,</p> <blockquote><p>World!</p></blockquote></blockquote>'

# Code-block tests
def test_codeblock():
    assert __render('    def hello_world():\n      print "Hello, World!"') == \
           '<pre><code>def hello_world():\n  print &quot;Hello, World!&quot;</code></pre>'

def test_strong():
    assert render('*Strong*') == '<p><strong>Strong</strong></p>'
    assert render('*_strong-emphasised_*') == '<p><strong><em>strong-emphasised</em></strong></p>'
    assert render('_*strong-emphasised*_') == '<p>_<strong>strong-emphasised</strong>_</p>'
def test_code():
    assert render('`code[42]`') == '<p><tt>code[42]</tt></p>'
def test_emphasised():
    assert render('_Emphasised_') == '<p><em>Emphasised</em></p>'
def test_link():
    assert render('[A link](http://example.com/)') == '<p><a href="http://example.com/" rel="nofollow">A link</a></p>'
    assert render('[*A link*](http://example.com/)') == '<p><a href="http://example.com/" rel="nofollow">*A link*</a></p>'
    assert render('[_A link_](http://example.com/)') == '<p><a href="http://example.com/" rel="nofollow">_A link_</a></p>'
