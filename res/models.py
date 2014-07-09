from django.db import models

import datetime
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

    def cut_front(self, m):
        new_minutes = int((m + self.start.minute) % 60)
        new_hours   = int(m / 60) + self.start.hour
        new_time    = datetime.time(hour=new_hours, minute=new_minutes)
        return Hours(self.start, new_time)

    def cut_back(self, m):
        new_minutes = int((self.start.minute + m) % 60)
        new_hours   = int(m / 60) + self.start.hour
        new_time    = datetime.time(hour=new_hours, minute=new_minutes)
        return Hours(new_time, self.end)

    def minutes(self):
        return self.end.minute - self.start.minute \
                + 60 * (self.end.hour - self.start.hour)

class Date:
    def __init__(self, date, hours):
        self.date = date
        self.hours = []
        self.add_hours(hours)

    def to_string(self):
        string = str(self.date) + ' ('
        for i in range(len(self.hours)):
            if i != 0:
                string += ', '
            string += self.hours[i].to_string()
        string += ')'
        return string

    def add_hours(self, hours):
        index = len(self.hours)
        if index == 0 or hours.start != self.hours[-1].end:
            self.hours.append(hours)
        else:
            self.hours[-1].end = hours.end
            index = index - 1

        while self.hours[index].minutes() > 60 and index < 100:
            self.hours.append(self.hours[index].cut_back(60))
            self.hours[index] = self.hours[index].cut_front(60)
            index = index + 1
