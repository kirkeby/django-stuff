# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

import jsonlib

def json_escape(field, arg):
    return jsonlib.write(field)

from django.core import template
template.register_filter('json_escape', json_escape, False)
