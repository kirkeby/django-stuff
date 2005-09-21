from django.models.fresh import pageviews
from django.utils.httpwrappers import HttpResponse

def fresh(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    elif request.META.has_key('REMOTE_ADDR'):
        ip = request.META['REMOTE_ADDR']
    else:
        ip = '0.0.0.0'

    url = '/' + request.GET['url'].split('/', 3)[-1]

    pv = pageviews.PageView(url=url)
    pv.referrer = request.GET['ref'] or None
    pv.user_agent = request.META.get('HTTP_USER_AGENT', None)
    pv.ip_address = ip
    pv.save()

    r = HttpResponse('/* Intentionally left empty */', 'text/css')
    r['Cache-Control'] = 'max-age=0'
    r['Expires'] = 'Fri, 16 Sep 2005 10:01:26 GMT'
    return r