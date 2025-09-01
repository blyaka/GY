
from django import template
from django.urls import resolve, reverse
from django.utils import translation

register = template.Library()

@register.simple_tag(takes_context=True)
def switch_language_url(context, lang_code):
    request = context["request"]
    match = resolve(request.path_info)

    with translation.override(lang_code):
        url = reverse(match.view_name, args=match.args, kwargs=match.kwargs)

    qs = request.META.get("QUERY_STRING")
    if qs:
        url = f"{url}?{qs}"
    return url
