from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def render_mail(self, template_prefix, email, context, headers=None):
        subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()
        subject = self.format_email_subject(subject)

        html = None
        try:
            html = render_to_string(f"{template_prefix}_message.html", context)
        except TemplateDoesNotExist:
            pass

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        if html:
            msg = EmailMessage(subject, html, from_email, [email], headers=headers)
            msg.content_subtype = "html"
            return msg
        try:
            text = render_to_string(f"{template_prefix}_message.txt", context)
        except TemplateDoesNotExist:
            text = ""
        return EmailMultiAlternatives(subject, text, from_email, [email], headers=headers)
