# google_calendar/utils.py
import os
import pickle
import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings

# Escopo para acesso ao Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service(professional=None):
    """
    Obtém serviço autenticado para acesso à API do Google Calendar
    
    Args:
        professional: instância do modelo Professional (opcional)
    
    Returns:
        Serviço autenticado do Google Calendar
    """
    credentials = None
    token_path = os.path.join(settings.BASE_DIR, 'credentials', 'token.pickle')
    
    # Se um profissional específico for fornecido, usar seu token específico
    if professional and professional.google_token_file:
        token_path = professional.google_token_file
    
    # Carregar credenciais armazenadas
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)
    
    # Se não houver credenciais válidas, solicitar login
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # Arquivo de credenciais da API do Google
            credentials_path = os.path.join(settings.BASE_DIR, 'credentials', 'credentials.json')
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            credentials = flow.run_local_server(port=0)
            
            # Salvar as credenciais
            if not os.path.exists(os.path.dirname(token_path)):
                os.makedirs(os.path.dirname(token_path))
                
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)
    
    # Construir serviço
    service = build('calendar', 'v3', credentials=credentials)
    return service

def sync_appointment_to_calendar(appointment):
    """
    Sincroniza um agendamento com o Google Calendar
    
    Args:
        appointment: instância do modelo Appointment
    
    Returns:
        ID do evento criado/atualizado no Google Calendar, ou None em caso de erro
    """
    from appointments.models import Appointment
    
    if not isinstance(appointment, Appointment):
        return None
    
    # Verificar se o profissional tem ID do Google Calendar configurado
    professional = appointment.professional
    if not professional.google_calendar_id:
        return None
    
    try:
        # Obter serviço do Google Calendar
        service = get_calendar_service(professional)
        
        # Preparar dados do evento
        start_datetime = datetime.datetime.combine(appointment.date, appointment.start_time)
        end_datetime = datetime.datetime.combine(appointment.date, appointment.end_time)
        
        event = {
            'summary': f"{appointment.service.name} - {appointment.client.name}",
            'location': settings.COMPANY_ADDRESS,
            'description': appointment.notes or '',
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'reminders': {
                'useDefault': True,
            },
        }
        
        # Verificar se é uma atualização ou criação
        if appointment.google_event_id:
            # Atualizar evento existente
            updated_event = service.events().update(
                calendarId=professional.google_calendar_id,
                eventId=appointment.google_event_id,
                body=event
            ).execute()
            
            return updated_event['id']
        else:
            # Criar novo evento
            created_event = service.events().insert(
                calendarId=professional.google_calendar_id,
                body=event
            ).execute()
            
            # Atualizar o agendamento com o ID do evento
            appointment.google_event_id = created_event['id']
            appointment.save(update_fields=['google_event_id'])
            
            return created_event['id']
    
    except Exception as e:
        # Registrar erro em log
        print(f"Erro ao sincronizar com Google Calendar: {str(e)}")
        return None

def delete_calendar_event(appointment):
    """
    Exclui um evento do Google Calendar
    
    Args:
        appointment: instância do modelo Appointment
    
    Returns:
        True se excluído com sucesso, False caso contrário
    """
    if not appointment.google_event_id or not appointment.professional.google_calendar_id:
        return False
    
    try:
        # Obter serviço do Google Calendar
        service = get_calendar_service(appointment.professional)
        
        # Excluir evento
        service.events().delete(
            calendarId=appointment.professional.google_calendar_id,
            eventId=appointment.google_event_id
        ).execute()
        
        # Limpar ID do evento no agendamento
        appointment.google_event_id = None
        appointment.save(update_fields=['google_event_id'])
        
        return True
    
    except HttpError as e:
        # Verificar se o erro é "Evento não encontrado" (410)
        if e.resp.status == 410:
            # O evento já foi excluído, limpar o ID
            appointment.google_event_id = None
            appointment.save(update_fields=['google_event_id'])
            return True
        
        print(f"Erro ao excluir evento do Google Calendar: {str(e)}")
        return False
    
    except Exception as e:
        print(f"Erro ao excluir evento do Google Calendar: {str(e)}")
        return False