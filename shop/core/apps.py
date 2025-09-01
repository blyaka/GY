from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from django.db.models.signals import post_save, post_delete
        from django.core.cache import cache
        from .models import SiteContacts

        def clear_cache(*a, **kw):
            cache.delete("site_contacts")

        post_save.connect(clear_cache, sender=SiteContacts)
        post_delete.connect(clear_cache, sender=SiteContacts)
