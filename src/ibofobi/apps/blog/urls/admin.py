from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.blog.views.admin',
    (r'^drafts/$', 'draft_index'),
    (r'^drafts/(?P<draft_id>\d+)/$', 'draft_edit'),
)
