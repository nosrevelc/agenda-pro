from django.shortcuts import render

# appointments/views.py
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

@login_required
@login_required
def appointment_list(request):
    # Filtragem por parâmetros
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    professional_filter = request.GET.get('professional', '')
    
    # Query base
    appointments = Appointment.objects.all()
    
    # Aplicar filtros
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(date=filter_date)
        except ValueError:
            pass
    
    if professional_filter:
        appointments = appointments.filter(professional_id=professional_filter)
    
    # Separar em agendamentos para hoje, futuros e passados
    today = timezone.now().date()
    
    # Agendamentos de hoje
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
        'today_appointments': today_appointments,  # Adicione esta linha
        'future_appointments': future_appointments,
        'past_appointments': past_appointments,
        'professionals': professionals,
        'status_choices': status_choices,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'professional_filter': professional_filter,
    }
    
    return render(request, 'appointments/appointment_list.html', context)
    # Filtragem por parâmetros
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    professional_filter = request.GET.get('professional', '')
    
    # Query base
    appointments = Appointment.objects.all()
    
    # Aplicar filtros
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(date=filter_date)
        except ValueError:
            pass
    
    if professional_filter:
        appointments = appointments.filter(professional_id=professional_filter)
    
    # Separar em agendamentos futuros e passados
    today = timezone.now().date()
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
            
            # Sugerir envio de mensagem de confirmação
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
    
    return render(request, 'appointments/appointment_form.html', context)

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
            
            # Se for um reagendamento, sugerir envio de mensagem
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
    
    # Disponibilizar templates de mensagem para envio rápido
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
            
            # Verificar número de faltas e atualizar lista negra se necessário
            no_shows_count = Appointment.objects.filter(
                client=appointment.client,
                status='no_show'
            ).count()
            
            if no_shows_count >= 3:  # Limite de faltas antes de ir para lista negra
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

@login_required
def appointment_send_message(request, appointment_id, message_type=None):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if message_type:
        # Obter template adequado para o tipo de mensagem
        try:
            template = MessageTemplate.objects.get(message_type=message_type, is_active=True)
            message_content = prepare_message_content(template.content, appointment)
        except MessageTemplate.DoesNotExist:
            template = None
            message_content = ""
    else:
        template = None
        message_content = ""
    
    if request.method == 'POST':
        template_id = request.POST.get('template')
        channel = request.POST.get('channel')
        content = request.POST.get('content')
        
        if template_id:
            try:
                selected_template = MessageTemplate.objects.get(id=template_id)
                template = selected_template
            except MessageTemplate.DoesNotExist:
                messages.error(request, 'Modelo de mensagem inválido.')
                return redirect('appointment_send_message', appointment_id=appointment_id)
        
        if not content:
            messages.error(request, 'O conteúdo da mensagem é obrigatório.')
            return redirect('appointment_send_message', appointment_id=appointment_id)
        
        # Criar registro de mensagem enviada
        sent_message = SentMessage.objects.create(
            appointment=appointment,
            template=template,
            channel=channel,
            content=content,
            sent_by=request.user
        )
        
        # Redirecionar para o link apropriado com base no canal selecionado
        if channel == 'whatsapp':
            url = get_deeplink_url('whatsapp', appointment.client.phone, content)
            return redirect(url)
        elif channel == 'sms':
            url = get_deeplink_url('sms', appointment.client.phone, content)
            return redirect(url)
        elif channel == 'email':
            url = get_deeplink_url('email', appointment.client.email, content, subject=f"Agendamento - {appointment.service.name}")
            return redirect(url)
        elif channel == 'call':
            url = get_deeplink_url('call', appointment.client.phone)
            return redirect(url)
        
        messages.success(request, 'Mensagem registrada com sucesso!')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    # Preparar opções de modelos de mensagem e canais de comunicação
    templates = MessageTemplate.objects.filter(is_active=True)
    
    # Determinar canais disponíveis com base nas informações do cliente
    channels = []
    if appointment.client.phone:
        channels.extend(['whatsapp', 'sms', 'call'])
    if appointment.client.email:
        channels.append('email')
    
    # Pré-selecionar o canal preferido do cliente
    preferred_channel = appointment.client.preferred_communication
    
    context = {
        'appointment': appointment,
        'templates': templates,
        'channels': channels,
        'selected_template': template,
        'message_content': message_content,
        'preferred_channel': preferred_channel,
    }
    
    return render(request, 'appointments/send_message.html', context)

@login_required
def get_template_content(request):
    """API para obter o conteúdo de um template processado para um agendamento"""
    template_id = request.GET.get('template_id')
    appointment_id = request.GET.get('appointment_id')
    
    if not template_id or not appointment_id:
        return JsonResponse({'error': 'Parâmetros incompletos'}, status=400)
    
    try:
        template = MessageTemplate.objects.get(id=template_id)
        appointment = Appointment.objects.get(id=appointment_id)
        
        content = prepare_message_content(template.content, appointment)
        
        return JsonResponse({'content': content})
    except (MessageTemplate.DoesNotExist, Appointment.DoesNotExist):
        return JsonResponse({'error': 'Dados não encontrados'}, status=404)

@login_required
def check_availability(request):
    """API para verificar disponibilidade de horários"""
    date = request.GET.get('date')
    professional_id = request.GET.get('professional_id')
    service_id = request.GET.get('service_id')
    appointment_id = request.GET.get('appointment_id')  # Para exclusão em caso de edição
    
    if not date or not professional_id or not service_id:
        return JsonResponse({'error': 'Parâmetros incompletos'}, status=400)
    
    try:
        date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        professional = Professional.objects.get(id=professional_id)
        service = Service.objects.get(id=service_id)
        
        # Obter agendamentos existentes para o dia
        existing_appointments = Appointment.objects.filter(
            professional=professional,
            date=date_obj,
            status__in=['scheduled', 'confirmed']
        )
        
        if appointment_id:
            existing_appointments = existing_appointments.exclude(id=appointment_id)
        
        # Criar lista de slots ocupados
        busy_slots = []
        for appointment in existing_appointments:
            busy_slots.append({
                'start': appointment.start_time.strftime('%H:%M'),
                'end': appointment.end_time.strftime('%H:%M'),
                'client': appointment.client.name,
                'service': appointment.service.name
            })
        
        # Duração do serviço
        service_duration = service.duration
        
        # Criar lista de horários disponíveis (das 8h às 18h, com intervalos de 30min)
        available_slots = []
        
        # Definir jornada de trabalho do profissional (padrão: 8h às 18h)
        work_start = datetime.strptime('08:00', '%H:%M').time()
        work_end = datetime.strptime('18:00', '%H:%M').time()
        
        current_time = datetime.combine(date_obj, work_start)
        end_time = datetime.combine(date_obj, work_end)
        
        # Verificar se a data é hoje e ajustar o horário inicial
        if date_obj == timezone.now().date():
            now = timezone.now()
            if now.time() > work_start:
                current_time = datetime.combine(date_obj, now.time())
                # Arredondar para o próximo slot de 30 minutos
                minutes_to_add = 30 - (current_time.minute % 30)
                current_time = current_time + timedelta(minutes=minutes_to_add)
        
        # Gerar slots de 30 minutos
        slot_interval = timedelta(minutes=30)
        
        while current_time + service_duration <= end_time:
            slot_start = current_time.time()
            slot_end = (current_time + service_duration).time()
            
            # Verificar se o slot está disponível
            is_available = True
            for busy in busy_slots:
                busy_start = datetime.strptime(busy['start'], '%H:%M').time()
                busy_end = datetime.strptime(busy['end'], '%H:%M').time()
                
                # Verificar sobreposição
                if (slot_start < busy_end and slot_end > busy_start):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append({
                    'start': slot_start.strftime('%H:%M'),
                    'end': slot_end.strftime('%H:%M')
                })
            
            current_time += slot_interval
        
        return JsonResponse({
            'busy_slots': busy_slots,
            'available_slots': available_slots,
            'service_duration': str(service_duration)
        })
    
    except ValueError:
        return JsonResponse({'error': 'Formato de data inválido'}, status=400)
    except Professional.DoesNotExist:
        return JsonResponse({'error': 'Profissional não encontrado'}, status=404)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Serviço não encontrado'}, status=404)
