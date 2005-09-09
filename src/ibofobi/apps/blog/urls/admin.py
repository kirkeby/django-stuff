from django.conf.urls.defaults import *

info_dict = {
    'app_label': 'blog',
    'module_name': 'drafts',
}

urlpatterns = patterns('',
    (r'^drafts/$', 'django.views.generic.list_detail.object_list', info_dict),
    (r'^drafts/create/$', 'django.views.generic.create_update.create_object', info_dict),
    (r'^drafts/update/(?P<object_id>\d+)/$', 'django.views.generic.create_update.update_object', info_dict),
    (r'^drafts/delete/(?P<object_id>\d+)/$', 'django.views.generic.create_update.delete_object', dict(info_dict, post_delete_redirect='../..')),
    (r'^drafts/view/(?P<object_id>\d+)/$', 'ibofobi.apps.blog.views.blog.preview_draft'),
    (r'^drafts/publish/(?P<object_id>\d+)/$', 'ibofobi.apps.blog.views.blog.publish_draft'),
)

