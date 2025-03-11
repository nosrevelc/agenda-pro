 # accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Professional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional_profile')
    specialty = models.CharField('Especialidade', max_length=100)
    bio = models.TextField('Biografia', blank=True, null=True)
    google_calendar_id = models.CharField('ID do Google Calendar', max_length=255, blank=True, null=True)
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'
        ordering = ['user__first_name', 'user__last_name']       
