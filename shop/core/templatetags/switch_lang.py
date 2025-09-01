from django import template
from django.conf import settings

register = template.Library()

# конфиги языка
LANG_SET = {code.split('-')[0] for code, _ in getattr(settings, 'LANGUAGES', [])}
DEFAULT_LANG = (getattr(settings, 'LANGUAGE_CODE', 'ru').split('-')[0])

# у тебя i18n_patterns(..., prefix_default_language=True)
PREFIX_DEFAULT = True

@register.simple_tag(takes_context=True)
def switch_language_url(context, lang_code: str):
    """Без resolve/reverse: просто подменяем префикс языка безопасно."""
    request = context.get("request")

    # нормализуем код
    lang = (lang_code or DEFAULT_LANG).split('-')[0]
    if lang not in LANG_SET:
        lang = DEFAULT_LANG

    # путь и query
    path = getattr(request, "path", "/") or "/"
    qs = getattr(request, "META", {}).get("QUERY_STRING", "")

    # разбор текущего пути
    parts = path.lstrip("/").split("/", 1)
    has_prefix = parts and parts[0] in LANG_SET
    rest = "/" + (parts[1] if len(parts) > 1 else "")

    if PREFIX_DEFAULT:
        # всегда префиксуем (и для дефолтного тоже)
        new_path = f"/{lang}{rest}"
    else:
        # если дефолтный — без префикса
        if lang == DEFAULT_LANG:
            new_path = rest or "/"
        else:
            new_path = f"/{lang}{rest}"

    # приклеим query если был
    if qs:
        new_path = f"{new_path}?{qs}"

    return new_path
