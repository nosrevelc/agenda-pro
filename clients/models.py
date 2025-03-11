# clients/models.py
from django.db import models
from django.core.validators import RegexValidator

class Client(models.Model):
    COMMUNICATION_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'E-mail'),
        ('call', 'Ligação'),
    ]
    
    name = models.CharField('Nome', max_length=200)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="O número de telefone deve estar no formato: '+999999999'. Até 15 dígitos permitidos."
    )
    phone = models.CharField('Telefone', validators=[phone_regex], max_length=17)
    email = models.EmailField('E-mail', blank=True, null=True)
    preferred_communication = models.CharField(
        'Meio de comunicação preferido',
        max_length=10,
        choices=COMMUNICATION_CHOICES,
        default='whatsapp'
    )
    is_blacklisted = models.BooleanField('Lista negra', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']


