# agenda_sys/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agenda_sys.settings')

app = Celery('agenda_sys')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Add periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Send reminders every day at 10:00 AM
    'send-daily-reminders': {
        'task': 'communications.tasks.schedule_reminders_for_today',
        'schedule': crontab(hour=10, minute=0),
    },
    # Clean old messages every Sunday at midnight
    'clean-old-messages': {
        'task': 'communications.tasks.clean_old_messages',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),
    },
}