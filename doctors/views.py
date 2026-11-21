from django.shortcuts import render
from django.db.models import Q
from .models import Doctor


def doctor_list(request):

    search_query = request.GET.get('search', '')

    doctors = Doctor.objects.all()

    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialization__icontains=search_query)
        )

    return render(
        request,
        'doctors.html',
        {
            'doctors': doctors,
            'search_query': search_query
        }
    )