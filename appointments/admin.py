from django.contrib import admin
from .models import Appointment


class AppointmentAdmin(admin.ModelAdmin):

    list_display = [
        'booking_code',
        'patient',
        'doctor',
        'appointment_date',
        'appointment_time',
        'status',
    ]

    list_filter = ['status', 'appointment_date']

    search_fields = [
        'patient__name',
        'patient__email',
        'doctor__name',
    ]

    ordering = ['-appointment_date']

    def booking_code(self, obj):
        return f"HOSP-{obj.id:04d}"

    booking_code.short_description = 'Booking ID'


admin.site.register(Appointment, AppointmentAdmin)