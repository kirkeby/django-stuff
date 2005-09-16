from django.models.fresh import pageviews
from django.utils.httpwrappers import HttpResponse

def fresh(request):
    pv = pageviews.PageView(user=request.user)
    # pv.session = 
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        pv.ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
    elif request.META.has_key('REMOTE_ADDR'):
        pv.ip_address = request.META.get('REMOTE_ADDR')
    else:
        pv.ip_address = '0.0.0.0'
    pv.url = request.GET['url']
    pv.referrer = request.GET['ref'] or None
    pv.user_agent = request.META.get('HTTP_USER_AGENT', None)
    pv.save()

    r = HttpResponse('/* Intentionally left empty */', 'text/css')
    r['Cache-Control'] = 'max-age=0'
    r['Expires'] = 'Fri, 16 Sep 2005 10:01:26 GMT'
    return r
