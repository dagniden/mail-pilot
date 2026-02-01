from django.contrib import admin

from campaigns.models import Campaign, CampaignAttempt, Client, MessageTemplate


# Register your models here.
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["id", "message_template", "status", "owner", "start_time", "end_time"]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "email", "owner"]


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "subject", "owner"]


@admin.register(CampaignAttempt)
class CampaignAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "attempt_time", "attempt_number", "status", "campaign", "client"]
