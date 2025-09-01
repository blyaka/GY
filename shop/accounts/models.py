from django.db import models
from django.urls import reverse

from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField('ФИО', max_length=150, blank=True)
    phone = models.CharField('Телефон', max_length=18, blank=True)
    address = models.TextField('Адрес', blank=True)
    favorites = models.ManyToManyField(
        'products.Product',
        through='Favorite',
        related_name='favorited_by',
        blank=True,
        verbose_name='Избранные товары'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.full_name.strip() if self.full_name else (self.user.email or self.user.username)
    
    def is_favorite(self, product) -> bool:
        return Favorite.objects.filter(profile=self, product=product).exists()


class Favorite(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='favorite_links')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='favorite_links')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = (('profile', 'product'),)
        indexes = [
            models.Index(fields=('profile', 'product')),
            models.Index(fields=('created_at',)),
        ]

    def __str__(self):
        return f'{self.profile} → {self.product}'