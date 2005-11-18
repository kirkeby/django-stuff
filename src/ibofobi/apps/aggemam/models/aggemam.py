# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import meta
from django.models import auth

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
        get_latest_by = 'happened'

    def __repr__(self):
        return self.short

class Feed(meta.Model):
    update = meta.BooleanField()
    next_update = meta.DateTimeField(auto_now_add=True)
    update_interval = meta.IntegerField(default=300) # minutes

    url = meta.URLField(unique=True)
    link = meta.URLField(blank=True, null=True)
    title = meta.CharField(maxlength=100, blank=True, null=True)

    class META:
        admin = meta.Admin(
            list_display = ['url', 'title', 'update'],
            list_filter = ['update', 'next_update'],
        )

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return self.url

RESULT_CHOICES = (
    ('ok', 'Ok'),
    ('no', 'No changes'),
    ('rm', 'Gone'),
    ('er', 'Error'),
    ('ot', 'Other'),
)
class FeedUpdate(meta.Model):
    feed = meta.ForeignKey(Feed)
    fetched = meta.DateTimeField(auto_now_add=True)
    result = meta.CharField(maxlength=2, choices=RESULT_CHOICES)
    processed = meta.BooleanField()

    http_status_code = meta.IntegerField(blank=True, null=True)
    http_last_mod = meta.CharField(maxlength=100, blank=True, null=True)
    http_etag = meta.CharField(maxlength=100, blank=True, null=True)
    http_headers = meta.TextField(blank=True, null=True)
    http_content = meta.TextField(blank=True, null=True)

    class META:
        get_latest_by = 'fetched'

        admin = meta.Admin(
            list_display = ['fetched', 'feed', 'result', 'processed'],
            list_filter = ['processed', 'fetched', 'result'],
        )

    def __repr__(self):
        return 'Feed update %r' % self.id

class Post(meta.Model):
    feed = meta.ForeignKey(Feed)
    guid = meta.CharField(maxlength=300)
    fetched = meta.DateTimeField(auto_now_add=True)

    posted = meta.DateTimeField()
    title = meta.CharField(maxlength=300, blank=True, null=True)
    author = meta.CharField(maxlength=100, blank=True, null=True)
    category = meta.CharField(maxlength=100, blank=True, null=True)
    summary = meta.TextField(blank=True, null=True)
    content = meta.TextField(blank=True, null=True)

    def get_preferred_link(self):
        """Get the most preferred alternate link."""
        if not hasattr(self, 'preferred_link'):
            type_scores = {
                'application/xhtml+xml': -10,
                'text/html': -5,
                'text/plain': -1,
            }
            def cmp_types(a, b):
                return cmp(type_scores.get(a.type, 0), type_scores.get(b.type, 0))
            
            links = self.get_link_list()
            links.sort(cmp_types)
            if links:
                self.preferred_link = links[0]
            else:
                self.preferred_link = None

        return self.preferred_link

    class META:
        unique_together = (('feed', 'guid'),)
        get_latest_by = 'posted'
        ordering = ['-posted', '-fetched']

        admin = meta.Admin(
            list_filter = ['posted', 'fetched'],
            list_display = ['__repr__', 'feed', 'posted', 'fetched'],
        )

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return self.guid

    def _module_get_unread(user):
        from django.core.db import db
        c = db.cursor()
        c.execute('''
                SELECT aggemam_posts.id
                FROM aggemam_posts, aggemam_subscriptions
                WHERE aggemam_subscriptions.user_id = %d
                AND aggemam_subscriptions.feed_id = aggemam_posts.feed_id
                AND NOT EXISTS (SELECT * FROM aggemam_userpostmarks
                                WHERE aggemam_userpostmarks.user_id = aggemam_subscriptions.user_id
                                AND aggemam_userpostmarks.post_id = aggemam_posts.id
                                AND aggemam_userpostmarks.mark = 'rd')
                ORDER BY aggemam_posts.posted ASC
                  ''' % user.id)
        return [ get_object(pk=post_id) for post_id, in c.fetchall() ]

class Link(meta.Model):
    post = meta.ForeignKey(Post)
    href = meta.URLField()
    type = meta.CharField(maxlength=80, blank=True, null=True)
    title = meta.CharField(maxlength=80, blank=True, null=True)

    class META:
        admin = meta.Admin()

    def __repr__(self):
        return self.title or self.href

class Subscription(meta.Model):
    user = meta.ForeignKey(auth.User)
    feed = meta.ForeignKey(Feed)

    def __repr__(self):
        return 'User %r; feed %r' % (self.get_user(), self.get_feed())

MARK_CHOICES = (
    ('rd', 'Read'),
)
class UserPostMark(meta.Model):
    user = meta.ForeignKey(auth.User)
    post = meta.ForeignKey(Post)
    mark = meta.CharField(maxlength=2, choices=MARK_CHOICES)
