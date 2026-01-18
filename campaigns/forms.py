from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms

from campaigns.models import Client, MessageTemplate, Campaign


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']


class MessageTemplateForm(ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['subject', 'body']


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        fields = ['message_template', 'clients', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clients': forms.CheckboxSelectMultiple(),
        }