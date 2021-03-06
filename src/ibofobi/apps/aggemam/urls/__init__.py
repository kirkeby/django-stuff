# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.aggemam.views.public',
    (r'^$', 'index'),
    (r'^subscribe/$', 'subscribe'),
    (r'^subscriptions/$', 'list_subscriptions'),
    (r'^unread-posts/$', 'list_unread_posts'),
    (r'feeds/(?P<feed_id>\d+)/$', 'feed_index'),
)
