# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.calendar.views',
    (r'^$', 'index'),
    (r'^(?P<year>\d+)/(?P<month>\d+)/$', 'month'),
    (r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/create/$', 'create'),
)
