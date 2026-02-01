import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)
    is_email_verified = models.BooleanField(default=False)
    verification_sent_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email

    def regenerate_verification_code(self):
        self.verification_code = uuid.uuid4()
        self.verification_sent_at = timezone.now()
        self.save(update_fields=["verification_code", "verification_sent_at"])

    def is_verification_expired(self):
        if not self.verification_sent_at:
            return True
        return timezone.now() > self.verification_sent_at + timedelta(days=1)

    def get_absolute_url(self):
        return reverse("users:user_detail", kwargs={"pk": self.pk})
