from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import Patient


def is_staff_user(user):
    print("Username:", user.username)
    print("Authenticated:", user.is_authenticated)
    print("Staff:", user.is_staff)

    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user, login_url='/admin/login/')
def patient_list(request):

    search_query = request.GET.get('search', '')

    patients = Patient.objects.all()

    if search_query:
        patients = patients.filter(name__icontains=search_query)

    return render(
        request,
        'patients.html',
        {
            'patients': patients,
            'search_query': search_query
        }
    )