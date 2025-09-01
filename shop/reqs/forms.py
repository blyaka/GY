from django import forms
from .models import Request, ContactRequest

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ("full_name", "email", "phone")


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ["full_name", "email", "phone", "topic", "message", "policy_agreed", "marketing_agreed", "page_url", "locale"]

    def clean_message(self):
        m = (self.cleaned_data.get("message") or "").strip()
        return m[:4000]