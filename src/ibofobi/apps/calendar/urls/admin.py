# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.conf.urls.defaults import *

info_dict = {
    'app_label': 'calendar',
    'module_name': 'events',
}

urlpatterns = patterns('django.views.generic.create_update',
   (r'^edit/(?P<object_id>\d+)/$', 'update_object', info_dict),
   (r'^delete/(?P<object_id>\d+)/$', 'delete_object', 
        dict(info_dict, post_delete_redirect='/calendar/')),
)
