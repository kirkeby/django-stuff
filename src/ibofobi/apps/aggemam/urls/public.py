from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.aggemam.views.public',
    (r'^$', 'index'),
    (r'^subscriptions/$', 'list_subscriptions'),
    (r'^unread-posts/$', 'list_unread_posts'),
)
