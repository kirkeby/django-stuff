from django.core import template
from django.core import template_loader
from django.conf.settings import TEMPLATE_DIRS
from django.conf.settings import ADMIN_URL
from django.core.extensions import DjangoContext as Context
from django.models.blog import posts
from django.models.blog import categories
from django.models.blog import drafts
from django.utils.httpwrappers import HttpResponse
from django.utils.httpwrappers import HttpResponseRedirect
from django.core.exceptions import Http404
from django.core.db import db
from django.core.defaultfilters import slugify
from django.conf import settings

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
        'posts': posts.get_list(limit=5, order_by=['-posted']),
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
        'posts': category.get_post_list(order_by=['-posted'], limit=limit),
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
                      'posts': len(posts.get_list(posted__year=date.year,
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
                      'posts': len(posts.get_list(posted__year=date.year,
                                                  posted__month=date.month)), }
                    for date, in rows ],
    })
    t = template_loader.get_template('blog/archive-year')
    return HttpResponse(t.render(c), xhtml_content_type)

def archive_month(request, year, month):
    c = Context(request, {
        'date': datetime.date(int(year), int(month), 1),
        'posts': posts.get_list(posted__year=int(year),
                                posted__month=int(month),
                                order_by=['posted']),
    })
    t = template_loader.get_template('blog/archive-month')
    return HttpResponse(t.render(c), xhtml_content_type)

def archive_day(request, year, month, day):
    c = Context(request, {
        'date': datetime.date(int(year), int(month), int(day)),
        'posts': posts.get_list(posted__year=int(year),
                                posted__month=int(month),
                                posted__day=int(day),
                                order_by=['posted']),
    })
    t = template_loader.get_template('blog/archive-day')
    return HttpResponse(t.render(c), xhtml_content_type)

def preview_draft(request, object_id):
    try:
        draft = drafts.get_object(pk=int(object_id))
    except drafts.DraftDoesNotExist:
        raise Http404

    draft.posted = datetime.datetime.now

    c = Context(request, {
        'post': draft,
        'is_draft': True,
    })
    t = template_loader.get_template('blog/post')
    return HttpResponse(t.render(c), xhtml_content_type)
preview_draft.admin_required = True

def publish_draft(request, object_id):
    try:
        draft = drafts.get_object(pk=int(object_id))
    except drafts.DraftDoesNotExist:
        raise Http404

    post = posts.Post(title=draft.title, content=draft.content)
    # post.tag is set by Post._pre_save
    post.slug = slugify(draft.title, None)
    post.posted = datetime.datetime.now()
    post.save()
    post.set_categories([ c.id for c in draft.get_category_list()])
    post.save()

    draft.delete()

    return HttpResponseRedirect('%s/blog/posts/%d/' % (settings.ADMIN_URL, post.id))
preview_draft.admin_required = True
