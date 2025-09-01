from django.contrib import admin
from django import forms
from modeltranslation.admin import TranslationAdmin
from .models import Post
from django_ckeditor_5.widgets import CKEditor5Widget


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'content_ru': CKEditor5Widget(config_name='default'),
            'content_en': CKEditor5Widget(config_name='default'),
        }


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    form = PostAdminForm
    list_display = ['title', 'created_at', 'updated_at']
    prepopulated_fields = {"slug": ("title",)}

    class Media:
        css = {
            'all': ('css/post.css',)
        }
