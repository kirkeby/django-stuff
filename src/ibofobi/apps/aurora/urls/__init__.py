# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import include, patterns

urlpatterns = patterns('ibofobi.apps.aurora.views',
    (r'^$', 'index'),
    (r'^torrent/(?P<t_id>\d+)/$', 'torrent'),
    (r'^torrent/(?P<t_id>\d+)/pause/$', 'pause'),
    (r'^torrent/(?P<t_id>\d+)/resume/$', 'resume'),
    (r'^add/$', 'add'),
)
