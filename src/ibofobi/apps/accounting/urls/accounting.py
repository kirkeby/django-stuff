from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.accounting.views.accounting',
    (r'^$',
      'index'),
    (r'^(?P<account_slug>[a-z0-9_-]+)/$',
      'view'),
)
