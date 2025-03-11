# services/models.py
from django.db import models
from accounts.models import Professional

class Service(models.Model):
    name = models.CharField('Nome', max_length=200)
    description = models.TextField('Descrição', blank=True, null=True)
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    duration = models.DurationField('Duração')
    professionals = models.ManyToManyField(
        Professional, 
        related_name='services',
        verbose_name='Profissionais'
    )
    is_active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['name']