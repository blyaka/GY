from django import template
import re

register = template.Library()

@register.filter
def pretty_phone(value):
    """
    Форматирует строку в вид +X XXX XXX XX XX
    Пример: +79991234567 -> +7 999 123 45 67
    """
    if not value:
        return ''
    digits = re.sub(r'\D', '', str(value))
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    if not digits.startswith('7'):
        digits = '7' + digits
    try:
        return f'+{digits[0]} {digits[1:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}'
    except IndexError:
        return '+' + digits
