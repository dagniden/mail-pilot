from django.db import models
from django.urls import reverse
from django.utils import timezone


class Client(models.Model):
    email = models.EmailField(unique=True, blank=False, verbose_name="Email", help_text="Введите email адрес")
    full_name = models.CharField(
        max_length=255,
        verbose_name="Полное имя получателя",
        help_text="Введите полное имя",
    )
    owner = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name="Владелец записи",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    comment = models.TextField(blank=True, verbose_name="Комментарий", help_text="Введите комментарий")

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [("can_view_all_recipients", "Can view all recipients")]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    def get_absolute_url(self):
        return reverse("campaigns:client_detail", kwargs={"pk": self.pk})


class MessageTemplate(models.Model):
    subject = models.CharField(
        max_length=255,
        blank=False,
        verbose_name="Тема письма",
        help_text="Введите тему письма",
    )
    body = models.TextField(blank=False, verbose_name="Тело письма", help_text="Введите тело письма")
    owner = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="templates",
        verbose_name="Владелец записи",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Шаблон сообщения"
        verbose_name_plural = "Шаблоны сообщений"
        ordering = ["-created_at"]
        permissions = [
            ("can_view_all_messages", "Can view all messages"),
        ]

    def __str__(self):
        return f"Шаблон письма #{self.id}: {self.subject}"

    def get_absolute_url(self):
        return reverse("campaigns:message_template_detail", kwargs={"pk": self.pk})


class Campaign(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Создана"
        IN_PROGRESS = "in_progress", "В процессе"
        FINISHED = "finished", "Завершена"

    message_template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.PROTECT,
        related_name="campaigns",
        verbose_name="Шаблон сообщения",
        help_text="Выберите шаблон сообщения",
    )
    clients = models.ManyToManyField(
        Client,
        related_name="campaigns",
        verbose_name="Клиенты",
        help_text="Выберите получателей рассылки",
    )
    owner = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="campaigns",
        verbose_name="Владелец записи",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=20, choices=Status, default=Status.CREATED)
    start_time = models.DateTimeField(
        blank=False,
        verbose_name="Время начала",
        help_text="Укажите дату и время начала рассылки",
    )
    end_time = models.DateTimeField(
        blank=False,
        verbose_name="Время окончания",
        help_text="Укажите дату и время окончания рассылки",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]
        permissions = [
            ("can_view_all_campaigns", "Can view all campaigns"),
            ("can_disable_campaign", "Can disable campaign"),
        ]

    def __str__(self):
        return f"Рассылка #{self.id}: {self.message_template.subject}"

    def update_status(self):
        current_time = timezone.now()

        if current_time < self.start_time:
            new_status = self.Status.CREATED
        elif current_time <= self.end_time:
            new_status = self.Status.IN_PROGRESS
        else:
            new_status = self.Status.FINISHED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=["status"])

    def can_be_sent(self):
        current_time = timezone.now()
        return self.start_time <= current_time <= self.end_time

    def get_absolute_url(self):
        return reverse("campaigns:campaign_detail", kwargs={"pk": self.pk})


class CampaignAttempt(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Успешно"
        FAILED = "failed", "Не успешно"

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ сервера SMTP")
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        related_name="attempts",
        verbose_name="Клиент",
    )
    status = models.CharField(max_length=20, choices=Status, default=Status.FAILED, verbose_name="Статус")
    attempt_number = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"

    def save(self, *args, **kwargs):
        if not self.pk:
            # Получаем последнюю CampaignAttempt для текущего клиента
            last_attempt = (
                CampaignAttempt.objects.filter(campaign=self.campaign, client=self.client)
                .order_by("-attempt_number")
                .first()
            )

            self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1

        super().save(*args, **kwargs)

    def __str__(self):
        campaign_info = f"{self.campaign.message_template.subject}" if self.campaign else "Удаленная рассылка"
        client_info = f"{self.client.full_name}" if self.client else "Удаленный клиент"
        return f"Попытка рассылки #{self.id} {campaign_info}: {client_info}"

    def get_absolute_url(self):
        return reverse("campaigns:attempt_detail", kwargs={"pk": self.pk})
