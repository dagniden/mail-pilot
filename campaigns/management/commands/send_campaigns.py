from django.core.management.base import BaseCommand

from campaigns.models import Campaign
from campaigns.services import CampaignService


class Command(BaseCommand):
    help = "Отправляет все активные кампании в пределах временного окна"

    def handle(self, *args, **options):

        active_campaigns = Campaign.objects.all()
        statistics = {"sent": 0, "skipped": 0}

        for campaign in active_campaigns:
            if not campaign.can_be_sent():
                statistics["skipped"] += 1
                continue

            result = CampaignService.send_campaign(campaign)
            statistics["sent" if result else "skipped"] += 1

        self.stdout.write(self.style.SUCCESS("Command finished"))
        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {statistics['sent']} campaigns, failed to send {statistics['skipped']} campaigns"
            )
        )
