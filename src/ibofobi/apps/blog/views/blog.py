from django.core import template
from django.core import template_loader
from django.conf.settings import TEMPLATE_DIRS
from django.conf.settings import ADMIN_URL
from django.core.extensions import DjangoContext as Context
from django.models.blog import posts
from django.models.blog import categories
from django.models.blog import comments
from django.utils.httpwrappers import HttpResponse
from django.utils.httpwrappers import HttpResponseRedirect
from django.core.exceptions import Http404
from django.core.db import db
from django.core.defaultfilters import slugify
from django.conf import settings

from ibofobi.apps.blog.templatetags import safe_markdown

import os
import datetime

xhtml_content_type = 'application/xhtml+xml; charset=utf-8'
atom_content_type = 'application/xml; charset=utf-8'

def __load_atom_template():
    for td in TEMPLATE_DIRS:
        path = os.path.join(td, 'blog/atom.xml')
        if os.path.exists(path):
            t = template.Template(open(path).read())
    return t

def latest(request, format=None):
    c = Context(request, {
        'posts': posts.get_list(listed__exact=True, limit=5, order_by=['-posted']),
    })
    if format == 'atom':
        t = __load_atom_template()
        ct = atom_content_type
    else:
        t = template_loader.get_template('blog/latest')
        ct = xhtml_content_type
    return HttpResponse(t.render(c), ct)

def tag_posts(request, slug, format=None, limit=None):
    try:
        category = categories.get_object(slug__exact=slug)
    except categories.CategoryDoesNotExist:
        raise Http404

    c = Context(request, {
        'tag': category,
        'posts': category.get_listed_post_list(order_by=['-posted'], limit=limit),
    })
    if format == 'atom':
        t = __load_atom_template()
        ct = atom_content_type
    else:
        t = template_loader.get_template('blog/tag-posts')
        ct = xhtml_content_type
    return HttpResponse(t.render(c), ct)

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
        'admin_url': ADMIN_URL,
    })
    t = template_loader.get_template('blog/post')
    return HttpResponse(t.render(c), xhtml_content_type)

def tag_index(request):
    c = Context(request, {
        'tags': categories.get_list(order_by=['name']),
    })
    t = template_loader.get_template('blog/tags')
    return HttpResponse(t.render(c), xhtml_content_type)

def archive_index(request):
    c = db.cursor()
    # FIXME -- use db abstraction layer for DATE_TRUNC
    c.execute("""SELECT DISTINCT DATE_TRUNC('month', posted) AS posted
                 FROM blog_posts ORDER BY posted DESC""")
    rows = c.fetchall()
    c.close()

    c = Context(request, {
        'months': [ { 'date': date,
                      'posts': len(posts.get_list(listed__exact=True,
                                                  posted__year=date.year,
                                                  posted__month=date.month)), }
                    for date, in rows ],
    })
    t = template_loader.get_template('blog/archive-index')
    return HttpResponse(t.render(c), xhtml_content_type)

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
                      'posts': len(posts.get_list(listed__exact=True,
                                                  posted__year=date.year,
                                                  posted__month=date.month)), }
                    for date, in rows ],
    })
    t = template_loader.get_template('blog/archive-year')
    return HttpResponse(t.render(c), xhtml_content_type)

def archive_month(request, year, month):
    c = Context(request, {
        'date': datetime.date(int(year), int(month), 1),
        'posts': posts.get_list(listed__exact=True,
                                posted__year=int(year),
                                posted__month=int(month),
                                order_by=['posted']),
    })
    t = template_loader.get_template('blog/archive-month')
    return HttpResponse(t.render(c), xhtml_content_type)

def archive_day(request, year, month, day):
    c = Context(request, {
        'date': datetime.date(int(year), int(month), int(day)),
        'posts': posts.get_list(listed__exact=True,
                                posted__year=int(year),
                                posted__month=int(month),
                                posted__day=int(day),
                                order_by=['posted']),
    })
    t = template_loader.get_template('blog/archive-day')
    return HttpResponse(t.render(c), xhtml_content_type)

def feeds_index(request):
    c = Context(request, {
        'tags': categories.get_list(order_by=['-name']),
    })
    t = template_loader.get_template('blog/feeds_index')
    return HttpResponse(t.render(c), xhtml_content_type)

def preview_comment(request, year, month, day, slug):
    try:
        p = posts.get_object(posted__year=int(year),
                             posted__month=int(month),
                             posted__day=int(day),
                             slug__exact=slug)
    except posts.PostDoesNotExist:
        raise Http404()

    if request.POST.has_key('comment'):
        comment = comments.get_object(pk=int(request.POST['comment']))

        if not p.id == comment.post_id:
            raise Http404()
        if comment.previewed:
            raise Http404()
    else:
        comment = comments.Comment(post=p, name=request.POST['name'])

    comment.user = request.user
    comment.previewed = False

    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        comment.ip_address = request.META['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    elif request.META.has_key('REMOTE_ADDR'):
        comment.ip_address = request.META.get('REMOTE_ADDR')
    else:
        comment.ip_address = '0.0.0.0'
    
    comment.email = request.POST['email']
    comment.url = request.POST['url']
    comment.content = safe_markdown.render(request.POST['content'])

    comment.save()

    c = Context(request, {
        'post': p,
        'markdown_content': request.POST['content'],
        'comment': comment,
    })
    t = template_loader.get_template('blog/preview-comment')
    ct = xhtml_content_type
    return HttpResponse(t.render(c), ct)

def post_comment(request, year, month, day, slug):
    try:
        p = posts.get_object(posted__year=int(year),
                             posted__month=int(month),
                             posted__day=int(day),
                             slug__exact=slug)
    except posts.PostDoesNotExist:
        raise Http404()

    try:
        c = comments.get_object(pk=int(request.POST.get('comment', '-1')))
    except comments.CommentDoesNotExist:
        raise Http404()

    if not p.id == c.post_id:
        raise Http404()
    if c.previewed:
        raise Http404()

    c.previewed = True
    c.save()

    return HttpResponseRedirect(c.get_absolute_url())
