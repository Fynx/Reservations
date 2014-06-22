from django.test import TestCase
from models import Room, Reservation, Free
from django.contrib.auth.models import User
from datetime import datetime

class RoomTestCase(TestCase):
    def setUp(self):
        Room.objects.create(name='Blue', capacity='10', \
                description='Nice blue room.')
        Room.objects.create(name='Yellow', capacity='7', \
                description='Simple yellow room.')
        Room.objects.create(name='Red', capacity='12', \
                description='Ugly red room.')
    
    def test_name(self):
        k = Room.objects.filter(name__startswith='Blue')
        self.assertEqual(k.count(), 1)
        p = Room(name='Magenta', capacity=1)
        p.save()
        self.assertEqual(Room.objects.count(), 4)
        p.delete()
        self.assertEqual(Room.objects.count(), 3)
    
    def test_description(self):
        k = Room.objects.filter(description__contains='Nice')
        self.assertEqual(k.count(), 1)
        p = Room(name='a', capacity=1, description='Not nice')
        p.save()
        self.assertEqual(Room.objects.count(), 4)
        p.delete()
        self.assertEqual(Room.objects.count(), 3)
        
    def test_capacity(self):
        p = Room(name='a', capacity=5)
        p.save()
        self.assertEqual(Room.objects.count(), 4)
        p.delete()
        self.assertEqual(Room.objects.count(), 3)        

class FreeTestCase(TestCase):
    def setUp(self):
        Room.objects.create(name='Blue', capacity='10', \
                description='Nice blue room.')
    
    def test_hours(self):
        p = Free(starthour=datetime.strptime('12:30', '%H:%M').time(), \
                room=Room.objects.get(name='Blue'), \
                date=datetime.strptime('11.02.01', '%d.%m.%y').date(),
                endhour=datetime.strptime('14:30', '%H:%M').time())
        p.save()
        self.assertEqual(Free.objects.count(), 1)
        p.delete()
        self.assertEqual(Free.objects.count(), 0)
    
    def test_date(self):
        p = Free(starthour=datetime.strptime('12:30', '%H:%M').time(), \
                date=datetime.strptime('11.02.01', '%d.%m.%y').date(),
                room=Room.objects.get(name='Blue'), \
                endhour=datetime.strptime('14:30', '%H:%M').time())
        p.save()
        self.assertEqual(Free.objects.count(), 1)
        p.delete()
        self.assertEqual(Free.objects.count(), 0)

class ReservationTestCase(TestCase):
    def setUp(self):
        Room.objects.create(name='Blue', capacity='10', \
                description='Nice blue room.')
        User.objects.create(username='Myname', email='myname@myname.com', \
                password='Mhasdasdi')
    
    def test_hours(self):
        p = Reservation(starthour=datetime.strptime('12:30', \
                '%H:%M').time(), room=Room.objects.get(name='Blue'),
                date=datetime.strptime('11.02.01', '%d.%m.%y').date(), \
                endhour=datetime.strptime('14:30', '%H:%M').time(), \
                user=User.objects.get(username='Myname'))
        p.save()
        self.assertEqual(Reservation.objects.count(), 1)
        p.delete()
        self.assertEqual(Reservation.objects.count(), 0)
    
    def test_date(self):
        p = Reservation(starthour=datetime.strptime('12:30', \
                '%H:%M').time(), date=datetime.strptime('11.02.01', \
                '%d.%m.%y').date(), room=Room.objects.get(name='Blue'), \
                endhour=datetime.strptime('14:30', '%H:%M').time(), \
                user=User.objects.get(username='Myname'))
        p.save()
        self.assertEqual(Reservation.objects.count(), 1)
        p.delete()
        self.assertEqual(Reservation.objects.count(), 0)
