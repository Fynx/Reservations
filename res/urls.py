from django.conf.urls import patterns, url

from res.models import Room, Reservation, Free

from res import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<room_id>\d+)/date/$', views.date, name='date'),
    url(r'^(?P<room_id>\d+)/date/(?P<free_id>\d+)/check/$', \
            views.check, name='check'),
    url(r'^(?P<free_id>\d+)/confirmed/$', views.confirmed, name='confirmed'),
    url('^my_reservations/$', views.my_reservations),
)