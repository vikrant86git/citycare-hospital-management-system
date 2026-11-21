from datetime import date, datetime, timedelta
from urllib.parse import quote

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse

from patients.models import Patient
from doctors.models import Doctor, DoctorAvailability
from .models import Appointment


# Generate available appointment slots
def get_available_slots(doctor, selected_date):

    day_name = selected_date.strftime("%A")

    availability_records = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_available=True
    )

    available_times = []

    for availability in availability_records:

        if day_name not in availability.days:
            continue

        start_datetime = datetime.combine(
            selected_date,
            availability.start_time
        )

        end_datetime = datetime.combine(
            selected_date,
            availability.end_time
        )

        duration = availability.slot_duration

        if duration <= 0 or start_datetime >= end_datetime:
            continue

        current_time = start_datetime

        while current_time + timedelta(minutes=duration) <= end_datetime:

            slot_time = current_time.time()

            # Do not show past time slots
            if selected_date == date.today():
                if slot_time <= datetime.now().time():
                    current_time += timedelta(minutes=duration)
                    continue

            # Check whether the slot is already booked
            already_booked = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=selected_date,
                appointment_time=slot_time
            ).exclude(
                status="Cancelled"
            ).exists()

            if not already_booked:
                available_times.append(
                    slot_time.strftime("%H:%M")
                )

            current_time += timedelta(minutes=duration)

    return sorted(set(available_times))


# AJAX: Get available slots
def get_doctor_slots(request):

    doctor_id = request.GET.get("doctor")
    appointment_date = request.GET.get("date")

    if not doctor_id or not appointment_date:
        return JsonResponse({"slots": []})

    try:
        doctor = Doctor.objects.get(id=doctor_id)
        selected_date = date.fromisoformat(appointment_date)

    except (Doctor.DoesNotExist, ValueError):
        return JsonResponse({"slots": []})

    if selected_date < date.today():
        return JsonResponse({"slots": []})

    slots = get_available_slots(
        doctor,
        selected_date
    )

    return JsonResponse({"slots": slots})


# Book Appointment with Validation
def book_appointment(request):

    doctors = Doctor.objects.all()
    errors = []

    if request.method == "POST":

        patient_name = request.POST.get("patient_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        age_input = request.POST.get("age", "").strip()
        gender = request.POST.get("gender", "").strip()
        address = request.POST.get("address", "").strip()
        appointment_date = request.POST.get("date", "").strip()
        appointment_time = request.POST.get("time", "").strip()
        reason = request.POST.get("reason", "").strip()
        doctor_id = request.POST.get("doctor", "").strip()

        if not all([
            patient_name, phone, email, age_input,
            gender, address, appointment_date,
            appointment_time, reason, doctor_id
        ]):
            errors.append("Please fill in all required fields.")

        if patient_name and not patient_name.replace(" ", "").isalpha():
            errors.append("Please enter a valid patient name.")

        phone_digits = "".join(filter(str.isdigit, phone))

        if len(phone_digits) < 10 or len(phone_digits) > 15:
            errors.append("Please enter a valid phone number.")

        try:
            validate_email(email)
        except ValidationError:
            errors.append("Please enter a valid email address.")

        try:
            age = int(age_input)

            if age < 1 or age > 120:
                errors.append("Age must be between 1 and 120.")

        except ValueError:
            age = 0
            errors.append("Please enter a valid age.")

        try:
            selected_date = date.fromisoformat(appointment_date)

            if selected_date < date.today():
                errors.append("Appointment date cannot be in the past.")

        except ValueError:
            selected_date = None
            errors.append("Please select a valid appointment date.")

        doctor = None

        if doctor_id:
            try:
                doctor = Doctor.objects.get(id=doctor_id)
            except (Doctor.DoesNotExist, ValueError):
                errors.append("Please select a valid doctor.")

        # Validate appointment time against doctor's availability
        if doctor and selected_date and appointment_time:

            available_slots = get_available_slots(
                doctor,
                selected_date
            )

            if appointment_time not in available_slots:
                errors.append(
                    "This appointment slot is not available. "
                    "Please select another time."
                )

        if not errors:

            patient, created = Patient.objects.get_or_create(
                email=email,
                defaults={
                    "name": patient_name,
                    "phone": phone,
                    "age": age,
                    "gender": gender,
                    "address": address,
                }
            )

            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=selected_date,
                appointment_time=datetime.strptime(
                    appointment_time,
                    "%H:%M"
                ).time(),
                reason=reason,
            )

            booking_code = f"HOSP-{appointment.id:04d}"

            return render(
                request,
                "appointment_success.html",
                {
                    "appointment": appointment,
                    "booking_code": booking_code,
                }
            )

    return render(
        request,
        "book_appointment.html",
        {
            "doctors": doctors,
            "errors": errors,
        }
    )


# View All Appointments with Search and Filters (Staff Only)
@user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url="/admin/login/"
)
def appointment_list(request):

    appointments = Appointment.objects.select_related(
        "patient", "doctor"
    ).all()

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    appointment_date = request.GET.get("date", "").strip()

    if search:

        query = Q(patient__name__icontains=search)

        if search.upper().startswith("HOSP-"):
            try:
                booking_number = int(
                    search.upper().replace("HOSP-", "")
                )
                query |= Q(id=booking_number)
            except ValueError:
                pass

        appointments = appointments.filter(query)

    valid_statuses = [
        "Pending",
        "Approved",
        "Completed",
        "Cancelled"
    ]

    if status in valid_statuses:
        appointments = appointments.filter(status=status)

    if appointment_date:
        appointments = appointments.filter(
            appointment_date=appointment_date
        )

    return render(
        request,
        "appointments.html",
        {
            "appointments": appointments,
            "search": search,
            "selected_status": status,
            "selected_date": appointment_date,
        }
    )


# Update Appointment Status and Open WhatsApp
@user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url="/admin/login/"
)
def update_appointment_status(request, appointment_id):

    if request.method == "POST":

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id
        )

        new_status = request.POST.get("status")

        valid_statuses = [
            "Pending",
            "Approved",
            "Completed",
            "Cancelled"
        ]

        if new_status in valid_statuses:

            appointment.status = new_status
            appointment.save()

            phone = "".join(
                filter(str.isdigit, appointment.patient.phone)
            )

            if len(phone) == 10:
                phone = "91" + phone

            if len(phone) < 10:
                return redirect("appointment_list")

            message = (
                f"Hello {appointment.patient.name},\n\n"
                f"Your CityCare Hospital appointment has been updated.\n\n"
                f"Booking ID: HOSP-{appointment.id:04d}\n"
                f"Doctor: {appointment.doctor.name}\n"
                f"Date: {appointment.appointment_date}\n"
                f"Time: {appointment.appointment_time}\n"
                f"Status: {appointment.status}\n\n"
                f"Thank you for choosing CityCare Hospital."
            )

            whatsapp_url = (
                f"https://wa.me/{phone}?text={quote(message)}"
            )

            return redirect(whatsapp_url)

    return redirect("appointment_list")


# Check Patient Appointment Status
def check_appointment_status(request):

    appointment = None
    error = None

    if request.method == "POST":

        booking_code = request.POST.get("booking_id", "").strip().upper()
        email = request.POST.get("email", "").strip()

        try:
            if not booking_code.startswith("HOSP-"):
                raise ValueError

            appointment_number = int(booking_code.replace("HOSP-", ""))

            appointment = Appointment.objects.get(
                id=appointment_number,
                patient__email__iexact=email
            )

        except (ValueError, Appointment.DoesNotExist):
            error = "Invalid Booking ID or Email. Please check your details."

    return render(request, "check_appointment_status.html", {
        "appointment": appointment,
        "error": error,
    })