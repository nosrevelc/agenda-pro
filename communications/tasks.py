# communications/tasks.py
from agenda_sys.celery import shared_task
from django.utils import timezone
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from agenda_sys.celery import shared_task
from datetime import datetime, timedelta

@shared_task
def send_reminder(appointment_id, template_id):
    """
    Tarefa para envio de lembretes automáticos
    
    Args:
        appointment_id: ID do agendamento
        template_id: ID do template de mensagem
    """
    from appointments.models import Appointment
    from .models import MessageTemplate, SentMessage
    from .utils import prepare_message_content
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        template = MessageTemplate.objects.get(id=template_id)
        
        # Verificar se o agendamento ainda está ativo
        if appointment.status not in ['scheduled', 'confirmed']:
            return
        
        # Preparar conteúdo da mensagem
        content = prepare_message_content(template.content, appointment)
        
        # Registrar mensagem enviada
        SentMessage.objects.create(
            appointment=appointment,
            template=template,
            channel=appointment.client.preferred_communication,
            content=content,
            sent_at=timezone.now()
        )
        
        # Aqui poderia ter integração com serviços externos de envio
        # No caso do sistema atual, apenas registramos a mensagem
        
        return True
    except (Appointment.DoesNotExist, MessageTemplate.DoesNotExist):
        return False
    

    @shared_task
def schedule_reminders_for_today():
    """
    Agenda lembretes para todos os agendamentos que precisam ser enviados hoje.
    Executado uma vez por dia pela configuração do Celery Beat.
    """
    from appointments.models import Appointment
    from communications.models import ReminderSettings, MessageTemplate
    
    today = timezone.now().date()
    
    # Obter todas as configurações de lembretes ativos
    reminder_settings = ReminderSettings.objects.filter(is_active=True)
    
    # Para cada configuração, enviar lembretes para agendamentos apropriados
    for setting in reminder_settings:
        # Calcular para qual data de agendamento devemos enviar lembretes hoje
        target_date = today + timedelta(days=setting.days_before)
        
        # Obter agendamentos para essa data que estão ativos
        appointments = Appointment.objects.filter(
            date=target_date,
            status__in=['scheduled', 'confirmed']
        )
        
        # Para cada agendamento, agendar o envio do lembrete
        for appointment in appointments:
            send_reminder.delay(appointment.id, setting.template.id)
    
    return f"Scheduled reminders for {today}"

@shared_task
def send_reminder(appointment_id, template_id):
    """
    Envia um lembrete para um agendamento específico
    
    Args:
        appointment_id: ID do agendamento
        template_id: ID do template de mensagem
    """
    from appointments.models import Appointment
    from communications.models import MessageTemplate, SentMessage
    from communications.utils import prepare_message_content
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        template = MessageTemplate.objects.get(id=template_id)
        
        # Verificar se o agendamento ainda está ativo
        if appointment.status not in ['scheduled', 'confirmed']:
            return f"Appointment {appointment_id} is not active anymore"
        
        # Preparar conteúdo da mensagem
        content = prepare_message_content(template.content, appointment)
        
        # Registrar mensagem enviada
        SentMessage.objects.create(
            appointment=appointment,
            template=template,
            channel=appointment.client.preferred_communication,
            content=content,
            sent_at=timezone.now()
        )
        
        # Aqui poderia ter integração com serviços externos de envio automático
        # No caso do sistema atual, apenas registramos a mensagem, que será enviada manualmente pelo operador
        
        return f"Reminder sent for appointment {appointment_id}"
    except (Appointment.DoesNotExist, MessageTemplate.DoesNotExist) as e:
        return f"Error sending reminder: {str(e)}"

@shared_task
def clean_old_messages(days=90):
    """
    Remove mensagens antigas do sistema
    
    Args:
        days: Número de dias para manter mensagens (padrão: 90)
    """
    from communications.models import SentMessage
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Contar mensagens antigas
    old_messages = SentMessage.objects.filter(sent_at__lt=cutoff_date)
    count = old_messages.count()
    
    # Excluir mensagens antigas
    old_messages.delete()
    
    return f"Deleted {count} old messages"