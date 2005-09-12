from django.core import meta
from django.conf.settings import MEDIA_ROOT
from django.models import auth

class Category(meta.Model):
    name = meta.CharField('name', maxlength=30)
    slug = meta.SlugField('identifier', prepopulate_from=['name'])

    class META:
        module_name = 'categories'
        verbose_name_plural = 'categories'

        admin = meta.Admin(
            fields = (
                (None, {'fields': ('name', 'slug')}),
            ),
        )

    def get_absolute_url(self):
        return '/blog/tags/%s/' % self.slug

    def get_latest_post(self):
        p = self.get_post_list(order_by=['-posted'], limit=1)
        if p:
            return p[0]

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
    posted = meta.DateTimeField('posted',
                                help_text='Date and time when post went public')
    title = meta.CharField(maxlength=100)
    content = meta.TextField()
    categories = meta.ManyToManyField(Category, blank=True)

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('title', 'slug', 'categories', 'content', 'posted')}),
            ),
        )

    def _pre_save(self):
        if not self.tag:
            self.tag = 'tag:ibofobi.dk,%d-%02d-%02d:%s' \
                       % (self.posted.year, self.posted.month,
                          self.posted.day, self.get_absolute_url())

    def get_absolute_url(self):
        return '/blog/archive/%d/%02d/%02d/%s/' % (self.posted.year, self.posted.month, self.posted.day, self.slug)

    def get_next_post(self):
        return get_object(posted__gt=self.posted,
                          order_by=['posted'],
                          limit=1)

    def get_previous_post(self):
        return get_object(posted__lt=self.posted,
                          order_by=['-posted'],
                          limit=1)

    def get_previewed_comment_list(self):
        return self.get_comment_list(previewed__exact=True)
    def get_previewed_comment_count(self):
        return self.get_comment_count(previewed__exact=True)

    def __repr__(self):
        return self.title

class Draft(meta.Model):
    title = meta.CharField(maxlength=50)
    content = meta.TextField()
    categories = meta.ManyToManyField(Category)

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('title', 'categories', 'content'),
                        'js': [MEDIA_ROOT + '/blog-draft-admin.js']}),
            ),
        )

    def get_absolute_url(self):
        return '/blog/admin/drafts/view/%d/' % self.id

    def __repr__(self):
        return self.title

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
        )

    def get_absolute_url(self):
        return self.get_post().get_absolute_url() + '#comment-%d' % self.id
