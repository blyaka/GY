from django import template
from django.conf import settings
from django.urls import resolve, reverse, NoReverseMatch, Resolver404
from django.utils import translation

register = template.Library()

@register.simple_tag(takes_context=True)
def switch_language_url(context, lang_code: str):
    request = context.get("request")
    if not request:
        return "/"

    path = request.path
    query = request.META.get("QUERY_STRING", "")

    try:
        match = resolve(path)
        with translation.override(lang_code):
            try:
                url = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
            except NoReverseMatch:
                url = None
        if url:
            if query:
                url = f"{url}?{query}"
            return url
    except Resolver404:
        pass

    langs = {code for code, _ in getattr(settings, "LANGUAGES", [])}
    parts = path.lstrip("/").split("/", 1)
    if parts and parts[0] in langs:
        rest = "/" + parts[1] if len(parts) > 1 else "/"
        url = f"/{lang_code}{rest}"
    else:
        url = f"/{lang_code}{path}"

    if query:
        url = f"{url}?{query}"
    return url
