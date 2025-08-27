from django import template
from django.core.cache import cache
from core.models import SiteContacts

register = template.Library()

@register.simple_tag
def get_site_contacts():
    k = "site_contacts"
    s = cache.get(k)
    if s is None:
        s = SiteContacts.get_solo()
        cache.set(k, s, 60 * 60)
    return s
