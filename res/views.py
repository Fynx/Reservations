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
def index(request):
    sort_order = request.GET.get('sort_order', 'id')
    filter_name = request.GET.get('filter_name', '')
    filter_capacity_lower = request.GET.get('filter_capacity_lower', '0')
    filter_capacity_upper = request.GET.get('filter_capacity_upper', '1000')
    page_number = request.GET.get('page_number', '0')
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

    for free in free_list:
        c_hours = Hours(free.starthour, free.endhour)
        if len(date_list) == 0 or free.date != date_list[-1].date:
            date_list.append(Date(free.date, c_hours))
        else:
            date_list[-1].add_hours(c_hours)

    return render(request, 'res/date.html', {'room': room, \
            'date_list': date_list})

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
    starthour = correct_time_value(starthour)
    startminutes = correct_time_value(startminutes)
    endhour = correct_time_value(endhour)
    endminutes = correct_time_value(endminutes)

    if check_if_hour(starthour) is None \
            or check_if_hour(endhour) is None \
            or check_if_minutes(startminutes) is None \
            or check_if_minutes(endminutes) is None:
        return False

    starttime = datetime.strptime(starthour + '-' + startminutes, \
            "%H-%M").time()
    endtime = datetime.strptime(endhour + '-' + endminutes, "%H-%M").time()

    if starttime >= endtime:
        return False

    if segbegin < segend:
        return segbegin <= starttime and segend >= endtime \
                and segbegin != segend
    else:
        return not(starttime < segbegin and starttime >= segend) \
                and not(endtime > segend and endtime <= segbegin) \

@login_required
@transaction.non_atomic_requests
def check(request, room_id, free_id):
    starthour = request.POST.get('starthour', '')
    startminutes = request.POST.get('startminutes', '')
    endhour = request.POST.get('endhour', '')
    endminutes = request.POST.get('endminutes', '')

    free = get_object_or_404(Free, pk=free_id)

    startminutes = correct_time_value(startminutes)
    endminutes = correct_time_value(endminutes)

    if not check_hours(starthour, startminutes, endhour, endminutes, \
            free.starthour, free.endhour):
        return render(request, 'res/hours.html', {'free': free, \
                'errors': True})
    else:
        return render(request, 'res/check.html', {'free': free, \
                'starthour': starthour + ":" + startminutes, \
                'endhour': endhour + ":" + endminutes})

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

@login_required
@transaction.atomic
def confirmed(request, free_id):
    starthour = request.POST.get('starthour', '')
    endhour = request.POST.get('endhour', '')

    starttime = datetime.strptime(fixed_time(starthour), '%H:%M').time()
    endtime = datetime.strptime(fixed_time(endhour), '%H:%M').time()
    errors = False

    try:
        free = Free.objects.get(pk=free_id)
    except Free.DoesNotExist:
        errors = True

    if not errors:
        if free.starthour < starttime:
            prev_free = Free.objects.create(room=free.room, date=free.date, \
                    starthour=free.starthour, endhour=starttime)
        if free.endhour > endtime:
            next_free = Free.objects.create(room=free.room, date=free.date, \
                    starthour=endtime, endhour=free.endhour)
        Reservation.objects.create(room=free.room, date=free.date, \
                starthour=starttime, endhour=endtime, user=request.user)
        free.delete()

    return render(request, 'res/confirmed.html', {'errors': errors})

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

