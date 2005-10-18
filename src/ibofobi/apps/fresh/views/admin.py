from django.core import template_loader
from django.utils.httpwrappers import HttpResponse
from django.core.extensions import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from django.models.fresh import pageviews

import datetime
import re

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
    return render_to_response('fresh/index', {})
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

    return render_to_response('fresh/referrers', {
            'referrers': referrers, 'oldest': oldest, })
referrers = staff_member_required(referrers)

def page_views(request):
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

    return render_to_response('fresh/page-views',
            { 'hits': hits, 'oldest': oldest, })
page_views = staff_member_required(page_views)

def live_page_views(request):
    hits = pageviews.get_list(order_by=['-served'], limit=10)
    return render_to_response('fresh/live-page-views', { 'hits': hits })
live_page_views = staff_member_required(live_page_views)
