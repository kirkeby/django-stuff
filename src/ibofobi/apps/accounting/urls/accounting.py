# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.accounting.views.accounting',
    (r'^$',
      'index'),
    (r'^(?P<account_slug>[a-z0-9_-]+)/$',
      'view'),
)
