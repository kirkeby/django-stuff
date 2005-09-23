from django.core import template_loader
from django.utils.httpwrappers import HttpResponse
from django.core.extensions import DjangoContext as Context

from django.models.fresh import pageviews

import re

meta_referrers = (
    (None, None,
        r'^http://([a-z]+\.)?ibofobi\.dk/'),
    (None, None,
        r'^(?!http://)'),
    ('Google', 'http://www.google.com/',
        r'^http://www\.google\.[a-z]+/'),
    ('Bloglines', 'http://www.bloglines.com/',
        r'^http://(www\.)?bloglines\.com/'),
)

def referrers(request):
    referrers = pageviews.get_values(distinct=True, fields=['referrer'],
                                     referrer__ne='')

    for ref in referrers:
        ref['text'] = ref['referrer']
        ref['url'] = ref['referrer']
        ref['count'] = pageviews.get_count(referrer__exact=ref['url'])

    for text, url, regex in meta_referrers:
        regex = re.compile(regex)
        these = [ r for r in referrers if regex.search(r['url']) ]
        referrers = [ r for r in referrers if not regex.search(r['url']) ]
        if these and url is not None:
            referrers.append({'url': url, 'text': text,
                              'count': sum([ r['count'] for r in these ]) })

    referrers.sort(key=lambda r: r['count'])
    referrers.reverse()

    t = template_loader.get_template('fresh/referrers')
    c = Context(request, { 'referrers': referrers, })
    return HttpResponse(t.render(c))
