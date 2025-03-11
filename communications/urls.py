# communications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.message_template_list, name='message_template_list'),
    path('templates/new/', views.message_template_create, name='message_template_create'),
    path('templates/<int:template_id>/', views.message_template_detail, name='message_template_detail'),
    path('templates/<int:template_id>/edit/', views.message_template_edit, name='message_template_edit'),
    path('templates/<int:template_id>/delete/', views.message_template_delete, name='message_template_delete'),
    path('history/', views.message_history, name='message_history'),
    path('reminders/', views.reminder_settings, name='reminder_settings'),
]