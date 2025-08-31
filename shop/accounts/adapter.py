# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
        try:
            html = render_to_string(f"{template_prefix}_message.html", context)
        except TemplateDoesNotExist:
            html = None
        try:
            text = render_to_string(f"{template_prefix}_message.txt", context)
        except TemplateDoesNotExist:
            text = ""

        msg = EmailMultiAlternatives(subject, html or text, settings.DEFAULT_FROM_EMAIL, [email])
        if html:
            msg.content_subtype = "html"
            if text:
                msg.attach_alternative(text, "text/plain")
        msg.send()
