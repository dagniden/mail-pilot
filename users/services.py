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

        email_body = f"""
Добро пожаловать в Mail Pilot!

Для завершения регистрации подтвердите ваш email-адрес, перейдя по ссылке:

{verification_url}

Ссылка действительна в течение 24 часов.

Если вы не регистрировались на Mail Pilot, просто проигнорируйте это письмо.

---
С уважением,
Команда Mail Pilot
        """

        send_mail(
            subject="Mail Pilot - подтвердите ваш email",
            message=email_body.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        user.verification_sent_at = timezone.now()
        user.save(update_fields=["verification_sent_at"])
