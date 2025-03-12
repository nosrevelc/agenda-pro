from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from datetime import timedelta
from .models import Appointment
from .forms import AppointmentForm
from clients.models import Client
from services.models import Service
from accounts.models import Professional
from communications.models import MessageTemplate, SentMessage
from communications.utils import prepare_message_content, get_deeplink_url

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_list(request):
    # Filtragem por parâmetros
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    professional_filter = request.GET.get('professional', '')
    
    # Consulta base
    appointments = Appointment.objects.all()
    
    # Aplicar filtros
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            filtered_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(date=filtered_date)
        except ValueError:
            pass
    
    if professional_filter:
        appointments = appointments.filter(professional_id=professional_filter)
    
    # Separar em agendamentos de hoje, futuros e passados
    today = timezone.now().date()
    
    today_appointments = appointments.filter(date=today).order_by('start_time')
    
    future_appointments = appointments.filter(
        Q(date__gt=today) | Q(date=today, start_time__gt=timezone.now().time())
    ).order_by('date', 'start_time')
    
    past_appointments = appointments.filter(
        Q(date__lt=today) | Q(date=today, start_time__lte=timezone.now().time())
    ).order_by('-date', '-start_time')
    
    # Dados para filtros
    professionals = Professional.objects.filter(is_active=True)
    status_choices = Appointment.STATUS_CHOICES
    
    context = {
        'today_appointments': today_appointments,  
        'future_appointments': future_appointments,
        'past_appointments': past_appointments,
        'professionals': professionals,
        'status_choices': status_choices,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'professional_filter': professional_filter,
    }
    
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.end_time = form.cleaned_data['end_time']
            appointment.save()
            
            messages.success(request, 'Agendamento criado com sucesso!')
            
            return redirect('appointment_send_message', appointment_id=appointment.id, message_type='confirmation')
        else:
            messages.error(request, 'Erro ao criar agendamento. Verifique os dados informados.')
    else:
        # Pré-selecionar data/hora a partir dos parâmetros da URL
        initial_data = {}
        date_param = request.GET.get('date')
        time_param = request.GET.get('time')
        professional_param = request.GET.get('professional')
        client_param = request.GET.get('client')
        service_param = request.GET.get('service')
        
        if date_param:
            try:
                initial_data['date'] = timezone.datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if time_param:
            try:
                initial_data['start_time'] = timezone.datetime.strptime(time_param, '%H:%M').time()
            except ValueError:
                pass
        
        if professional_param:
            try:
                initial_data['professional'] = int(professional_param)
            except ValueError:
                pass
        
        if client_param:
            try:
                initial_data['client'] = int(client_param)
            except ValueError:
                pass
        
        if service_param:
            try:
                initial_data['service'] = int(service_param)
            except ValueError:
                pass
        
        form = AppointmentForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Novo Agendamento',
    }
    
    return render(request, 'appointments/create.html', context)

@login_required
def appointment_edit(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            updated_appointment.end_time = form.cleaned_data['end_time']
            updated_appointment.save()
            
            messages.success(request, 'Agendamento atualizado com sucesso!')
            
            if (appointment.date != updated_appointment.date or 
                appointment.start_time != updated_appointment.start_time):
                return redirect('appointment_send_message', appointment_id=appointment.id, message_type='reschedule')
            
            return redirect('appointment_detail', appointment_id=appointment.id)
        else:
            messages.error(request, 'Erro ao atualizar agendamento. Verifique os dados informados.')
    else:
        form = AppointmentForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
        'title': 'Editar Agendamento',
    }
    
    return render(request, 'appointments/appointment_form.html', context)

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    sent_messages = appointment.sent_messages.all().order_by('-sent_at')
    
    message_templates = MessageTemplate.objects.filter(is_active=True)
    
    context = {
        'appointment': appointment,
        'sent_messages': sent_messages,
        'message_templates': message_templates,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def appointment_cancel(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        no_show = request.POST.get('no_show', False)
        
        if no_show:
            appointment.status = 'no_show'
            
            no_show_count = Appointment.objects.filter(
                client=appointment.client,
                status='no_show'
            ).count()
            
            if no_show_count >= 3:
                appointment.client.is_blacklisted = True
                appointment.client.save()
                messages.warning(
                    request, 
                    f'O cliente {appointment.client.name} foi adicionado à lista negra devido a múltiplas faltas.'
                )
        else:
            appointment.status = 'cancelled'
        
        if reason:
            appointment.notes = f"{appointment.notes or ''}\n\nCancelamento: {reason}".strip()
        
        appointment.save()
        
        messages.success(request, 'Agendamento cancelado com sucesso!')
        return redirect('appointment_list')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/appointment_cancel.html', context)


# Função para enviar mensagem sobre um agendamento
def appointment_send_message(request, appointment_id, message_type=None):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Lógica para enviar a mensagem relacionada ao tipo
    # Exemplo: Se for um tipo de mensagem específico, trate isso aqui
    if message_type == 'confirmation':
        # Enviar confirmação, por exemplo
        message = "Your appointment has been confirmed!"
    elif message_type == 'reminder':
        # Enviar lembrete
        message = "Reminder: Your appointment is coming up!"
    else:
        # Mensagem padrão
        message = "Message sent regarding your appointment."
    
    # Aqui você pode adicionar lógica de envio, como e-mail ou SMS
    return JsonResponse({'status': 'success', 'message': message})

# Função para obter conteúdo de template
def get_template_content(request):
    # Aqui você pode buscar algum conteúdo específico para templates, dependendo da sua lógica de negócio
    template_content = {
        'title': 'My Template Content',
        'body': 'This is the content of your template.'
    }
    return JsonResponse(template_content)

# Função para verificar disponibilidade de agendamento
def check_availability(request):
    # Aqui você pode verificar se existem horários disponíveis para agendamento
    available_times = ['09:00', '10:00', '11:00', '14:00', '15:00']  # Exemplo fixo, pode ser dinâmico
    return JsonResponse({'status': 'success', 'available_times': available_times})
