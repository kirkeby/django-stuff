from django.core import meta

SEVERITY_CHOICES = (
    (0, 'Debug'),
    (3, 'Notice'),
    (7, 'Warning'),
    (9, 'Error'),
)
class Message(meta.Model):
    happened = meta.DateTimeField(auto_now_add=True)
    severity = meta.IntegerField(choices=SEVERITY_CHOICES)
    short = meta.CharField(maxlength=100)
    detailed = meta.TextField(blank=True, null=True)

    class META:
        admin = meta.Admin(
            list_display = ['happened', 'severity', 'short'],
            list_filter = ['happened', 'severity'],
        )
        get_latest_by = ['happened']

    def __repr__(self):
        return self.short

class Feed(meta.Model):
    update = meta.BooleanField()

    url = meta.URLField(unique=True)
    link = meta.URLField(blank=True, null=True)
    title = meta.CharField(maxlength=100, blank=True, null=True)

    class META:
        admin = meta.Admin(
            list_display = ['url', 'title', 'update'],
            list_filter = ['update'],
        )

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return self.url

RESULT_CHOICES = (
    ('ok', 'Ok'),
    ('rm', 'Gone'),
    ('er', 'Error'),
    ('ot', 'Other'),
)
class FeedUpdate(meta.Model):
    feed = meta.ForeignKey(Feed)
    fetched = meta.DateTimeField(auto_now_add=True)
    result = meta.CharField(maxlength=2, choices=RESULT_CHOICES)
    processed = meta.BooleanField()

    http_status_code = meta.IntegerField()
    http_last_mod = meta.CharField(maxlength=100, blank=True, null=True)
    http_etag = meta.CharField(maxlength=100, blank=True, null=True)
    http_headers = meta.TextField(blank=True, null=True)
    http_content = meta.TextField(blank=True, null=True)

    class META:
        get_latest_by = ['fetched']

        admin = meta.Admin(
            list_display = ['fetched', 'feed', 'result', 'processed'],
            list_filter = ['processed', 'fetched', 'result'],
        )

    def __repr__(self):
        return repr('Feed update %r' % self.id)

class Post(meta.Model):
    feed = meta.ForeignKey(Feed)
    guid = meta.CharField(maxlength=100)
    fetched = meta.DateTimeField(auto_now_add=True)

    posted = meta.DateTimeField()
    title = meta.CharField(maxlength=100, blank=True, null=True)
    author = meta.CharField(maxlength=100, blank=True, null=True)
    category = meta.CharField(maxlength=100, blank=True, null=True)
    summary = meta.TextField(blank=True, null=True)
    content = meta.TextField(blank=True, null=True)

    class META:
        unique_together = (('feed', 'guid'),)
        get_latest_by = ['fetched']

        admin = meta.Admin(
            list_filter = ['posted'],
            list_display = ['title', 'feed', 'posted'],
        )

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return self.guid

class Link(meta.Model):
    post = meta.ForeignKey(Post)
    href = meta.URLField()
    type = meta.CharField(maxlength=80, blank=True, null=True)
    title = meta.CharField(maxlength=80, blank=True, null=True)

    class META:
        admin = meta.Admin()

    def __repr__(self):
        return self.title or self.href
