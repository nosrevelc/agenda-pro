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
        self.fields['client'].queryset = Client.objects.filter(is_blacklisted=False)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        self.fields['professional'].queryset = Professional.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        service = cleaned_data.get('service')
        professional = cleaned_data.get('professional')
        
        if date and start_time and service and professional:
            if date < timezone.now().date():
                raise forms.ValidationError("Não é possível agendar para uma data no passado.")
            
            # Verificação do horário de início
            current_time = timezone.now().time()
            if date == timezone.now().date() and start_time < current_time:
                raise forms.ValidationError("Não é possível agendar para um horário no passado.")
            
            # Calcular o horário de término do serviço
            duration_seconds = service.duration.total_seconds()
            duration_hours = int(duration_seconds // 3600)
            duration_minutes = int((duration_seconds % 3600) // 60)
            start_datetime = datetime.combine(date, start_time)
            end_datetime = start_datetime + timedelta(hours=duration_hours, minutes=duration_minutes)
            end_time = end_datetime.time()
            cleaned_data['end_time'] = end_time
            
            # Verificar conflitos de agendamento
            conflicting_appointments = Appointment.objects.filter(
                professional=professional,
                date=date,
                status__in=['scheduled', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for appointment in conflicting_appointments:
                if (start_time < appointment.end_time and end_time > appointment.start_time):
                    raise forms.ValidationError(
                        f"O profissional já possui um agendamento conflitante das {appointment.start_time.strftime('%H:%M')} "
                        f"às {appointment.end_time.strftime('%H:%M')}."
                    )
            
            # Verificar se o profissional realiza o serviço
            if not service.professionals.filter(id=professional.id).exists():
                raise forms.ValidationError(
                    f"O profissional {professional} não realiza o serviço {service}."
                )
        
        return cleaned_data
