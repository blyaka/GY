from modeltranslation.translator import register, TranslationOptions
from .models import Post

@register(Post)
class PostTR(TranslationOptions):
    fields = ('title', 'content')