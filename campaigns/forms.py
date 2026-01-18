from django.core.exceptions import ValidationError
from django.forms import ModelForm

from campaigns.models import Client


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']