# communications/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MessageTemplate, SentMessage, ReminderSettings

@login_required
def message_template_list(request):
    templates = MessageTemplate.objects.all()
    return render(request, 'communications/template_list.html', {'templates': templates})

@login_required
def message_template_create(request):
    return render(request, 'communications/template_form.html')

@login_required
def message_template_detail(request, template_id):
    template = get_object_or_404(MessageTemplate, id=template_id)
    return render(request, 'communications/template_detail.html', {'template': template})

@login_required
def message_template_edit(request, template_id):
    template = get_object_or_404(MessageTemplate, id=template_id)
    return render(request, 'communications/template_form.html', {'template': template})

@login_required
def message_template_delete(request, template_id):
    template = get_object_or_404(MessageTemplate, id=template_id)
    return redirect('message_template_list')

@login_required
def message_history(request):
    messages = SentMessage.objects.all().order_by('-sent_at')
    return render(request, 'communications/message_history.html', {'messages': messages})

@login_required
def reminder_settings(request):
    settings = ReminderSettings.objects.all()
    return render(request, 'communications/reminder_settings.html', {'settings': settings})