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

    def attributes_string(self):
        attrs = self.attributes.all()
        string = ''
        for a in attrs:
            logger.error(a.name)
            if len(string) != 0:
                string = string + ', '
            string = string + a.name
        logger.error("done")
        return string

    def is_free(self, res_date):
        for hours in res_date.hours:
            if not Free.get_free(self.id, res_date.date, hours):
                return False
        return True

    def apply_attribute_changes(self):
        if self.capacity < 15:
            board = Attribute.objects.get(name='whiteboard')
            if board == None:
                board = Attribute(name='whiteboard')
                board.save()
        else:
            board = Attribute.objects.get(name='greenboard')
            if board == None:
                board = Attribute(name='greenboard')
                board.save()
        if not self.attributes.filter(name=board.name):
            self.attributes.add(board)

    def apply_attribute_changes_to_all():
        rooms = Rooms.objects.all()
        for room in rooms:
            room.apply_attribute_changes()
            room.save()

    def has_attributes(self):
        return self.attributes.exists()

class Free(models.Model):
    room = models.ForeignKey(Room)
    date = models.DateField('date')
    starthour = models.TimeField()
    endhour = models.TimeField()

    def __str__(self):
        return '%d.%d.%d %d:%d-%d:%d %s' % (self.date.year, self.date.month, \
                self.date.day, self.starthour.hour, self.starthour.minute, \
                self.endhour.hour, self.endhour.minute, self.room.name)

    def split(self, start, end):
        if self.starthour < start:
            f1 = Free(room=self.room, date=self.date,
                    starthour=self.starthour, endhour=start)
            f1.save()
        if self.endhour > end:
            f2 = Free(room=self.room, date=self.date, starthour=end,
                    endhour=self.endhour)
            f2.save()
        self.delete()

    def get_free(room_id, date, hours):
        frees  = Free.objects.filter(room=room_id)
        result = frees.filter(date=date).filter(starthour__lte=hours.start) \
                .filter(endhour__gte=hours.end)
        if len(result) == 1:
            return result[0]
        else:
            return None

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
