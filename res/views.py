from datetime import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
import logging
import math
import re

from res.models import Attribute, Room, Reservation, Free, Hours, Date

logger = logging.getLogger(__name__)

@login_required
@transaction.non_atomic_requests
def index(request, error=''):
    return render(request, 'res/index.html', {'error': error})

@login_required
@transaction.non_atomic_requests
def check(request):
    room_id   = int(request.GET.get('room_id', ''))
    room      = get_object_or_404(Room, pk=room_id)

    date_from_list = request.GET.getlist('date_from')
    date_to_list   = request.GET.getlist('date_to')

    if not date_from_list:
        return index(request)

    date_from_list = sorted(date_from_list)
    date_to_list   = sorted(date_to_list)

    result_dates = []
    for i in range(len(date_from_list)):
        d_from = date_from_list[i]
        d_to   = date_to_list[i]

        if len(d_from.split('|')[1]) > 0 and len(d_to.split('|')[1]) > 0:
            date = d_from.split(',')[0] + ',' + d_from.split('|')[1] + '-' \
                    + d_to.split('|')[1]

            logger.error(date)

            full_date = Date.from_string(date)
            if full_date.hours[0].start < full_date.hours[0].end:
                if len(result_dates) == 0 or result_dates[-1].date != full_date.date:
                    result_dates.append(full_date)
                else:
                    result_dates[-1].add_hours(full_date.hours[0])

    if not result_dates:
        return index(request, 'Invalid fields\' values.')
    for date in result_dates:
        if not room.is_free(date):
            return index(request, 'Error occurred during registration. Date '
                    + date.to_string() + ' is not available.')
    return render(request, 'res/check.html', {'room': room,
            'date_list': result_dates})

@login_required
@transaction.atomic
def confirmed(request):
    room_id   = int(request.GET.get('room_id', ''))
    room      = get_object_or_404(Room, pk=room_id)
    date_list = request.GET.getlist('date')

    if not date_list:
        return render(request, 'res/index.html')

    result_dates = []
    for date in date_list:
        full_date = Date.from_string(date)
        if len(result_dates) == 0 or result_dates[-1].date != full_date.date:
            result_dates.append(full_date)
        else:
            result_dates[-1].add_hours(full_date.hours[0])

    for date in result_dates:
        if not room.is_free(date):
            return render(request, 'res/index.html',
                    {'error': 'Error occurred during registration. Date '
                        + date.to_string() + ' is not available.'})

    for date in result_dates:
        for hours in date.hours:
            free = Free.get_free(room_id, date.date, hours)
            free.split(hours.start, hours.end)
            Reservation.objects.create(room=room, date=date.date, \
                    starthour=hours.start, endhour=hours.end, \
                    user=request.user)

    return render(request, 'res/confirmed.html')

@login_required
@transaction.non_atomic_requests
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'res/my_reservations.html', \
            {'reservations': reservations})

@transaction.non_atomic_requests
def login_view(request):
    if request.user is not None and request.user.is_authenticated():
        return HttpResponseRedirect('/')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    nextpage = request.GET.get('next', '')
    user = auth.authenticate(username=username, password=password)
    errors = False
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect(nextpage)
    else:
        if not (username == '' and password == ''):
            # Show an error page
            errors = True
        return render(request, 'res/login.html', {'errors': errors})

@transaction.non_atomic_requests
def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")

@transaction.non_atomic_requests
def attr_dump(request):
    return HttpResponse(serializers.serialize("json", \
            Attribute.objects.all()))

@transaction.non_atomic_requests
def rooms_dump(request):
    return HttpResponse(serializers.serialize("json", Room.objects.all()))

@transaction.non_atomic_requests
def terms_dump(request):
    return HttpResponse(serializers.serialize("json", \
            Free.objects.all().order_by('starthour')))
