from django.core import template
from django.core import template_loader
from django.conf.settings import TEMPLATE_DIRS
from django.core.extensions import DjangoContext as Context
from django.models.blog import posts
from django.models.blog import categories
from django.utils.httpwrappers import HttpResponse
from django.core.exceptions import Http404
from django.core.db import db

import os
import datetime

content_type = 'application/xhtml+xml; charset=utf-8'

def latest(request):
    c = Context(request, {
        'posts': posts.get_list(limit=5, order_by=['-posted']),
    })
    t = template_loader.get_template('blog/latest')
    return HttpResponse(t.render(c), content_type)

def atom(request):
    c = Context(request, {
        'posts': posts.get_list(limit=5, order_by=['-posted']),
    })
    for td in TEMPLATE_DIRS:
        path = os.path.join(td, 'blog/atom.xml')
        if os.path.exists(path):
            t = template.Template(open(path).read())
    return HttpResponse(t.render(c), 'application/xml; charset=utf-8')

def post(request, year, month, day, slug):
    try:
        p = posts.get_object(posted__year=int(year),
                             posted__month=int(month),
                             posted__day=int(day),
                             slug__exact=slug)
    except posts.PostDoesNotExist:
        raise Http404()

    c = Context(request, {
        'post': p,
    })
    t = template_loader.get_template('blog/post')
    return HttpResponse(t.render(c), content_type)

def tag_index(request):
    c = Context(request, {
        'tags': categories.get_list(),
    })
    t = template_loader.get_template('blog/tags')
    return HttpResponse(t.render(c), content_type)

def tag_posts(request, slug):
    try:
        category = categories.get_object(slug__exact=slug)
    except categories.CategoryDoesNotExist:
        raise Http404

    c = Context(request, {
        'tag': category,
        'posts': category.get_post_list(order_by=['-posted']),
    })
    t = template_loader.get_template('blog/tag-posts')
    return HttpResponse(t.render(c), content_type)

def archive_index(request):
    c = db.cursor()
    # FIXME -- use db abstraction layer for DATE_TRUNC
    c.execute("""SELECT DISTINCT DATE_TRUNC('month', posted) AS posted
                 FROM blog_posts ORDER BY posted DESC""")
    rows = c.fetchall()
    c.close()

    c = Context(request, {
        'months': [ { 'date': date,
                      'posts': len(posts.get_list(posted__year=date.year,
                                                  posted__month=date.month)), }
                    for date, in rows ],
    })
    t = template_loader.get_template('blog/archive-index')
    return HttpResponse(t.render(c), content_type)

def archive_year(request, year):
    c = db.cursor()
    # FIXME -- use db abstraction layer for DATE_TRUNC
    c.execute("""SELECT DISTINCT DATE_TRUNC('month', posted) AS posted
                 FROM blog_posts WHERE DATE_TRUNC('year', posted) = '%s-01-01'
                 ORDER BY posted""" % year)
    rows = c.fetchall()
    c.close()

    c = Context(request, {
        'year': year,
        'months': [ { 'date': date,
                      'posts': len(posts.get_list(posted__year=date.year,
                                                  posted__month=date.month)), }
                    for date, in rows ],
    })
    t = template_loader.get_template('blog/archive-year')
    return HttpResponse(t.render(c), content_type)

def archive_month(request, year, month):
    c = Context(request, {
        'date': datetime.date(int(year), int(month), 1),
        'posts': posts.get_list(posted__year=int(year),
                                posted__month=int(month),
                                order_by=['posted']),
    })
    t = template_loader.get_template('blog/archive-month')
    return HttpResponse(t.render(c), content_type)

def archive_day(request, year, month, day):
    c = Context(request, {
        'date': datetime.date(int(year), int(month), int(day)),
        'posts': posts.get_list(posted__year=int(year),
                                posted__month=int(month),
                                posted__day=int(day),
                                order_by=['posted']),
    })
    t = template_loader.get_template('blog/archive-day')
    return HttpResponse(t.render(c), content_type)
