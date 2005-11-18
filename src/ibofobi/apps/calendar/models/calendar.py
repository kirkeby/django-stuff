# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import meta

class EventClass(meta.Model):
    title = meta.CharField(maxlength=20)

    class META:
        admin = meta.Admin(
            fields=(
                (None, {'fields': ('title',)}),
            ),
        )
        module_name = 'eventclasses'
        verbose_name_plural = 'event classes'

    def __repr__(self):
        return self.title

class Event(meta.Model):
    title = meta.CharField(maxlength=80)
    start_date = meta.DateField()
    end_date = meta.DateField()

    class META:
        ordering = ['-start_date']
        admin = meta.Admin(
            fields=(
                (None, {'fields': ('title', 'start_date', 'end_date')}),
            ),
            date_hierarchy='start_date',
        )

    def get_absolute_url(self):
        return '/calendar/%d/%d/' % (self.start_date.year, self.start_date.month)

    def __repr__(self):
        if self.end_date == self.start_date:
            return self.start_date.strftime('%d. %b %Y: ') + self.title 
        else:
            st = self.start_date.strftime('%d. %b %Y')
            en = self.end_date.strftime('%d. %b %Y')
            return '%s -> %s: %s' % (st, en, self.title)

cron_help_text = '''A cron-like date-description with these fields:<br />
1. Day of the month [1,31]<br />
2. Month of the year [1,12]<br />
3. Day of the week ([0,6] with 0=Sunday)
'''

class RecurringEvent(meta.Model):
    title = meta.CharField(maxlength=80)
    fields = meta.CharField(maxlength=30, help_text=cron_help_text)
    classes = meta.ManyToManyField(EventClass, related_name='class',
                                   blank=True)

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('title', 'fields')}),
                ('Classes', {'fields': ('classes',)}),
            )
        )
        db_table = 'calendar_recevents'

    def __repr__(self):
        return self.title

    def _module_is_here(self, when):
        day, mon, weekday = parse_cron_reccurence(self.fields)

        if day:
            if not when.day == day:
                return False

        if mon:
            if not when.month == mon:
                return False

        if weekday:
            if not when.weekday() == weekday - 1:
                return False

        return True

    def _manipulator_validate_fields(self, field_data, all_data):
        try:
            parse_cron_reccurence(field_data)
        except:
            from django.core import validators
            import sys
            tp, ex, tb = sys.exc_info()
            raise validators.ValidationError, ex.args
        
    def _module_parse_cron_reccurence(fields):
        month_names = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12,
        }
        weekday_names = {
            'monday': 1, 'mon': 1,
            'tuesday': 2, 'tue': 2,
            'wednesday': 3, 'wed': 3,
            'thursday': 4, 'thu': 4,
            'friday': 5, 'fri': 5,
            'saturday': 6, 'sat': 6,
            'sunday': 7, 'sun': 7,
        }

        try:
            day, mon, weekday = fields.split(' ')
        except ValueError:
            raise 'A cron date-description must have exactly three fields'

        if day == '*':
            day = None
        else:
            try:
                day = int(day)
            except ValueError:
                raise ValueError, 'Invalid day-of-month %s' % day

        if mon == '*':
            mon = None
        elif mon.lower() in month_names:
            mon = month_names[mon.lower()]
        else:
            try:
                mon = int(mon)
            except ValueError:
                raise ValueError, 'Invalid month %s' % mon

        if weekday == '*':
            weekday = None
        elif weekday.lower() in weekday_names:
            weekday = weekday_names[weekday.lower()]
        else:
            try:
                weekday = int(weekday)
            except ValueError:
                raise ValueError, 'Invalid weekday %s' % weekday

        return day, mon, weekday

