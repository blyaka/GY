from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.text import slugify
from django.urls import reverse


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    preview = models.ImageField('Превью', upload_to="posts/", default="posts/default.jpg")
    content = CKEditor5Field("Контент", config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    on_main = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title