from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service

@login_required
def service_list(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services})

@login_required
def service_create(request):
    return render(request, 'services/service_form.html')

@login_required
def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/service_detail.html', {'service': service})

@login_required
def service_edit(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/service_form.html', {'service': service})

@login_required
def service_delete(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return redirect('service_list')