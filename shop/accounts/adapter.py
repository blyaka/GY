from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Делает HTML основным телом, а text/plain — альтернативой.
    Если txt нет — шлём только HTML.
    """

    def send_mail(self, template_prefix, email, context):
        # subject обязателен и всегда txt по контракту allauth
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

        # Если есть HTML — делаем его основным
        if html_body:
            msg = EmailMultiAlternatives(subject, html_body, to=[email])
            msg.content_subtype = "html"  # text/html
            if text_body:
                msg.attach_alternative(text_body, "text/plain")
        else:
            # fallback: только текст
            msg = EmailMultiAlternatives(subject, text_body or "", to=[email])

        self.send_mail_message(msg)
