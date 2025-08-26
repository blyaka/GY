from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message="Телефон должен быть в формате +79991234567 (10–15 цифр)."
)

class Request(models.Model):
    full_name = models.CharField("ФИО", max_length=150)
    email = models.EmailField("Email", blank=True, validators=[EmailValidator()])
    phone = models.CharField("Телефон", max_length=16, blank=True, validators=[phone_validator])
    created_at = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True, editable=False)
    user_agent = models.TextField(blank=True, editable=False)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def clean(self):
        if not self.email and not self.phone:
            raise ValidationError("Нужно указать телефон или email.")

    def __str__(self):
        return f"{self.full_name} [{self.email or self.phone or '—'}]"

class TelegramBot(models.Model):
    name = models.CharField("Название", max_length=100, default="Основной бот")
    token = models.CharField("Bot Token", max_length=120)
    enabled = models.BooleanField("Включен", default=True)

    class Meta:
        verbose_name = "Telegram бот"
        verbose_name_plural = "Telegram боты"

    def __str__(self):
        return f"{self.name} ({'on' if self.enabled else 'off'})"

class TelegramRecipient(models.Model):
    title = models.CharField("Название чата/пользователя", max_length=150, blank=True)
    chat_id = models.BigIntegerField("Chat ID", unique=True)
    active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Получатель TG"
        verbose_name_plural = "Получатели TG"

    def __str__(self):
        return self.title or str(self.chat_id)
