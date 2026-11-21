from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from urllib.parse import quote
from django.http import HttpResponseRedirect

from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

def home(request):

    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()

    total_services = 6

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'total_services': total_services,
    }

    return render(request, 'home.html', context)


@user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url='/admin/login/'
)
def dashboard(request):

    # Update appointment status and open WhatsApp
    if request.method == 'POST':

        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')

        valid_statuses = [
            'Pending',
            'Approved',
            'Completed',
            'Cancelled'
        ]

        if new_status in valid_statuses:

            appointment = Appointment.objects.filter(
                id=appointment_id
            ).select_related('patient', 'doctor').first()

            if appointment:

                appointment.status = new_status
                appointment.save()

                # Get patient phone number
                phone = appointment.patient.phone

                # Keep only digits
                phone = ''.join(
                    digit for digit in phone if digit.isdigit()
                )

                # Add India country code if number has 10 digits
                if len(phone) == 10:
                    phone = '91' + phone

                # Generate booking ID
                booking_id = f"HOSP-{appointment.id:04d}"

                # Create WhatsApp message
                message = (
                    f"Hello {appointment.patient.name},\n\n"
                    f"Your appointment at CityCare Hospital "
                    f"has been {new_status}.\n\n"
                    f"Doctor: Dr. {appointment.doctor.name}\n"
                    f"Specialization: "
                    f"{appointment.doctor.specialization}\n"
                    f"Date: {appointment.appointment_date}\n"
                    f"Time: {appointment.appointment_time}\n"
                    f"Booking ID: {booking_id}\n\n"
                    f"Thank you for choosing CityCare Hospital."
                )

                # Encode message
                encoded_message = quote(message)

                # WhatsApp URL
                whatsapp_url = (
                    f"https://wa.me/{phone}?text={encoded_message}"
                )

                return HttpResponseRedirect(whatsapp_url)

        return redirect('dashboard')

    # Summary counts
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()

    pending_appointments = Appointment.objects.filter(
        status='Pending'
    ).count()

    approved_appointments = Appointment.objects.filter(
        status='Approved'
    ).count()

    completed_appointments = Appointment.objects.filter(
        status='Completed'
    ).count()

    cancelled_appointments = Appointment.objects.filter(
        status='Cancelled'
    ).count()

    # Patient records filtered by appointment status
    patient_status = request.GET.get(
        'patient_status', ''
    ).strip()

    patients = Patient.objects.all().order_by('-id')

    if patient_status in [
        'Pending', 'Approved', 'Completed', 'Cancelled'
    ]:
        patients = patients.filter(
            appointment__status=patient_status
        ).distinct()

    # All appointment records
    appointments = Appointment.objects.select_related(
        'patient', 'doctor'
    ).all().order_by('-id')

    # Appointment filters using status and date
    appointment_status = request.GET.get(
        'status', ''
    ).strip()

    appointment_date = request.GET.get(
        'date', ''
    ).strip()

    if appointment_status in [
        'Pending', 'Approved', 'Completed', 'Cancelled'
    ]:
        appointments = appointments.filter(
            status=appointment_status
        )

    if appointment_date:
        appointments = appointments.filter(
            appointment_date=appointment_date
        )

    # Dashboard data
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'patients': patients,
        'appointments': appointments,
        'patient_status': patient_status,
        'selected_status': appointment_status,
        'selected_date': appointment_date,
    }

    return render(request, 'dashboard.html', context)