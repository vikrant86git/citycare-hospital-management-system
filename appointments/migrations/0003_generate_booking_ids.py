import uuid
from django.db import migrations


def generate_booking_ids(apps, schema_editor):
    Appointment = apps.get_model('appointments', 'Appointment')

    for appointment in Appointment.objects.filter(booking_id__isnull=True):
        appointment.booking_id = uuid.uuid4()
        appointment.save(update_fields=['booking_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_appointment_booking_id'),
    ]

    operations = [
        migrations.RunPython(generate_booking_ids),
    ]