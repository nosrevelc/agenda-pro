# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('services/', views.services_report, name='services_report'),
    path('clients/', views.clients_report, name='clients_report'),
    path('export/csv/<str:report_type>/', views.export_csv, name='export_csv'),
    path('export/pdf/<str:report_type>/', views.export_pdf, name='export_pdf'),
]