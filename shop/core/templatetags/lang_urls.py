from django import template
from django.conf import settings

register = template.Library()

LANG_SET = {code.split('-')[0] for code, _ in getattr(settings, 'LANGUAGES', [])}
DEFAULT_LANG = getattr(settings, 'LANGUAGE_CODE', 'ru').split('-')[0]

@register.simple_tag(takes_context=True)
def lang_switch(context, lang_code: str):
    request = context.get("request")
    lang = (lang_code or DEFAULT_LANG).split('-')[0]
    if lang not in LANG_SET:
        lang = DEFAULT_LANG

    path = getattr(request, "path", "/") or "/"
    qs = getattr(request, "META", {}).get("QUERY_STRING", "")

    parts = path.lstrip("/").split("/", 1)
    has_prefix = parts and parts[0] in LANG_SET
    rest = "/" + (parts[1] if len(parts) > 1 else "")

    # prefix_default_language=True → всегда /<lang>/...
    new_path = f"/{lang}{rest if has_prefix else path if path.startswith('/') else '/' + path}"

    if qs:
        new_path = f"{new_path}?{qs}"
    return new_path
