# communications/utils.py
from datetime import datetime, timedelta
import urllib.parse

def prepare_message_content(content, appointment):
    """
    Substitui shortcodes em um template de mensagem com dados reais do agendamento
    """
    if not content or not appointment:
        return ""
    
    # Data e hora formatadas
    date_formatted = appointment.date.strftime('%d/%m/%Y')
    time_formatted = appointment.start_time.strftime('%H:%M')
    end_time_formatted = appointment.end_time.strftime('%H:%M')
    
    # Obter informações do cliente, serviço e profissional
    client = appointment.client
    service = appointment.service
    professional = appointment.professional
    
    # Substituir shortcodes
    replacements = {
        '{nome}': client.name,
        '{telefone}': client.phone,
        '{email}': client.email or '',
        '{data}': date_formatted,
        '{hora}': time_formatted,
        '{hora_fim}': end_time_formatted,
        '{servico}': service.name,
        '{valor}': f"R$ {service.price:.2f}".replace('.', ','),
        '{duracao}': str(service.duration).split(':')[0] + 'h' + str(service.duration).split(':')[1] + 'min',
        '{profissional}': str(professional),
    }
    
    # Aplicar substituições
    for code, value in replacements.items():
        content = content.replace(code, str(value))
    
    return content

def get_deeplink_url(channel, destination, message=None, subject=None):
    """
    Gera URLs para abrir aplicativos nativos do dispositivo para envio de mensagens
    
    Args:
        channel: whatsapp, sms, email ou call
        destination: número de telefone ou e-mail
        message: conteúdo da mensagem (opcional)
        subject: assunto (apenas para e-mail)
    
    Returns:
        URL para abrir o aplicativo correspondente
    """
    if channel == 'whatsapp':
        # Remover caracteres não numéricos do telefone
        phone = ''.join(filter(str.isdigit, destination))
        
        # Assegurar que o número tem o formato internacional
        if not phone.startswith('55'):
            phone = '55' + phone
        
        # Codificar a mensagem para URL
        encoded_message = urllib.parse.quote(message or '')
        
        return f"https://api.whatsapp.com/send?phone={phone}&text={encoded_message}"
    
    elif channel == 'sms':
        # Formatar número de telefone
        phone = ''.join(filter(str.isdigit, destination))
        
        # Codificar a mensagem para URL
        encoded_message = urllib.parse.quote(message or '')
        
        return f"sms:{phone}?body={encoded_message}"
    
    elif channel == 'email':
        # Codificar assunto e corpo para URL
        encoded_subject = urllib.parse.quote(subject or '')
        encoded_message = urllib.parse.quote(message or '')
        
        return f"mailto:{destination}?subject={encoded_subject}&body={encoded_message}"
    
    elif channel == 'call':
        # Formatar número de telefone
        phone = ''.join(filter(str.isdigit, destination))
        
        return f"tel:{phone}"
    
    return "#"  # URL vazia para fallback

def schedule_reminders(appointment):
    """
    Agenda lembretes automáticos para um agendamento
    
    Args:
        appointment: instância do modelo Appointment
    """
    from .models import ReminderSettings, SentMessage
    from .tasks import send_reminder
    
    # Obter configurações de lembretes ativos
    reminder_settings = ReminderSettings.objects.filter(is_active=True)
    
    # Para cada configuração, agendar o envio do lembrete
    for setting in reminder_settings:
        reminder_date = appointment.date - timedelta(days=setting.days_before)
        
        # Só agendar se a data do lembrete for no futuro
        if reminder_date >= datetime.now().date():
            # Criar tarefa para envio do lembrete
            send_reminder.apply_async(
                args=[appointment.id, setting.template.id],
                eta=datetime.combine(reminder_date, datetime.strptime('10:00', '%H:%M').time())
            )