# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.models.scryer import pageviews
from django.models.core import sites
from django.utils.httpwrappers import HttpResponse

from django.conf import settings

import datetime

def pageview(request):
    if getattr(settings, 'SCRYER_SKIP', False):
        pass

    else:
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        elif request.META.has_key('REMOTE_ADDR'):
            ip = request.META['REMOTE_ADDR']
        else:
            ip = '0.0.0.0'

        if request.GET.has_key('site'):
            site = sites.get_object(pk=int(request.GET['site']))
        else:
            site = sites.get_object(pk=settings.SITE_ID)

        session_key = None
        # If there is a cookie with a session use that use that
        # FIXME -- should it expire before the Django-session cookie?!
        try:
            session_key = request.session['scryer-session']
        except KeyError:
            pass

        # Look for a recent request with this IP-address, if this exists,
        # reuse that session; this is a band-aid when the browser refuses
        # our cookie.
        if session_key is None:
            oldest = datetime.datetime.now() - pageviews.session_lifetime
            hits = pageviews.get_list(ip_address__exact=ip,
                                      served__gt=oldest,
                                      order_by=['-served'],
                                      limit=1)
            if hits:
                session_key = hits[0].session_key

        # Finally, create a new session
        if session_key is None:
            session_key = pageviews.get_new_session_key()

        request.session['scryer-session'] = session_key
        
        url = '/' + request.GET['url'].split('/', 3)[-1]

        pv = pageviews.PageView(site=site, url=url)
        pv.referrer = request.GET.get('ref', '') or None
        pv.user_agent = request.META.get('HTTP_USER_AGENT', None)
        pv.session_key = session_key
        pv.ip_address = ip
        pv.save()

    r = HttpResponse('/* Intentionally left empty */', 'text/css')
    r['Cache-Control'] = 'max-age=0'
    r['Expires'] = 'Fri, 16 Sep 2005 10:01:26 GMT'
    return r
