
from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        subject = render_to_string(f"{template_prefix}_subject.txt", context).strip()

        html_body = None
        text_body = None
        try:
            html_body = render_to_string(f"{template_prefix}_message.html", context)
        except TemplateDoesNotExist:
            pass
        try:
            text_body = render_to_string(f"{template_prefix}_message.txt", context)
        except TemplateDoesNotExist:
            pass

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        if html_body:
            msg = EmailMultiAlternatives(subject, html_body, from_email, [email])
            msg.content_subtype = "html"
            if text_body:
                msg.attach_alternative(text_body, "text/plain")
        else:
            msg = EmailMultiAlternatives(subject, text_body or "", from_email, [email])

        msg.send()
