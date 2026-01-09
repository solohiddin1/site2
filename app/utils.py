from django.conf import settings
import requests

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
CHAT_ID = settings.CHAT_ID


def send_telegram_message(name, phone_number, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = (
        f"<b>📨 Yangi Xabar Qabul Qilindi</b>\n\n"
        f"<b>👤 Ism:</b> {name}\n"
        f"<b>📞 Telefon:</b> {phone_number}\n"
        f"<b>💬 Xabar:</b> {message}"
    )
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)