from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.scryer.views.public',
    (r'^$', 'pageview'),
)
