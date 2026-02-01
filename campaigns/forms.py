from django import forms
from django.forms import ModelForm

from campaigns.models import Campaign, Client, MessageTemplate


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]


class MessageTemplateForm(ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ["subject", "body"]


class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        fields = ["message_template", "clients", "start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "clients": forms.CheckboxSelectMultiple(),
        }
