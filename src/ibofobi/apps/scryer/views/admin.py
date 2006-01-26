# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import template_loader
from django.core import extensions
from django.core.exceptions import Http404
from django.utils.httpwrappers import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.db import db

from django.models.scryer import pageviews

import datetime
import re

def render_to_response(template, request, kwargs):
    ctx = extensions.DjangoContext(request)
    return extensions.render_to_response(template, kwargs, ctx)

def index(request):
    return render_to_response('scryer/index', request, {})
index = staff_member_required(index)

def referrers(request):
    if request.GET.has_key('max-age'):
        max_age = int(request.GET['max-age'])
        oldest_dt = datetime.datetime.now() - datetime.timedelta(days=max_age)
        oldest = "now() - interval '%d day'" % max_age
    else:
        oldest_dt = None
        oldest = "'-infinity'"

    c = db.cursor()
    # Pity the database server . . .
    c.execute('SELECT r.id, r.name, r.href, COUNT(p) '
              'FROM scryer_pageviews p, scryer_aggregatedreferrers r '
              'WHERE p.referrer ~ r.regex AND NOT r.ignore '
              "AND p.served > %s "
              'GROUP BY r.id, r.name, r.href '
              'UNION '
              'SELECT 0, referrer, referrer, COUNT(*) '
              'FROM scryer_pageviews '
              'WHERE NOT EXISTS (SELECT * FROM scryer_aggregatedreferrers WHERE referrer ~ regex) '
              "AND referrer <> '' "
              "AND served > %s "
              'GROUP BY referrer '
              'ORDER BY 4 DESC' % (oldest, oldest))
    referrers = [ { 'url': r[2],
                    'text': r[1],
                    'count': r[3], }
                  for r in c.fetchall() ]
    c.close()

    return render_to_response('scryer/referrers', request, {
            'referrers': referrers,
            'oldest': oldest_dt, })
referrers = staff_member_required(referrers)

def view_session(request, session_key):
    session = pageviews.get_session(session_key)
    if not session:
        raise Http404()
    return render_to_response('scryer/view_session', request, session)
view_session = staff_member_required(view_session)

def searches(request):
    if request.GET.has_key('max-age'):
        max_age = int(request.GET['max-age'])
        oldest_dt = datetime.datetime.now() - datetime.timedelta(days=max_age)
        oldest = "now() - interval '%d day'" % max_age
    else:
        oldest_dt = None
        oldest = "'-infinity'"

    c = db.cursor()
    # Pity the database server . . .
    c.execute('SELECT s.id, s.name, s.href '
              'FROM scryer_pageviews p, scryer_searchengines s '
              'WHERE p.referrer ~ r.regex AND NOT r.ignore '
              "AND p.served > %s "
              'GROUP BY r.id, r.name, r.href '
              'UNION '
              'SELECT 0, referrer, referrer, COUNT(*) '
              'FROM scryer_pageviews '
              'WHERE NOT EXISTS (SELECT * FROM scryer_aggregatedreferrers WHERE referrer ~ regex) '
              "AND referrer <> '' "
              "AND served > %s "
              'GROUP BY referrer '
              'ORDER BY 4 DESC' % (oldest, oldest))
    referrers = [ { 'url': r[2],
                    'text': r[1],
                    'count': r[3], }
                  for r in c.fetchall() ]
    c.close()

    return render_to_response('scryer/referrers', request, {
            'referrers': referrers,
            'oldest': oldest_dt, })
referrers = staff_member_required(referrers)

def top_pages(request):
    if request.GET.has_key('max-age'):
        max_age = int(request.GET['max-age'])
        max_age = datetime.timedelta(days=max_age)
        oldest = datetime.datetime.now() - max_age
    else:
        oldest = None
    
    hits = pageviews.get_values(distinct=True, fields=['url'],
                                served__gt=oldest) 

    for hit in hits:
        hit['count'] = pageviews.get_count(url__exact=hit['url'],
                                           served__gt=oldest)

    hits.sort(lambda a, b: cmp(b['count'], a['count']))

    return render_to_response('scryer/top_pages', request,
            { 'hits': hits, 'oldest': oldest, })
top_pages = staff_member_required(top_pages)

def page_views(request):
    hits = pageviews.get_list(order_by=['-served'], limit=10)
    return render_to_response('scryer/page_views', request, { 'hits': hits })
page_views = staff_member_required(page_views)

def sessions(request):
    c = db.cursor()
    c.execute('SELECT session_key FROM scryer_pageviews '
              'GROUP BY session_key ORDER BY MAX(served) DESC '
              'LIMIT 10')
    session_keys = c.fetchall()
    sessions = [ pageviews.get_session(sk) for sk, in session_keys ]
    return render_to_response('scryer/sessions', request, locals())
sessions = staff_member_required(sessions)
