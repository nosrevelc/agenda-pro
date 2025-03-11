# appointments/models.py
from django.db import models
from clients.models import Client
from services.models import Service
from accounts.models import Professional

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Agendado'),
        ('confirmed', 'Confirmado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
        ('no_show', 'Não compareceu'),
    ]
    
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Cliente'
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Serviço'
    )
    professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Profissional'
    )
    date = models.DateField('Data')
    start_time = models.TimeField('Hora de início')
    end_time = models.TimeField('Hora de término')
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.TextField('Observações', blank=True, null=True)
    google_event_id = models.CharField('ID do evento no Google', max_length=255, blank=True, null=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    def __str__(self):
        return f"{self.client.name} - {self.service.name} - {self.date} {self.start_time}"
    
    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-date', '-start_time']
        unique_together = [['professional', 'date', 'start_time']]