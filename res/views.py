from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render
from datetime import datetime
import logging
import math
import re

from res.models import Room, Reservation, Free, Hours, Date

logger = logging.getLogger(__name__)

@login_required
@transaction.non_atomic_requests
def index(request, error=''):
    sort_order            = request.GET.get('sort_order', 'id')
    filter_name           = request.GET.get('filter_name', '')
    filter_capacity_lower = request.GET.get('filter_capacity_lower', '0')
    filter_capacity_upper = request.GET.get('filter_capacity_upper', '1000')
    page_number           = request.GET.get('page_number', '0')
    # would be nice to give the choice to the user
    elems_per_page = 10

    filter_capacity_lower = int(filter_capacity_lower)
    filter_capacity_upper = int(filter_capacity_upper)

    if page_number == '':
        page_number = 0
    else:
        page_number = int(page_number)

    room_list = Room.objects.filter(Q(name__contains=filter_name) \
            | Q(description__contains=filter_name)) \
            .filter(capacity__gte=filter_capacity_lower) \
            .filter(capacity__lte=filter_capacity_upper) \
            .order_by(sort_order)

    room_list_count = room_list.count()
    pages_number = int(math.ceil(float(room_list_count) \
            / float(elems_per_page)))

    if page_number > math.ceil((room_list_count - 1) / elems_per_page):
        page_number = int(math.ceil(float(room_list_count - 1) / \
                float(elems_per_page)))
    if page_number < 1:
        page_number = 1

    pages = ''
    for i in range (0, pages_number):
        pages = pages + 'x'

    return render(request, 'res/index.html', {'room_list': \
            room_list[(page_number - 1) * elems_per_page: \
            min(page_number * elems_per_page, room_list_count)], \
            'filter_name': filter_name, \
            'filter_capacity_lower': filter_capacity_lower, \
            'filter_capacity_upper': filter_capacity_upper, \
            'sort_order': sort_order, \
            'page_number': page_number, 'pages': pages, \
            'mult_pages': pages_number > 1, \
            'first_entry': str((page_number - 1) * 10)})

@login_required
@transaction.non_atomic_requests
def date(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    free_list = room.free_set.all().order_by('starthour').order_by('date')
    date_list = []

    for index in range(0, len(free_list)):
        free = free_list[index]
        c_hours = Hours(free.starthour, free.endhour)
        if len(date_list) == 0 or free.date != date_list[-1].date:
            date = Date(free.date)
            date.add_hours(c_hours)
            date_list.append(date)
        else:
            date_list[-1].add_hours(c_hours)

    return render(request, 'res/date.html', {'room': room, \
            'date_list': date_list})

@login_required
@transaction.non_atomic_requests
def check(request):
    room_id   = int(request.GET.get('room_id', ''))
    room      = get_object_or_404(Room, pk=room_id)
    date_list = request.GET.getlist('date')

    if not date_list:
        return index(request, 'res/index.html')

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

    logger.error("Checking...")

    for date in result_dates:
        if not room.is_free(date):
            return render(request, 'res/index.html',
                    {'error': 'Error occurred during registration. Date '
                        + date.to_string() + ' is not available.'})

    logger.error("Registering!")

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

