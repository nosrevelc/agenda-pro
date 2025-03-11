# communications/models.py
from django.db import models
from appointments.models import Appointment

class MessageTemplate(models.Model):
    TYPE_CHOICES = [
        ('confirmation', 'Confirmação de Agendamento'),
        ('reminder', 'Lembrete'),
        ('thank_you', 'Agradecimento'),
        ('custom', 'Personalizada'),
    ]
    
    name = models.CharField('Nome', max_length=100)
    message_type = models.CharField(
        'Tipo de mensagem',
        max_length=20,
        choices=TYPE_CHOICES,
        default='custom'
    )
    content = models.TextField('Conteúdo')
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Modelo de mensagem'
        verbose_name_plural = 'Modelos de mensagens'

class SentMessage(models.Model):
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'E-mail'),
        ('call', 'Ligação'),
    ]
    
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Agendamento'
    )
    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.SET_NULL,
        related_name='sent_messages',
        verbose_name='Modelo de mensagem',
        null=True,
        blank=True
    )
    channel = models.CharField(
        'Canal',
        max_length=10,
        choices=CHANNEL_CHOICES
    )
    content = models.TextField('Conteúdo')
    sent_at = models.DateTimeField('Enviado em', auto_now_add=True)
    sent_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        related_name='sent_messages',
        verbose_name='Enviado por',
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.appointment.client.name} - {self.channel} - {self.sent_at}"
    
    class Meta:
        verbose_name = 'Mensagem enviada'
        verbose_name_plural = 'Mensagens enviadas'
        ordering = ['-sent_at']

 # Reminder settings model
class ReminderSettings(models.Model):
    DAYS_CHOICES = [
        (1, '1 dia antes'),
        (2, '2 dias antes'),
        (3, '3 dias antes'),
    ]
    
    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.CASCADE,
        related_name='reminder_settings',
        verbose_name='Modelo de mensagem'
    )
    days_before = models.IntegerField(
        'Dias antes',
        choices=DAYS_CHOICES,
        default=1
    )
    is_active = models.BooleanField('Ativo', default=True)
    
    def __str__(self):
        return f"{self.template.name} - {self.days_before} dias antes"
    
    class Meta:
        verbose_name = 'Configuração de lembrete'
        verbose_name_plural = 'Configurações de lembretes'
        unique_together = [['template', 'days_before']]       