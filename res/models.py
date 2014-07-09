from django.db import models

import datetime as pdatetime
from datetime import datetime
from django.utils import timezone
from django.db import models

from django.contrib.auth.models import User

import logging

logger = logging.getLogger(__name__)

class Attribute(models.Model):
    name = models.CharField(unique=True, max_length=30)
    description = models.CharField(blank=True, max_length=200)
    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(unique=True, max_length=30)
    capacity = models.DecimalField(max_digits=3, decimal_places=0)
    description = models.CharField(blank=True, max_length=2000)
    attributes = models.ManyToManyField(Attribute)
    def __str__(self):
        return self.name

    def is_free(self, res_date):
        c_date = datetime.combine(res_date.date, pdatetime.time.min)
        n_date = c_date + pdatetime.timedelta(days=1)

        frees = self.free_set.filter(date__gte=c_date).filter(date__lte=n_date)

        for hours in res_date.hours:
            start = datetime.combine(res_date.date, hours.start)
            end   = datetime.combine(res_date.date, hours.end)
            if not frees.filter(date__lte=start).filter(date__gte=end).exists():
                return False
        return True


class Free(models.Model):
    room = models.ForeignKey(Room)
    date = models.DateField('date')
    starthour = models.TimeField()
    endhour = models.TimeField()
    def __str__(self):
        return '%d.%d.%d %d:%d-%d:%d %s' % (self.date.year, self.date.month, \
                self.date.day, self.starthour.hour, self.starthour.minute, \
                self.endhour.hour, self.endhour.minute, self.room.name)

class Reservation(models.Model):
    room = models.ForeignKey(Room)
    date = models.DateField('date')
    starthour = models.TimeField()
    endhour = models.TimeField()
    user = models.ForeignKey(User)
    def __str__(self):
        return '%s %d.%d.%d %d:%d-%d:%d %s' % (self.user.username, \
                self.date.year, self.date.month, \
                self.date.day, self.starthour.hour, \
                self.starthour.minute, self.endhour.hour, \
                self.endhour.minute, \
                self.room.name)

class Hours:
    def __init__(self, start, end):
        self.start = start
        self.end   = end

    def to_string(self):
        return self.start.strftime('%H:%M') + '-' + self.end.strftime('%H:%M')

    def from_string(string):
        start = datetime.strptime(string[0:5], '%H:%M').time()
        end   = datetime.strptime(string[6:11], '%H:%M').time()
        return Hours(start, end)

    def cut_front(self, m):
        new_minutes = int((m + self.start.minute) % 60)
        new_hours   = int(m / 60) + self.start.hour
        new_time    = pdatetime.time(hour=new_hours, minute=new_minutes)
        return Hours(self.start, new_time)

    def cut_back(self, m):
        new_minutes = int((self.start.minute + m) % 60)
        new_hours   = int(m / 60) + self.start.hour
        new_time    = pdatetime.time(hour=new_hours, minute=new_minutes)
        return Hours(new_time, self.end)

    def minutes(self):
        return self.end.minute - self.start.minute \
                + 60 * (self.end.hour - self.start.hour)

    #Auxiliary functions

    def correct_time_value(value):
        if value == '':
            return '00'
        else:
            return value

    def check_if_hour(t):
        return re.match('^(0|1\d)|(2(0|1|2|3))|\d$', t)

    def check_if_minutes(m):
        return re.match('^(0|1|2|3|4|5)?\d$', m)

    def check_hours(starthour, startminutes, endhour, endminutes, segbegin, \
            segend):
        starthour    = correct_time_value(starthour)
        startminutes = correct_time_value(startminutes)
        endhour      = correct_time_value(endhour)
        endminutes   = correct_time_value(endminutes)

        if check_if_hour(starthour) is None \
                or check_if_hour(endhour) is None \
                or check_if_minutes(startminutes) is None \
                or check_if_minutes(endminutes) is None:
            return False

        starttime = pdatetime.strptime(starthour + '-' + startminutes, \
                "%H-%M").time()
        endtime = pdatetime.strptime(endhour + '-' + endminutes, "%H-%M").time()

        if starttime >= endtime:
            return False

        if segbegin < segend:
            return segbegin <= starttime and segend >= endtime \
                    and segbegin != segend
        else:
            return not(starttime < segbegin and starttime >= segend) \
                    and not(endtime > segend and endtime <= segbegin)

    def fixed_time(string):
        if re.match('^\d\d:\d\d$', string):
            return string
        elif re.match('^\d:\d\d$', string):
            return '0' + string
        elif re.match('^\d:\d$', string):
            return '0' + string[0] + ':' + '0' + string[2]
        elif re.match('^\d\d:\d$', string):
            return string[:2] + ':0' + string[3]
        elif re.match('^\d\d:$', string):
            return string + '00'
        else:
            return '00:00'


class Date:
    def __init__(self, date):
        self.date = date
        self.hours = []

    def to_string(self):
        string = self.get_date_string() + ' ('
        for i in range(len(self.hours)):
            if i != 0:
                string += ', '
            string += self.hours[i].to_string()
        string += ')'
        return string

    # String from which a Date object is created is slightly different from
    # the one created by to_string method.
    def from_string(string):
        date  = datetime.strptime(string[0:8], "%d.%m.%y")
        hours = Hours.from_string(string[9:20])
        date_object = Date(date)
        date_object.add_hours(hours)
        return date_object

    def get_date_string(self):
        return self.date.strftime("%d.%m.%y")

    def add_hours(self, hours):
        if len(self.hours) == 0 or hours.start != self.hours[-1].end:
            self.hours.append(hours)
        else:
            self.hours[-1].end = hours.end

    def cut_hours(self):
        new_date = Date(self.date)
        index = 0
        for s_index in range(len(self.hours)):
            new_date.hours.append(self.hours[s_index])
            while new_date.hours[index].minutes() > 60 and index < 100:
                new_date.hours.append(new_date.hours[index].cut_back(60))
                new_date.hours[index] = new_date.hours[index].cut_front(60)
                index = index + 1
            index = index + 1

        return new_date
