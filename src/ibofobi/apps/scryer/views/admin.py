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

meta_referrers = (
    (None, None,
        r'^http://([a-z]+\.)?ibofobi\.dk/'),
    (None, None,
        r'^(?!http://)'),
    ('Google', 'http://www.google.com/',
        r'^http://www\.google\.([a-z]+|[a-z]+\.[a-z]+)/search\?'),
    ('Bloglines', 'http://www.bloglines.com/',
        r'^http://(www\.)?bloglines\.com/'),
)

def index(request):
    return render_to_response('scryer/index', request, {})
index = staff_member_required(index)

def referrers(request):
    if request.GET.has_key('max-age'):
        max_age = int(request.GET['max-age'])
        max_age = datetime.timedelta(days=max_age)
        oldest = datetime.datetime.now() - max_age
    else:
        oldest = None
    
    referrers = pageviews.get_values(distinct=True, fields=['referrer'],
                                     referrer__ne='',
                                     served__gt=oldest)

    for ref in referrers:
        ref['text'] = ref['referrer']
        ref['url'] = ref['referrer']
        ref['count'] = pageviews.get_count(referrer__exact=ref['url'],
                                           served__gt=oldest)

    for text, url, regex in meta_referrers:
        regex = re.compile(regex)
        these = [ r for r in referrers if regex.search(r['url']) ]
        referrers = [ r for r in referrers if not regex.search(r['url']) ]
        if these and url is not None:
            referrers.append({'url': url, 'text': text,
                              'count': sum([ r['count'] for r in these ]) })

    referrers.sort(lambda a, b: cmp(b['count'], a['count']))

    return render_to_response('scryer/referrers', request, {
            'referrers': referrers, 'oldest': oldest, })
referrers = staff_member_required(referrers)

def view_session(request, session_key):
    session = pageviews.get_session(session_key)
    if not session:
        raise Http404()
    return render_to_response('scryer/view_session', request, session)
view_session = staff_member_required(view_session)

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
