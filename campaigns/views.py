from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from campaigns.forms import ClientForm, MessageTemplateForm, CampaignForm
from campaigns.models import Client, MessageTemplate, Campaign
from campaigns.services import CampaignService


class ClientListView(ListView):
    model = Client
    context_object_name = "clients"


class ClientDetailView(DetailView):
    model = Client
    context_object_name = "client"


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('campaigns:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('campaigns:client_list')


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('campaigns:client_list')


class MessageTemplateListView(ListView):
    model = MessageTemplate
    context_object_name = "message_templates"


class MessageTemplateDetailView(DetailView):
    model = MessageTemplate
    context_object_name = "message_template"


class MessageTemplateCreateView(CreateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    success_url = reverse_lazy('campaigns:message_templates_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageTemplateUpdateView(UpdateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    success_url = reverse_lazy('campaigns:message_templates_list')


class MessageTemplateDeleteView(DeleteView):
    model = MessageTemplate
    context_object_name = "message_template"
    success_url = reverse_lazy('campaigns:message_templates_list')


# Campaign CRUD Views
class CampaignListView(ListView):
    model = Campaign
    context_object_name = "campaigns"


class CampaignDetailView(DetailView):
    model = Campaign
    context_object_name = "campaign"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def post(self, request, *args, **kwargs):
        campaign = self.get_object()
        if "send_campaign" in request.POST:
            CampaignService.send_campaign(campaign)
        return redirect('campaigns:campaign_detail', pk=campaign.pk)



class CampaignCreateView(CreateView):
    model = Campaign
    form_class = CampaignForm
    success_url = reverse_lazy('campaigns:campaign_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CampaignUpdateView(UpdateView):
    model = Campaign
    form_class = CampaignForm
    success_url = reverse_lazy('campaigns:campaign_list')


class CampaignDeleteView(DeleteView):
    model = Campaign
    success_url = reverse_lazy('campaigns:campaign_list')