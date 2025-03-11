# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Professional

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def professional_list(request):
    professionals = Professional.objects.all()
    return render(request, 'accounts/professional_list.html', {'professionals': professionals})

@login_required
def professional_create(request):
    return render(request, 'accounts/professional_form.html')

@login_required
def professional_detail(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    return render(request, 'accounts/professional_detail.html', {'professional': professional})

@login_required
def professional_edit(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    return render(request, 'accounts/professional_form.html', {'professional': professional})

@login_required
def professional_delete(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    return redirect('professional_list')

@login_required
def calendar_setup(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    return render(request, 'accounts/calendar_setup.html', {'professional': professional})