from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from campaigns.forms import ClientForm
from campaigns.models import Client


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