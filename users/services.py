from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

from .models import CustomUser


class EmailVerificationService:

    @staticmethod
    def send_verification(user: CustomUser, request):
        if user.is_verification_expired():
            user.regenerate_verification_code()

        verification_url = request.build_absolute_uri(
            reverse("users:verify_email", kwargs={"code": user.verification_code})
        )

        send_mail(
            subject="MailPilot - подтвердите ваш email",
            message=f"Перейдите по ссылке: {verification_url}\nСсылка действительна 24 часа.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        user.verification_sent_at = timezone.now()
        user.save(update_fields=["verification_sent_at"])
