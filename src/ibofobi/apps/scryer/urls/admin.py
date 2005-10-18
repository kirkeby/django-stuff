from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.scryer.views.admin',
    (r'^$', 'index'),
    (r'^page-views/$', 'page_views'),
    (r'^referrers/$', 'referrers'),
    (r'^live/page-views/$', 'live_page_views'),
)
