import json
import logging
import time
import re
import requests

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.html import escape
from django.utils import timezone
from django.core.cache import cache
from django.urls import reverse

from .forms import RequestForm, ContactForm
from .models import TelegramBot, TelegramRecipient

log = logging.getLogger(__name__)

# ---- лимиты
IP_PER_MIN  = 1
IP_PER_DAY  = 10
ADDR_PER_DAY = 3

PHONE_CLEAN_RE = re.compile(r"[^\d+]")


def _rate_limit(key: str, limit: int, window_sec: int) -> bool:
    if cache.add(key, 1, timeout=window_sec):
        return True
    try:
        val = cache.incr(key)
    except Exception:
        val = cache.get(key, 0)
    return int(val or 0) <= limit


def _send_telegram(text: str) -> None:
    bots = TelegramBot.objects.filter(enabled=True)
    recipients = list(
        TelegramRecipient.objects.filter(active=True).values_list("chat_id", flat=True)
    )
    if not bots or not recipients:
        return
    for bot in bots:
        url = f"https://api.telegram.org/bot{bot.token}/sendMessage"
        for chat_id in recipients:
            try:
                requests.post(
                    url,
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    timeout=6,
                )
            except Exception as e:
                log.warning("Telegram send error: %s", e)


@require_POST
@csrf_protect
def submit_request(request):
    if request.content_type and request.content_type.startswith("application/json"):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("invalid json")
        data = {
            "full_name": (payload.get("full_name") or payload.get("fio") or "").strip(),
            "email":     (payload.get("email") or "").strip(),
            "phone":     PHONE_CLEAN_RE.sub("", (payload.get("phone") or "").strip()),
        }
        honeypot = (payload.get("website") or "").strip()
        ts_raw   = str(payload.get("ts") or "")
    else:
        data = request.POST.copy()
        data["phone"] = PHONE_CLEAN_RE.sub("", (data.get("phone") or "").strip())
        honeypot = (data.get("website") or "").strip()
        ts_raw   = str(data.get("ts") or "")

    if honeypot:
        return JsonResponse({"ok": False, "errors": {"__all__": ["Spam detected"]}}, status=400)

    now = int(time.time())
    try:
        ts = int(ts_raw)
    except Exception:
        ts = 0
    if ts and (now - ts < 2 or now - ts > 3600):
        return JsonResponse({"ok": False, "errors": {"__all__": ["Suspicious timing"]}}, status=400)

    ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
    email = (data.get("email") or "").lower()
    phone = (data.get("phone") or "")

    if not _rate_limit(f"reqs:ip:{ip}:m1", IP_PER_MIN, 60):
        return JsonResponse({"ok": False, "errors": {"__all__": ["Слишком много запросов. Попробуйте позже."]}}, status=429)
    if not _rate_limit(f"reqs:ip:{ip}:d1", IP_PER_DAY, 86400):
        return JsonResponse({"ok": False, "errors": {"__all__": ["Лимит на сегодня исчерпан."]}}, status=429)
    if email and not _rate_limit(f"reqs:email:{email}:d1", ADDR_PER_DAY, 86400):
        return JsonResponse({"ok": False, "errors": {"email": ["Слишком много заявок для этого email."]}}, status=429)
    if phone and not _rate_limit(f"reqs:phone:{phone}:d1", ADDR_PER_DAY, 86400):
        return JsonResponse({"ok": False, "errors": {"phone": ["Слишком много заявок для этого телефона."]}}, status=429)

    form = RequestForm(data=data)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    obj = form.save(commit=False)
    obj.user_ip = ip
    obj.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
    obj.full_clean()
    obj.save()

    local_created = timezone.localtime(obj.created_at)
    text = (
        "<b>Новая заявка PRIVE Labaratory</b>\n"
        f"👤 <b>ФИО:</b> {escape(obj.full_name)}\n"
        f"📞 <b>Телефон:</b> {escape(obj.phone or '—')}\n"
        f"✉️ <b>Email:</b> {escape(obj.email or '—')}\n"
        f"🕒 <b>Дата:</b> {local_created:%d.%m.%Y %H:%M}\n"
    )
    _send_telegram(text)

    return JsonResponse({"ok": True})


# --------- НОВОЕ: форма «Свяжитесь с нами» (страница Покупателю и т.п.)
@require_POST
@csrf_protect
def submit_contact(request):
    # поддержка JSON и обычного form POST
    if request.content_type and request.content_type.startswith("application/json"):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("invalid json")
        data = {
            "full_name": (payload.get("name") or payload.get("full_name") or "").strip(),
            "email":     (payload.get("email") or "").strip(),
            "phone":     PHONE_CLEAN_RE.sub("", (payload.get("phone") or "").strip()),
            "topic":     (payload.get("topic") or "other"),
            "message":   (payload.get("message") or "").strip(),
            "policy_agreed": bool(payload.get("policy")),
            "marketing_agreed": bool(payload.get("marketing")),
            "page_url":  (payload.get("page_url") or request.META.get("HTTP_REFERER") or ""),
            "locale":    (payload.get("locale") or getattr(request, "LANGUAGE_CODE", "") or ""),
        }
        honeypot = (payload.get("website") or "").strip()
        ts_raw   = str(payload.get("ts") or "")
    else:
        data = request.POST.copy()
        data["full_name"] = (data.get("name") or data.get("full_name") or "").strip()
        data["phone"] = PHONE_CLEAN_RE.sub("", (data.get("phone") or "").strip())
        data["policy_agreed"] = bool(data.get("policy"))
        data["marketing_agreed"] = bool(data.get("marketing"))
        if not data.get("topic"):
            data["topic"] = "other"
        if not data.get("page_url"):
            data["page_url"] = request.META.get("HTTP_REFERER") or ""
        if not data.get("locale"):
            data["locale"] = getattr(request, "LANGUAGE_CODE", "") or ""
        honeypot = (data.get("website") or "").strip()
        ts_raw   = str(data.get("ts") or "")

    # антиспам поле и тайминг
    if honeypot:
        return JsonResponse({"ok": False, "errors": {"__all__": ["Spam detected"]}}, status=400)

    now = int(time.time())
    try:
        ts = int(ts_raw)
    except Exception:
        ts = 0
    if ts and (now - ts < 2 or now - ts > 3600):
        return JsonResponse({"ok": False, "errors": {"__all__": ["Suspicious timing"]}}, status=400)

    # rate-limit
    ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
    email = (data.get("email") or "").lower()
    phone = (data.get("phone") or "")

    if not _rate_limit(f"contact:ip:{ip}:m1", IP_PER_MIN, 60):
        return JsonResponse({"ok": False, "errors": {"__all__": ["Слишком много запросов. Попробуйте позже."]}}, status=429)
    if not _rate_limit(f"contact:ip:{ip}:d1", IP_PER_DAY, 86400):
        return JsonResponse({"ok": False, "errors": {"__all__": ["Лимит на сегодня исчерпан."]}}, status=429)
    if email and not _rate_limit(f"contact:email:{email}:d1", ADDR_PER_DAY, 86400):
        return JsonResponse({"ok": False, "errors": {"email": ["Слишком много заявок для этого email."]}}, status=429)
    if phone and not _rate_limit(f"contact:phone:{phone}:d1", ADDR_PER_DAY, 86400):
        return JsonResponse({"ok": False, "errors": {"phone": ["Слишком много заявок для этого телефона."]}}, status=429)

    form = ContactForm(data=data)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    obj = form.save(commit=False)
    obj.user_ip = ip
    obj.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
    obj.full_clean()
    obj.save()

    local_created = timezone.localtime(obj.created_at)
    topic_map = {
        "order": "Оформление заказа",
        "payment": "Оплата",
        "delivery": "Доставка",
        "exchange": "Возврат и обмен",
        "other": "Другое",
    }
    msg_preview = (obj.message or "—").strip()
    if len(msg_preview) > 500:
        msg_preview = msg_preview[:497] + "…"

    text = (
        "<b>Новая контактная заявка</b>\n"
        f"👤 <b>Имя:</b> {escape(obj.full_name)}\n"
        f"📞 <b>Телефон:</b> {escape(obj.phone or '—')}\n"
        f"✉️ <b>Email:</b> {escape(obj.email or '—')}\n"
        f"🏷 <b>Тема:</b> {topic_map.get(obj.topic, obj.topic)}\n"
        f"💬 <b>Сообщение:</b> {escape(msg_preview)}\n"
        f"📣 <b>Маркетинг:</b> {'да' if obj.marketing_agreed else 'нет'}\n"
        f"🕒 <b>Дата:</b> {local_created:%d.%m.%Y %H:%M}\n"
    )
    _send_telegram(text)

    if request.content_type and request.content_type.startswith("application/json"):
        return JsonResponse({"ok": True})

    referer = data.get("page_url") or request.META.get("HTTP_REFERER") or reverse("buyer")
    sep = "&" if "?" in referer else "?"
    return HttpResponseRedirect(f"{referer}{sep}sent=1")
