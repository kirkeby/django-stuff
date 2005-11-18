# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.scryer.views.admin',
    (r'^$', 'index'),
    (r'^top-pages/$', 'top_pages'),
    (r'^referrers/$', 'referrers'),
    (r'^page-views/$', 'page_views'),
    (r'^sessions/$', 'sessions'),
    (r'^sessions/(?P<session_key>[a-z0-9]+)/$', 'view_session'),
)
