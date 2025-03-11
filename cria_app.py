import os

# Lista de aplicações a serem criadas
apps = [
    'accounts',
    'clients',
    'services',
    'appointments',
    'communications',
    'reports'
]

for app in apps:
    os.system(f'python manage.py startapp {app}')