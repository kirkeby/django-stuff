"""A safe subset of Markdown <

Markdown syntax supported:

    This is a
    paragraph.

    This is a new paragraph.

    > This is a blockquote.
    >
    > > In reply to this (damn top-posters!)

        def a_longer_code_snippet():
            pass

    `a_short_code_snippet()` embedded in a paragraph.

    [Hello, World](http://www.example.com/)

    *strong*

    _emphasis_

Things I might add:

    Header level 1
    ==============

    Header level 2
    --------------

    1. An
    2. ordered
    3. list.

    * An
    * unordered
    * list.
"""

import re

from django.core.defaultfilters import escape

# Only return valid XHTML 1.0 Strict.
# Escape all HTML.
# Test cases!

def render(doc):
    lines = doc.split('\n')
    blocks = []
    while lines:
        blocks.append(pop_block(lines))
    return '\n'.join(blocks)

def pop_block(lines):
    while not lines[0].strip():
        lines.pop(0)
        if not lines:
            return ''
    
    if lines[0].startswith('>'):
        return pop_blockquote(lines)
    elif lines[0].startswith('    '):
        return pop_codeblock(lines)
    else:
        return pop_paragraph(lines)

def pop_paragraph(lines):
    p = []
    while lines:
        if not lines[0].strip():
            break
        if lines[0].startswith('>'):
            break
        if lines[0].startswith('    '):
            break

        p.append(lines.pop(0))

    return '<p>' + render_paragraph(escape('\n'.join(p), None)) + '</p>'

def pop_blockquote(lines):
    q = []
    while lines:
        if not lines[0].startswith('>'):
            break
        line = lines.pop(0)
        q.append(line[1:].lstrip())

    return '<blockquote>' + render('\n'.join(q)) + '</blockquote>'

def pop_codeblock(lines):
    c = []
    while lines:
        if not lines[0].startswith('    '):
            break
        c.append(lines.pop(0)[4:])
    return '<pre><code>' + escape('\n'.join(c), None) + '</code></pre>'

re_strong = re.compile(r"\*([\w&;/%#'_-]+)\*")
re_em = re.compile(r"_([\w&;/%#'*-]+)_")
re_link = re.compile(r"\[([\w&;/%#'_*-]+)\]\(([a-z]+://[a-zA-Z0-9._-]+/[^\]]+)\)")
re_link = re.compile(r"\[([^]]+)\]\(([a-z]+://[a-zA-Z0-9._-]+/[^)]*)\)")
def render_paragraph(p):
    p = re_strong.sub(r'<strong>\1</strong>', p)
    p = re_em.sub(r'<em>\1</em>', p)
    p = re_link.sub(r'<a href="\2" rel="nofollow">\1</a>', p)
    return p
