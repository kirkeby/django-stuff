def wrap(field, arg):
    return str(field).replace('<textarea ', '<textarea wrap="%s" ' % arg)

from django.core import template
template.register_filter('wrap', wrap, True)
