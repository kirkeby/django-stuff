# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import extensions
from django.core.exceptions import Http404
from django.utils.httpwrappers import HttpResponseRedirect
from django.core import formfields

from django.contrib.admin.views.decorators import staff_member_required

from django.models.blog import posts
from django.models.blog import comments

import datetime

def page(function, template_name):
    def g(request, *args, **kwargs):
        result = function(request, *args, **kwargs)
        if isinstance(result, dict):
            ctx = extensions.DjangoContext(request)
            return extensions.render_to_response(template_name, result, ctx)
        else:
            return result
    return staff_member_required(g)

def draft_index(request):
    return {
        'drafts': posts.get_list(listed__exact=False,
                                 order_by=['-posted']),
    }
draft_index = page(draft_index, 'blog/drafts_index')

def draft_edit(request, draft_id):
    try:
        manipulator = posts.ChangeManipulator(draft_id)
    except posts.PostDoesNotExist:
        raise Http404

    draft = manipulator.original_object

    if request.POST:
        do_publish = request.POST['action'] == 'publish'

        data = request.POST.copy()
        if do_publish:
            data['listed'] = 'on'
        now = datetime.datetime.now()
        data['posted_date'] = now.strftime('%Y-%m-%d')
        data['posted_time'] = now.strftime('%H:%M:%S')
        data.setlist('categories', [ d.id for d in draft.get_category_list() ])

        errors = manipulator.get_validation_errors(data)

        if not errors:
            draft.posted = datetime.datetime.now()

            manipulator.do_html2python(data)
            manipulator.save(data)
            draft = posts.get_object(pk=draft.id)

            if do_publish:
                return HttpResponseRedirect("../../../posts/%d/" % draft.id)

    else:
        errors = {}
        data = draft.__dict__

    form = formfields.FormWrapper(manipulator, data, errors)
    return locals()
draft_edit = page(draft_edit, 'blog/draft_preview')

def comments_index(request):
    return {
        'comments': comments.get_list(order_by=['-posted']),
    }
comments_index = page(comments_index, 'blog/admin/comments_index')

def delete_comments(request):
    for id in request.POST.getlist('comments'):
        comment = comments.get_object(pk=int(id))
        comment.delete()
    return HttpResponseRedirect('..')
delete_comments = staff_member_required(delete_comments)
