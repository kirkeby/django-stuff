from django.core import template_loader
from django.core.extensions import DjangoContext as Context
from django.models.accounting import accounts
from django.utils.httpwrappers import HttpResponse
from django.core.exceptions import Http404

def index(request):
    t = template_loader.get_template('accounting/index')
    c = Context(request, {
        'account_list': accounts.get_list(),
    })
    return HttpResponse(t.render(c))

def view(request, account_slug):
    try:
        account = accounts.get_object(path__exact=account_slug)
    except accounts.AccountDoesNotExist:
        raise Http404
    t = template_loader.get_template('accounting/view')
    c = Context(request, {
        'account': account,
    })
    return HttpResponse(t.render(c))
