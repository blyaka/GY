import random
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import uuid
from django.db.models import F



class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ImageField(verbose_name='avatar', upload_to="profile/", null=True, blank=True, default=f'profile/d{random.randint(1,8)}.jpg')
    

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('community:profile', args=[str(self.id)])

    def get_avatar(self):
        return self.avatar.url
