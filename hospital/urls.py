from django.contrib import admin
from django.urls import path

from . import views
from appointments import views as appointment_views
from doctors import views as doctor_views
from patients import views as patient_views


urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # Homepage
    path('', views.home, name='home'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Appointment booking
    path(
        'book-appointment/',
        appointment_views.book_appointment,
        name='book_appointment'
    ),

    # Doctors
    path(
        'doctors/',
        doctor_views.doctor_list,
        name='doctor_list'
    ),

    # Patients
    path(
        'patients/',
        patient_views.patient_list,
        name='patient_list'
    ),

    # Appointment list
    path(
        'appointments/',
        appointment_views.appointment_list,
        name='appointment_list'
    ),

    # Update appointment status
    path(
        'appointments/update/<int:appointment_id>/',
        appointment_views.update_appointment_status,
        name='update_appointment_status'
    ),

    # Check appointment status
    path(
        'check-appointment-status/',
        appointment_views.check_appointment_status,
        name='check_appointment_status'
    ),

    # Get available doctor slots
    path(
        'get-doctor-slots/',
        appointment_views.get_doctor_slots,
        name='get_doctor_slots'
    ),

]