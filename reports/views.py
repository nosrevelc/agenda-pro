# reports/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from appointments.models import Appointment
from clients.models import Client
from services.models import Service

@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html')

@login_required
def attendance_report(request):
    return render(request, 'reports/attendance_report.html')

@login_required
def services_report(request):
    return render(request, 'reports/services_report.html')

@login_required
def clients_report(request):
    return render(request, 'reports/clients_report.html')

@login_required
def export_csv(request, report_type):
    # Implementação básica para exportação CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
    return response

@login_required
def export_pdf(request, report_type):
    # Implementação básica para exportação PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    return response