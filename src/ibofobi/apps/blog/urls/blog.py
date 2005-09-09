from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.blog.views.blog',
    (r'^$', 'latest'),
    (r'^atom/$', 'atom'),
    (r'^tags/$', 'tag_index'),
    (r'^tags/(?P<slug>[\w-]+)/$', 'tag_posts'),
    (r'^archive/$', 'archive_index'),
    (r'^archive/(?P<year>\d+)/$', 'archive_year'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/$', 'archive_month'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'archive_day'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[\w-]+)/$', 'post'),
)
