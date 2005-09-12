from django.conf.urls.defaults import *

urlpatterns = patterns('ibofobi.apps.blog.views.blog',
    (r'^$', 'latest'),
    (r'^feeds/$', 'feeds_index'),
    (r'^feeds/latest/$', 'latest', {'format': 'atom'}),
    (r'^feeds/tags/(?P<slug>[\w-]+)/$', 'tag_posts', {'format': 'atom', 'limit': 5}),
    (r'^tags/$', 'tag_index'),
    (r'^tags/(?P<slug>[\w-]+)/$', 'tag_posts'),
    (r'^archive/$', 'archive_index'),
    (r'^archive/(?P<year>\d+)/$', 'archive_year'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/$', 'archive_month'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'archive_day'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[\w-]+)/$', 'post'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[\w-]+)/preview-comment/$', 'preview_comment'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[\w-]+)/post-comment/$', 'post_comment'),
    (r'^admin/', include('ibofobi.apps.blog.urls.admin')),
)
