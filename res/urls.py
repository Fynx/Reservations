from django.conf.urls import patterns, url

from res.models import Room, Reservation, Free

from res import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^check/$', views.check, name='check'),
    url(r'^confirmed/$', views.confirmed, name='confirmed'),
    url(r'^my_reservations/$', views.my_reservations),
    url(r'^attr_dump/$', views.attr_dump),
    url(r'^rooms_dump/$', views.rooms_dump),
    url(r'^terms_dump/$', views.terms_dump),
)