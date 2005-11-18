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
