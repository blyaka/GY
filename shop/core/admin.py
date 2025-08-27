from django.contrib import admin
from .models import SiteContacts

@admin.register(SiteContacts)
class SiteContactsAdmin(admin.ModelAdmin):
    list_display = ("phone", "email")
    def has_add_permission(self, request):
        return not SiteContacts.objects.exists()
