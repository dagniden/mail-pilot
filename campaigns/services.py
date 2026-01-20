from campaigns.models import Campaign, CampaignAttempt
from django.core.mail import send_mail

from config import settings


class CampaignService:

    @staticmethod
    def send_campaign(campaign: Campaign) -> bool:
        """
        Отправляет кампанию всем клиентам.
        Создает CampaignAttempt для каждого клиента.

        Returns:
            bool: True если кампания была отправлена, False если вне временного окна
        """
        if not campaign.can_be_sent():
            return False

        for client in campaign.clients.all():
            try:
                send_mail(
                    subject=campaign.message_template.subject,
                    message=campaign.message_template.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False
                )
                CampaignAttempt.objects.create(
                    campaign=campaign,
                    client=client,
                    status=CampaignAttempt.Status.SUCCESS,
                    server_response='Email sent successfully'
                )
            except Exception as e:
                CampaignAttempt.objects.create(
                    campaign=campaign,
                    client=client,
                    status=CampaignAttempt.Status.FAILED,
                    server_response=f'SMTP error: {str(e)}'
                )

        return True
