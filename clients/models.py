# clients/models.py
from django.db import models
import phonenumbers
from django.core.exceptions import ValidationError

class Client(models.Model):
    COMMUNICATION_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'E-mail'),
        ('call', 'Ligação'),
    ]
    
    @staticmethod  # Adicione este decorador
    def validate_phone_number(value):
        """
        Valida números de telefone internacionais
        """
        try:
            # Tenta parsear o número com código do país
            parsed_number = phonenumbers.parse(value, None)
            
            # Verifica se é um número válido
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError('Número de telefone inválido')
        
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValidationError('Formato de número de telefone inválido')

    name = models.CharField('Nome', max_length=200)
    phone = models.CharField(
        'Telefone', 
        max_length=20, 
        validators=[validate_phone_number]
    )
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