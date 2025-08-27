from django.db import models

class SiteContacts(models.Model):
    phone = models.CharField("Телефон", max_length=64, blank=True)
    phone2 = models.CharField("Второй Телефон", max_length=64, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)

    whatsapp = models.URLField("WhatsApp", blank=True)
    telegram = models.URLField("Telegram", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    vk = models.URLField("VK", blank=True)
    youtube = models.URLField("YouTube", blank=True)
    tiktok = models.URLField("TikTok", blank=True)

    class Meta:
        verbose_name = "Контакты и соцсети"
        verbose_name_plural = "Контакты и соцсети"

    def __str__(self):
        return "Контакты сайта"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
