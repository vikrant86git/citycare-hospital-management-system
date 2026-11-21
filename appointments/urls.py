from django.urls import path
from . import views

urlpatterns = [
    path(
        "check-status/",
        views.check_appointment_status,
        name="check_appointment_status"
    ),
]