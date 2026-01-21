from django.urls import path

from .views import (
    CampaignAttemptDetailView,
    CampaignAttemptListView,
    CampaignCreateView,
    CampaignDeleteView,
    CampaignDetailView,
    CampaignListView,
    CampaignUpdateView,
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
    MessageTemplateCreateView,
    MessageTemplateDeleteView,
    MessageTemplateDetailView,
    MessageTemplateListView,
    MessageTemplateUpdateView,
)

app_name = "campaigns"

urlpatterns = [
    # Клиенты
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("clients/create/", ClientCreateView.as_view(), name="client_create"),
    path("clients/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("clients/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    # Шаблоны рассылок
    path("message_templates/", MessageTemplateListView.as_view(), name="message_templates_list"),
    path("message_templates/create/", MessageTemplateCreateView.as_view(), name="message_template_create"),
    path("message_templates/<int:pk>/", MessageTemplateDetailView.as_view(), name="message_template_detail"),
    path("message_templates/<int:pk>/update/", MessageTemplateUpdateView.as_view(), name="message_template_update"),
    path("message_templates/<int:pk>/delete/", MessageTemplateDeleteView.as_view(), name="message_template_delete"),
    # Рассылки
    path("campaigns/", CampaignListView.as_view(), name="campaign_list"),
    path("campaigns/create/", CampaignCreateView.as_view(), name="campaign_create"),
    path("campaigns/<int:pk>/", CampaignDetailView.as_view(), name="campaign_detail"),
    path("campaigns/<int:pk>/update/", CampaignUpdateView.as_view(), name="campaign_update"),
    path("campaigns/<int:pk>/delete/", CampaignDeleteView.as_view(), name="campaign_delete"),
    # Попытки рассылки
    path("attempts/", CampaignAttemptListView.as_view(), name="attempt_list"),
    path("attempts/<int:pk>/", CampaignAttemptDetailView.as_view(), name="attempt_detail"),
]
