from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

NOTIFICATION_TYPES = [
        ('INFO', 'Информационное'),
        ('WARNING', 'Предупреждение'),
        ('ERROR', 'Ошибка'),
        ('SUCCESS', 'Успех'),
    ]

DELIVERY_METHODS = [
        ('EMAIL', 'Email'),
        ('TELEGRAM', 'Telegram'),
        ('SMS', 'SMS'),
    ]
STATUS_CHOICES = [
        ('PENDING', 'В ожидании'),
        ('SENT', 'Отправлено'),
        ('FAILED', 'Не удалось'),
        ('RETRY', 'Повторная попытка'),
    ]


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='INFO')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(default=timezone.now)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class DeliveryAttempt(models.Model):
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE,
        related_name='delivery_attempts'
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHODS
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='PENDING')
    attempt_number = models.PositiveIntegerField(default=1)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['attempt_number']


class UserNotificationSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='notification_settings')
    email = models.EmailField(blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    email_enabled = models.BooleanField(default=True)
    telegram_enabled = models.BooleanField(default=False)
    sms_enabled = models.BooleanField(default=False)

    def get_available_methods(self):
        methods = []
        if self.email_enabled and self.email:
            methods.append('EMAIL')
        if self.telegram_enabled and self.telegram_chat_id:
            methods.append('TELEGRAM')
        if self.sms_enabled and self.phone_number:
            methods.append('SMS')
        return methods
