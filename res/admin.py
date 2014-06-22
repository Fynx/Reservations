from django.contrib import admin
from res.models import Room, Reservation, Free, Attribute
from django import forms
from django.db.models import Q

class FreeForm(forms.ModelForm):
    class Meta:
        model = Free

    def clean(self):
        cleaned_data = super(FreeForm, self).clean()
        new_room = cleaned_data.get("room")
        new_date = cleaned_data.get("date")
        time_from = cleaned_data.get("starthour")
        time_to = cleaned_data.get("endhour")

        if time_from > time_to:
            raise forms.ValidationError('"From" must be greater than "To"')

        colliding_reservations = Reservation.objects.filter(room=new_room) \
                .filter(date=new_date) \
                .filter(Q(starthour__lt=time_to, starthour__gte=time_from) \
                | Q(endhour__gt=time_from, endhour__lte=time_to))
        if colliding_reservations.count() > 0:
            raise forms.ValidationError('Collides with existing reservation.')

        colliding_frees = Free.objects.filter(room=new_room) \
                .filter(date=new_date) \
                .filter(Q(starthour__lt=time_to, starthour__gte=time_from) \
                | Q(endhour__gt=time_from, endhour__lte=time_to))
        if colliding_frees.count() > 0:
            raise forms.ValidationError('Collides with existing free time.')

        return cleaned_data

class FreeAdmin(admin.ModelAdmin):
    form = FreeForm

class FreeInline(admin.StackedInline):
    model = Free
    extra = 1

class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,       {'fields': ['name']}),
        ('Capacity', {'fields': ['capacity']}),
        (None,       {'fields': ['description']}),
    ]
    inlines = [FreeInline]

class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name',     {'fields': ['name']}),
        ('Password', {'fields': ['password']}),
    ]

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation

    def clean(self):
        cleaned_data = super(ReservationForm, self).clean()
        new_room = cleaned_data.get("room")
        new_date = cleaned_data.get("date")
        time_from = cleaned_data.get("starthour")
        time_to = cleaned_data.get("endhour")

        if time_from > time_to:
            raise forms.ValidationError('"From" must be greater than "To"')

        colliding_reservations = Reservation.objects.filter(room=new_room) \
                .filter(date=new_date) \
                .filter(Q(starthour__lt=time_to, starthour__gte=time_from) \
                | Q(endhour__gt=time_from, endhour__lte=time_to))
        if colliding_reservations.count() > 0:
            raise forms.ValidationError('Collides with existing reservation.')

        colliding_frees = Free.objects.filter(room=new_room) \
                .filter(date=new_date) \
                .filter(Q(starthour__lt=time_to, starthour__gte=time_from) \
                | Q(endhour__gt=time_from, endhour__lte=time_to))
        if colliding_frees.count() > 0:
            raise forms.ValidationError('Collides with existing free time.')

        return cleaned_data

class ReservationAdmin(admin.ModelAdmin):
    form = ReservationForm

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute

    def clean(self):
        cleaned_data = super(AttributeForm, self).clean()
        return cleaned_data

class AttributeAdmin(admin.ModelAdmin):
    form = AttributeForm

admin.site.register(Room, RoomAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Free, FreeAdmin)
admin.site.register(Attribute, AttributeAdmin)