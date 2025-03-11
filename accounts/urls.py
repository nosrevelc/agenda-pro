# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.professional_list, name='professional_list'),
    path('new/', views.professional_create, name='professional_create'),
    path('<int:professional_id>/', views.professional_detail, name='professional_detail'),
    path('<int:professional_id>/edit/', views.professional_edit, name='professional_edit'),
    path('<int:professional_id>/delete/', views.professional_delete, name='professional_delete'),
    path('<int:professional_id>/calendar-setup/', views.calendar_setup, name='calendar_setup'),
]