from django.contrib import admin

from campaigns.models import Campaign, Client, MessageTemplate


# Register your models here.
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    pass


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    pass