from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.models import Site
from types import SimpleNamespace
from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders


class CustomAccountAdapter(DefaultAccountAdapter):

    def get_user_display(self, user):
        full = getattr(user, "full_name", None) or getattr(user, "get_full_name", lambda: "")()
        return full or user.get_username()
    
    
    def _current_site(self, request):
        try:
            if request is not None:
                return self.get_current_site(request)
        except Exception:
            pass
        try:
            return Site.objects.get_current()
        except Exception:
            pass
        domain = (request.get_host() if getattr(request, "get_host", None) else
                  (settings.ALLOWED_HOSTS[0] if getattr(settings, "ALLOWED_HOSTS", None) else "localhost"))
        name = getattr(settings, "SITE_NAME", domain)
        return SimpleNamespace(domain=domain, name=name)

    def render_mail(self, template_prefix, email, context, headers=None):
        subj = render_to_string(f"{template_prefix}_subject.txt", context).strip()
        subj = self.format_email_subject(subj)

        u = context.get("user")
        if u and "user_display" not in context:
            context["user_display"] = self.get_user_display(u)

        try:
            html = render_to_string(f"{template_prefix}_message.html", context)
        except TemplateDoesNotExist:
            html = None
        if html:
            msg = EmailMessage(subj, html, settings.DEFAULT_FROM_EMAIL, [email], headers=headers)
            msg.content_subtype = "html"
            path = finders.find('images/GY.png')
            if path:
                with open(path, 'rb') as f:
                    img = MIMEImage(f.read(), _subtype='png')
                img.add_header('Content-ID', '<gylogo>')
                img.add_header('Content-Disposition', 'inline', filename='GY.png')
                msg.attach(img)
            return msg
        return super().render_mail(template_prefix, email, context, headers=headers)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        user = emailconfirmation.email_address.user
        email = emailconfirmation.email_address.email

        try:
            activate_url = self.get_email_confirmation_url(request, emailconfirmation)
        except Exception:
            activate_url = emailconfirmation.key

        ctx = {
            "user": user,
            "current_site": self._current_site(request),
            "activate_url": activate_url,
            "user_display": self.get_user_display(user),
            "request": request,
        }

        prefix = "account/email/email_confirmation_signup" if signup else "account/email/email_confirmation"

        subject = render_to_string(f"{prefix}_subject.txt", ctx).strip()
        subject = self.format_email_subject(subject)
        html = render_to_string(f"{prefix}_message.html", ctx)

        msg = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, [email])
        msg.content_subtype = "html"

        path = finders.find('images/GY.png')
        if path:
            with open(path, 'rb') as f:
                img = MIMEImage(f.read(), _subtype='png')
            img.add_header('Content-ID', '<gylogo>')
            img.add_header('Content-Disposition', 'inline', filename='GY.png')
            msg.attach(img)

        msg.send()
