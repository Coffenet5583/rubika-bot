"""
بات ساده‌ی ضد لینک/تبلیغ برای کانال روبیکا
پیش‌نیاز: بات باید در کانال، ادمین با دسترسی «حذف پیام» باشد.
"""

import re
import time
import requests

TOKEN = "CECEHI0EOSZIOTIIXPWJOTIEYPLBMPPODSEFPIWXINEIERXSEVYIEKXDSZMOPAMR"
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"

# چه چیزی «لینک/تبلیغ» حساب می‌شود - این‌ها را بر اساس نیازت اصلاح کن
LINK_PATTERNS = [
    r"https?://\S+",              # http:// یا https://
    r"www\.\S+",                  # www.something
    r"\b\S+\.(ir|com|net|org|io)\b",  # دامنه‌های رایج
    r"@\w{4,}",                   # یوزرنیم‌های چت/کانال (اختیاری - ممکنه فالس‌پازیتیو بده)
    r"t\.me/\S+",                 # لینک تلگرام
    r"rubika\.ir/\S+",            # لینک کانال روبیکا
]

# کلمات کلیدی تبلیغاتی رایج (اختیاری - اضافه/کم کن)
AD_KEYWORDS = ["تبلیغ", "پروموشن", "تخفیف ویژه", "سفارش دهید", "لینک زیر"]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in LINK_PATTERNS]


def is_ad_or_link(text: str) -> bool:
    if not text:
        return False
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    for kw in AD_KEYWORDS:
        if kw in text:
            return True
    return False


def delete_message(chat_id: str, message_id: str):
    url = f"{BASE_URL}/deleteMessage"
    data = {"chat_id": chat_id, "message_id": message_id}
    resp = requests.post(url, json=data)
    print("حذف شد:", resp.status_code, resp.text)


def get_updates(offset_id=None, limit=50):
    url = f"{BASE_URL}/getUpdates"
    data = {"limit": limit}
    if offset_id:
        data["offset_id"] = offset_id
    resp = requests.post(url, json=data)
    resp.raise_for_status()
    return resp.json()


def main():
    offset_id = None
    print("بات در حال اجراست... (Ctrl+C برای توقف)")
    while True:
        try:
            result = get_updates(offset_id=offset_id)
            data = result.get("data", result)  # بسته به ساختار پاسخ ممکنه فرق کنه
            updates = data.get("updates", [])
            offset_id = data.get("next_offset_id", offset_id)

            for update in updates:
                # ساختار دقیق فیلدها را با پرینت یک نمونه پاسخ بررسی و در صورت نیاز اصلاح کن
                new_message = update.get("new_message") or update.get("message")
                if not new_message:
                    continue

                chat_id = new_message.get("chat_id") or update.get("chat_id")
                message_id = new_message.get("message_id")
                text = new_message.get("text", "")

                if is_ad_or_link(text):
                    print(f"لینک/تبلیغ پیدا شد در پیام {message_id}: {text[:50]}")
                    delete_message(chat_id, message_id)

        except Exception as e:
            print("خطا:", e)

        time.sleep(2)  # فاصله بین هر بار چک کردن


if __name__ == "__main__":
    main()
