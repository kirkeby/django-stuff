from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.fresh.views.admin',
    (r'^referrers/$', 'referrers'),
)
