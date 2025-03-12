# appointments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.appointment_create, name='appointment_create'),
]
