# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

def wrap(field, arg):
    return str(field).replace('<textarea ', '<textarea wrap="%s" ' % arg)

from django.core import template
template.register_filter('wrap', wrap, True)
