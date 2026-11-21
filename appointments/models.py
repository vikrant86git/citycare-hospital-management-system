import uuid
from django.db import models
from patients.models import Patient
from doctors.models import Doctor


class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    booking_id = models.UUIDField(
    default=uuid.uuid4,
    unique=True,
    editable=False
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name}"