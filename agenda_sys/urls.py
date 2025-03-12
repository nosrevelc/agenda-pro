from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from accounts.views import dashboard, profile
from appointments.views import (
    appointment_list, appointment_create, appointment_edit, appointment_detail,
    appointment_cancel, appointment_send_message, get_template_content, 
    check_availability
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('', dashboard, name='dashboard'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/password-change-done/'
    ), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    
    # Apps URLs
    path('clients/', include('clients.urls')),
    path('services/', include('services.urls')),
    path('professionals/', include('accounts.urls')),
    path('messages/', include('communications.urls')),
    path('reports/', include('reports.urls')),
    
    # Appointments URLs
    path('appointments/', appointment_list, name='appointment_list'),  # Lista de agendamentos
    path('appointments/new/', appointment_create, name='appointment_create'),
    path('appointments/<int:appointment_id>/', appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/edit/', appointment_edit, name='appointment_edit'),
    path('appointments/<int:appointment_id>/cancel/', appointment_cancel, name='appointment_cancel'),
    path('appointments/<int:appointment_id>/send-message/', appointment_send_message, name='appointment_send_message'),
    path('appointments/<int:appointment_id>/send-message/<str:message_type>/', 
        appointment_send_message, name='appointment_send_message'),
    
    # API endpoints
    path('api/template-content/', get_template_content, name='get_template_content'),
    path('api/check-availability/', check_availability, name='check_availability'),
]

# Servir arquivos de mídia em ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
