from django.contrib import admin
from django import forms
from .models import Doctor, DoctorAvailability


class DoctorAvailabilityForm(forms.ModelForm):

    days = forms.MultipleChoiceField(
        choices=DoctorAvailability.DAYS,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = DoctorAvailability
        fields = '__all__'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'specialization',
        'phone',
        'email',
        'experience',
        'consultation_fee',
    ]

    search_fields = ['name', 'specialization', 'email']


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):

    form = DoctorAvailabilityForm

    list_display = [
        'doctor',
        'display_days',
        'start_time',
        'end_time',
        'slot_duration',
        'is_available',
    ]

    list_filter = ['is_available']
    search_fields = ['doctor__name']

    def display_days(self, obj):
        return ', '.join(obj.days)

    display_days.short_description = 'Available Days'