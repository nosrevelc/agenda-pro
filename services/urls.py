# services/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('new/', views.service_create, name='service_create'),
    path('<int:service_id>/', views.service_detail, name='service_detail'),
    path('<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('<int:service_id>/delete/', views.service_delete, name='service_delete'),
]