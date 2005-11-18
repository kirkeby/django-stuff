# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import template_loader
from django.core.extensions import DjangoContext as Context
from django.models.calendar import events
from django.models.calendar import recurringevents
from django.utils.httpwrappers import HttpResponse
from django.utils.httpwrappers import HttpResponseRedirect
from django.core.exceptions import Http404
from django.core import formfields

import datetime
import time

def index(request):
    return HttpResponseRedirect('%d/%02d/' % time.localtime()[:2])

def month(request, year, month):
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        raise Http404
    
    t = template_loader.get_template('calendar/month')
    c = Context(request, {
        'year': year,
        'month': month,
        'matrix': get_month_matrix(year, month),
    })
    return HttpResponse(t.render(c))

def create(request, year, month, day):
    manipulator = events.AddManipulator()

    # Handle POSTs uphere (unless they contain errors).
    if request.POST:
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)

        if not errors:
            manipulator.do_html2python(new_data)
            event = manipulator.save(new_data)
            return HttpResponseRedirect(event.get_absolute_url())

    else:
        errors, new_data = {}, {}

    # A fresh GET or a POST with errors, falls through here.

    # Fetch start_date and end_date defaults from URL.
    try:
        year = int(year)
        month = int(month)
        day = int(day)
        start_date = end_date = datetime.date(year, month, day)
    except ValueError:
        raise Http404
    new_data['start_date'] = start_date
    new_data['end_date'] = end_date

    # Send back a create form.
    form = formfields.FormWrapper(manipulator, new_data, errors)
    t = template_loader.get_template('calendar/create')
    c = Context(request, { 'form': form, })
    return HttpResponse(t.render(c))

def get_month_matrix(year, month):
    """get_month_matrix(year, month) -> [ [ ... ] ... ]

    Generate a cal(1)-like matrix for the given month."""

    now = datetime.date.today()
    recurring = recurringevents.get_list()

    def end_of_month(when):
        """end_of_month(when) -> when

        Find seconds since the epoch on midnight the first of the
        following month."""
        t = list(time.localtime(when))
        if t[1] == 12:
            t[0] = t[0] + 1
            t[1] = 1
        else:
            t[1] = t[1] + 1
        return time.mktime(t)
        
    def get_day(time_epoch):
        year, month, day, hh, mm, ss, weekday, julian, dst = \
            time.localtime(time_epoch)
        date = datetime.date(year, month, day)
        return {
            'events': events.get_list(start_date__lte=date,
                                      end_date__gte=date),
            'recurringevents': [ e for e in recurring
                                 if recurringevents.is_here(e, date) ],
            'year': year,
            'month': month,
            'day': day,
            'today': date == now,
        }

    # set time_epoch to the first day in the matrix
    time_epoch = time.mktime((year, month, 1, 0, 0, 0, 0, 0, -1))
    time_tuple = time.localtime(time_epoch) # fills in weekday
    time_epoch = time_epoch - 24 * 60 * 60 * time_tuple[6]
    end_time = end_of_month(time_epoch)
    
    # create matrix
    matrix = []
    while time_epoch < end_time:
        matrix.append([])
        for weekday in range(7):
            matrix[-1].append(get_day(time_epoch))
            time_epoch = time_epoch + 24 * 60 * 60

    return matrix
