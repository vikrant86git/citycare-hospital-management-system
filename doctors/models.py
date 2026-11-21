from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    experience = models.IntegerField()
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.name


class DoctorAvailability(models.Model):

    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='availability'
    )

    days = models.JSONField(default=list)

    start_time = models.TimeField()
    end_time = models.TimeField()

    slot_duration = models.PositiveIntegerField(default=30)

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.doctor.name} - {', '.join(self.days)}"