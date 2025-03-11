# clients/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client
# Você precisará criar um formulário para Cliente

@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

@login_required
def client_create(request):
    # Implementação básica
    return render(request, 'clients/client_form.html')

@login_required
def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'clients/client_detail.html', {'client': client})

@login_required
def client_edit(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return render(request, 'clients/client_form.html', {'client': client})

@login_required
def client_delete(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    # Implementação básica
    return redirect('client_list')