import os
import popen2

markdown_pl = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'Markdown.pl')
markdown_cmd = ['perl', markdown_pl]

def markdown(doc, arg):
    # FIXME -- handle unicode
    chld_out, chld_in, chld_err = popen2.popen3(markdown_cmd)
    chld_in.write(doc)
    chld_in.close()
    res = chld_out.read()
    chld_out.close()
    err = chld_err.read()
    chld_err.close()

    if err:
        raise AssertionError, err
    return res

from django.core import template
template.register_filter('markdown', markdown, False)
