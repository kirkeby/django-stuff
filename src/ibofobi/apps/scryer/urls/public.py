# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.scryer.views.public',
    (r'^$', 'pageview'),
)
