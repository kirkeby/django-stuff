# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import meta
from django.models import auth
from django.models import core

import datetime
session_lifetime = datetime.timedelta(seconds=30 * 60)

class PageView(meta.Model):
    ip_address = meta.IPAddressField()
    served = meta.DateTimeField(auto_now_add=True)
    site = meta.ForeignKey(core.Site)
    url = meta.CharField(maxlength=512)
    session_key = meta.CharField(maxlength=40)
    referrer = meta.CharField(maxlength=512, blank=True, null=True)
    user_agent = meta.CharField(maxlength=512, blank=True, null=True)

    def _module_get_session(session_key):
        from django.utils.timesince import timesince

        hits = get_list(session_key__exact=session_key, order_by=['-served'])
        if not hits:
            return None
        
        started = hits[-1].served
        ended = hits[0].served
        lasted = timesince(started, ended)
        client = hits[0].ip_address
        browser = hits[0].user_agent

        return dict(locals()) # Yeehaw!
    
    def _module_get_new_session_key():
        "Returns session key that isn't being used."
        from django.conf.settings import SECRET_KEY
        import md5, random, sys
        # The random module is seeded when this Apache child is created.
        # Use SECRET_KEY as added salt.
        while 1:
            session_key = md5.new(str(random.randint(0, sys.maxint - 1)) + SECRET_KEY).hexdigest()
            try:
                get_object(session_key__exact=session_key)
            except PageViewDoesNotExist:
                break
        return session_key

    class META:
        module_constants = {
            'session_lifetime': session_lifetime,
        }

        admin = meta.Admin(
            list_display = ['url', 'ip_address', 'served'],
            list_filter = ['site', 'served'],
        )

    def __repr__(self):
        return self.ip_address

class AggregatedReferrer(meta.Model):
    """I represent an aggregation of several referrers into one meta-referrer,
    for example I can aggregate all referrals from Google into one, to make your
    referrer lists easier to read."""

    name = meta.CharField(maxlength=30)
    href = meta.CharField(maxlength=100)
    regex = meta.CharField(maxlength=100)
    ignore = meta.BooleanField(default=False)

    class META:
        admin = meta.Admin(
            list_display = ['name', 'regex', 'ignore'],
            list_filter = ['ignore'],
        )

    def __str__(self):
        return self.name

class SearchEngine(meta.Model):
    """I represent a search-engine."""

    name = meta.CharField(maxlength=30)
    href = meta.CharField(maxlength=100)
    regex = meta.CharField(maxlength=100)

    class META:
        admin = meta.Admin(
            list_display = ['name', 'regex', 'ignore'],
            list_filter = ['ignore'],
        )

    def __str__(self):
        return self.name
