# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import template_loader
from django.utils.httpwrappers import HttpResponse
from django.core.extensions import DjangoContext
from django.core.extensions import render_to_response
from django.core.validators import isAlphaNumeric
from django.conf import settings

from django.contrib.admin.views.decorators import staff_member_required

from django.models.aggemam import subscriptions
from django.models.aggemam import feeds
from django.models.aggemam import posts

from ibofobi.apps.aggemam.utils import feedfinder

class Context(DjangoContext):
    def __init__(self, request, **kwargs):
        DjangoContext.__init__(self, request, kwargs)
        self['settings'] = settings

def index(request):
    t = template_loader.get_template('aggemam/index')
    c = Context(request)
    return HttpResponse(t.render(c))

format_content_types = {
    'json': 'application/x-javascript',
}
def json_enabled_page(f, template_name):
    def g(request, *args):
        format = request.GET.get('format', None)
        isAlphaNumeric(format, None)

        ct = format_content_types.get(format, None)
        if format:
            t = template_loader.get_template(template_name + '.' + format)
        else:
            t = template_loader.get_template(template_name)

        c = f(request, *args)
        return HttpResponse(t.render(c), ct)

    return g

def subscribe(request):
    if request.GET:
        url = request.GET['url']
        fds = feedfinder.getFeeds(url)
        return render_to_response('aggemam/subscribe', {'url': url,
                                            'feeds': fds})

    elif request.POST:
        subs = []
        for url in request.POST.getlist('feeds'):
            try:
                feed = feeds.get_object(url__exact=url)
            except feeds.FeedDoesNotExist:
                feed = feeds.Feed(url=url, update=True)
                feed.save()

            sub = subscriptions.Subscription(user=request.user, feed=feed)
            sub.save()
            subs.append(sub)

        return render_to_response('aggemam/subscribed', {'subscriptions': subs})
subscribe = staff_member_required(subscribe)

def list_subscriptions(request):
    subs = subscriptions.get_list(user__id__exact=request.user.id)
    return Context(request, subscriptions=subs)
    
def list_unread_posts(request):
    return Context(request, posts=posts.get_unread_for_user(request.user))
list_unread_posts = json_enabled_page(list_unread_posts, 'aggemam/list_posts')
