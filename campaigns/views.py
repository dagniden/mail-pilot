from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from campaigns.forms import CampaignForm, ClientForm, MessageTemplateForm
from campaigns.models import Campaign, CampaignAttempt, Client, MessageTemplate
from campaigns.services import CampaignService


# Client CRUD views
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Client
    context_object_name = "client"

    def test_func(self):
        return self.get_object().owner == self.request.user


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Client
    form_class = ClientForm

    def test_func(self):
        return self.get_object().owner == self.request.user


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    success_url = reverse_lazy("campaigns:client_list")

    def test_func(self):
        return self.get_object().owner == self.request.user


# MessageTemplate CRUD view
class MessageTemplateListView(LoginRequiredMixin, ListView):
    model = MessageTemplate
    context_object_name = "message_templates"

    def get_queryset(self):
        return MessageTemplate.objects.filter(owner=self.request.user)


class MessageTemplateDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = MessageTemplate
    context_object_name = "message_template"

    def test_func(self):
        return self.get_object().owner == self.request.user


class MessageTemplateCreateView(LoginRequiredMixin, CreateView):
    model = MessageTemplate
    form_class = MessageTemplateForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageTemplateUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MessageTemplate
    form_class = MessageTemplateForm

    def test_func(self):
        return self.get_object().owner == self.request.user


class MessageTemplateDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MessageTemplate
    context_object_name = "message_template"
    success_url = reverse_lazy("campaigns:message_templates_list")

    def test_func(self):
        return self.get_object().owner == self.request.user


# Campaign CRUD Views
class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    context_object_name = "campaigns"

    def get_queryset(self):
        return Campaign.objects.filter(owner=self.request.user)


class CampaignDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
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
        return redirect("campaigns:campaign_detail", pk=campaign.pk)

    def test_func(self):
        return self.get_object().owner == self.request.user


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm

    def test_func(self):
        return self.get_object().owner == self.request.user


class CampaignDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Campaign
    success_url = reverse_lazy("campaigns:campaign_list")

    def test_func(self):
        return self.get_object().owner == self.request.user


# CampaignAttempt read only views
class CampaignAttemptListView(LoginRequiredMixin, ListView):
    model = CampaignAttempt
    context_object_name = "attempts"

    def get_queryset(self):
        queryset = super().get_queryset()
        campaign_id = self.request.GET.get("campaign_id")
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset.select_related("campaign", "client").order_by("-attempt_time")


class CampaignAttemptDetailView(LoginRequiredMixin, DetailView):
    model = CampaignAttempt
    context_object_name = "attempt"
