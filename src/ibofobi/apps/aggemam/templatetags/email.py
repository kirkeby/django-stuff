# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

def indent_lines(field, arg):
    return field.replace('\n', '\n    ')

from django.core import template
template.register_filter('indent_lines', indent_lines, False)
