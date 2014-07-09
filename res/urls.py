from django.conf.urls import patterns, url

from res.models import Room, Reservation, Free

from res import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<room_id>\d+)/date/$', views.date, name='date'),
    url(r'^check/$', views.check, name='check'),
    url(r'^confirmed/$', views.confirmed, name='confirmed'),
    url('^my_reservations/$', views.my_reservations),
)