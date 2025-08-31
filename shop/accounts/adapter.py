# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
        html = text = ""
        try:  html = render_to_string(f"{template_prefix}_message.html", context)
        except TemplateDoesNotExist: pass
        try:  text = render_to_string(f"{template_prefix}_message.txt", context)
        except TemplateDoesNotExist: pass

        if html:
            msg = EmailMultiAlternatives(subject, html, to=[email])
            msg.content_subtype = "html"  # главный — HTML
            if text:
                msg.attach_alternative(text, "text/plain")
        else:
            msg = EmailMultiAlternatives(subject, text or "", to=[email])
        self.send_mail_message(msg)
