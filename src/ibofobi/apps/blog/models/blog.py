# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import meta
from django.core.cache import cache
from django.conf import settings
from django.models import auth

from ibofobi.apps.blog.markdown import markdown

class Category(meta.Model):
    name = meta.CharField('name', maxlength=30)
    slug = meta.SlugField('identifier', prepopulate_from=['name'])

    class META:
        module_name = 'categories'
        module_constants = {
            'settings': settings,
        }
        verbose_name_plural = 'categories'

        admin = meta.Admin()

    def get_absolute_url(self):
        return '%s/tags/%s/' % (settings.BLOG_URL, self.slug)

    def get_latest_post(self):
        p = self.get_post_list(listed__exact=True, order_by=['-posted'], limit=1)
        if p:
            return p[0]

    def get_listed_post_list(self, **kwargs):
        return self.get_post_list(listed__exact=True, **kwargs)

    def __repr__(self):
        return self.name

class Post(meta.Model):
    slug = meta.SlugField('slug',
                          unique_for_date='posted',
                          prepopulate_from=['title'],
                          help_text='The last part of the posts URL')
    tag = meta.CharField('tag',
                         help_text='A globally unique, immutable identifer', 
                         editable=False,
                         unique=True,
                         maxlength=100)
    listed = meta.BooleanField(help_text='Is post shown in the public views')
    posted = meta.DateTimeField('posted',
                                help_text='Date and time when post went public')
    title = meta.CharField(maxlength=100)
    content = meta.TextField(help_text='''Quick Markdown guide:
                                          <nobr><code>[A Link](http://example.com/)</code></nobr>,
                                          <code>*strong*</code>,
                                          <code>_emphasis_</code>,
                                          <nobr><code>&gt; blockquote</code></nobr>,
                                          <code>`code`</code>''')
    categories = meta.ManyToManyField(Category, blank=True)

    class META:
        get_latest_by = 'posted'

        module_constants = {
            'cache': cache,
            'settings': settings,
            'markdown': markdown,
            'cache_seconds': getattr(settings, 'BLOG_MARKDOWN_CACHE_SECONDS', 0),
        }

        admin = meta.Admin(
            fields = (
                (None, {'fields': ('title', 'slug', 'listed', 'posted')}),
                (None, {'fields': ('categories', 'content')}),
            ),
            list_filter = ['posted', 'listed'],
            list_display = ['title', 'posted', 'listed'],
        )

    def _pre_save(self):
        if not getattr(self, 'tag', None):
            fmt = getattr(settings, 'BLOG_TAG_FORMAT', 'tag:%s/archive/%d/%02d/%02d/%s/' % (settings.BLOG_URL, self.posted.year, self.posted.month, self.posted.day, self.slug))
            self.tag = fmt % dict(year=self.posted.year,
                                  month=self.posted.month,
                                  day=self.posted.day,
                                  slug=self.slug)

    def get_absolute_url(self):
        return '%s/archive/%d/%02d/%02d/%s/' % (settings.BLOG_URL, self.posted.year, self.posted.month, self.posted.day, self.slug)

    def get_next_post(self):
        return get_object(posted__gt=self.posted,
                          order_by=['posted'],
                          limit=1)

    def get_previous_post(self):
        return get_object(posted__lt=self.posted,
                          order_by=['-posted'],
                          limit=1)

    def get_content_rendered(self):
        """Return the content of this post, rendered as XHTML."""
        rendered = None
        if cache_seconds and self.listed:
            key = 'ibofobi.blog.markdown_cache.' + self.get_absolute_url()
            rendered = cache.get(key)
        if not rendered:
            rendered = markdown(self.content)
        if cache_seconds and self.listed:
            cache.set(key, rendered, cache_seconds)
        return rendered

    def get_previewed_comment_list(self):
        return self.get_comment_list(previewed__exact=True, order_by=['posted'])
    def get_previewed_comment_count(self):
        return self.get_comment_count(previewed__exact=True)

    def __str__(self):
        return self.title
    def __repr__(self):
        return '<blog.Post %r>' % self.id

class Comment(meta.Model):
    user = meta.ForeignKey(auth.User, blank=True, null=True)
    name = meta.CharField(maxlength=20)
    email = meta.EmailField(blank=True, null=True)
    url = meta.URLField(blank=True, null=True)
    
    post = meta.ForeignKey(Post)
    posted = meta.DateTimeField(auto_now_add=True)
    previewed = meta.BooleanField()
    ip_address = meta.IPAddressField()

    content = meta.TextField()

    class META:
        get_latest_by = 'posted'
        admin = meta.Admin(
            list_display = ['name', 'post', 'posted', 'previewed'],
            list_filter = ['posted', 'previewed'],
        )

    def get_absolute_url(self):
        return self.get_post().get_absolute_url() + '#comment-%d' % self.id

    def __repr__(self):
        return 'Comment %r on %r' % (self.id, self.get_post())
