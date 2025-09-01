from django.contrib import admin
from .models import Request, TelegramBot, TelegramRecipient, ContactRequest

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "created_at")
    search_fields = ("full_name", "email", "phone")
    readonly_fields = ("created_at", "user_ip", "user_agent")

admin.site.register(TelegramBot)
admin.site.register(TelegramRecipient)

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "topic", "policy_agreed", "marketing_agreed", "created_at")
    list_filter = ("topic", "policy_agreed", "marketing_agreed", "created_at")
    search_fields = ("full_name", "email", "phone", "message")
    readonly_fields = ("created_at", "user_ip", "user_agent")