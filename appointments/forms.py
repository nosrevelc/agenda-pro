# appointments/forms.py
from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from clients.models import Client
from services.models import Service
from accounts.models import Professional

class AppointmentForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data',
        initial=timezone.now().date
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Hora de início'
    )
    
    class Meta:
        model = Appointment
        fields = ['client', 'service', 'professional', 'date', 'start_time', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrando apenas clientes ativos (não na lista negra)
        self.fields['client'].queryset = Client.objects.filter(is_blacklisted=False)
        
        # Filtrando apenas serviços ativos
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        
        # Filtrando apenas profissionais ativos
        self.fields['professional'].queryset = Professional.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        service = cleaned_data.get('service')
        professional = cleaned_data.get('professional')
        
        if date and start_time and service and professional:
            # Verificar se a data não é no passado
            if date < timezone.now().date():
                raise forms.ValidationError("Não é possível agendar para uma data no passado.")
            
            # Calcular hora de término com base na duração do serviço
            duration_seconds = service.duration.total_seconds()
            duration_hours = int(duration_seconds // 3600)
            duration_minutes = int((duration_seconds % 3600) // 60)
            
            start_datetime = datetime.combine(date, start_time)
            end_datetime = start_datetime + timedelta(hours=duration_hours, minutes=duration_minutes)
            end_time = end_datetime.time()
            
            # Adicionar hora de término ao cleaned_data
            cleaned_data['end_time'] = end_time
            
            # Verificar se o profissional está disponível nesse horário
            conflicting_appointments = Appointment.objects.filter(
                professional=professional,
                date=date,
                status__in=['scheduled', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for appointment in conflicting_appointments:
                # Verificar se há sobreposição de horários
                if (start_time < appointment.end_time and end_time > appointment.start_time):
                    raise forms.ValidationError(
                        f"O profissional já possui um agendamento conflitante das "
                        f"{appointment.start_time.strftime('%H:%M')} às "
                        f"{appointment.end_time.strftime('%H:%M')}."
                    )
                    
            # Verificar se o serviço pode ser realizado pelo profissional
            if professional not in service.professionals.all():
                raise forms.ValidationError(
                    f"O profissional {professional} não realiza o serviço {service}."
                )
        
        return cleaned_data