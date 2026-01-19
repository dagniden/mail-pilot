from django.urls import path
from . import views

app_name = "campaigns"

urlpatterns = [
    # Клиенты
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Шаблоны рассылок
    path('message_templates/', views.MessageTemplateListView.as_view(), name='message_templates_list'),
    path('message_templates/create/', views.MessageTemplateCreateView.as_view(), name='message_template_create'),
    path('message_templates/<int:pk>/', views.MessageTemplateDetailView.as_view(), name='message_template_detail'),
    path('message_templates/<int:pk>/update/', views.MessageTemplateUpdateView.as_view(), name='message_template_update'),
    path('message_templates/<int:pk>/delete/', views.MessageTemplateDeleteView.as_view(), name='message_template_delete'),

    # Рассылки
    path('campaigns/', views.CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign_detail'),
    path('campaigns/<int:pk>/update/', views.CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/<int:pk>/delete/', views.CampaignDeleteView.as_view(), name='campaign_delete'),
]
