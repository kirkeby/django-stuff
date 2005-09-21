from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.fresh.views.status',
    (r'^referrers/$', 'referrers'),
)
