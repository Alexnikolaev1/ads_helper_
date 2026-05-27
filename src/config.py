import os
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

MODELS_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

PLATFORMS = {
    "Универсальный": {"hint": "универсальный пост для любой соцсети", "max_chars": 2000},
    "ВКонтакте": {"hint": "пост для ленты ВКонтакте", "max_chars": 4096},
    "Telegram": {"hint": "пост для Telegram-канала", "max_chars": 4096},
    "Instagram": {"hint": "подпись к посту в Instagram", "max_chars": 2200},
    "Avito / объявление": {"hint": "текст объявления на Avito или аналогах", "max_chars": 8000},
}

TONES = ["Дружелюбный", "Деловой", "Срочная акция", "Премиум", "С юмором", "Экспертный"]

LENGTHS = {
    "Короткий": "2–4 строки, максимум лаконичности",
    "Средний": "5–8 строк, баланс деталей и читаемости",
    "Длинный": "9–14 строк, больше аргументов и выгод",
}

VARIANT_COUNTS = [2, 3, 4, 5]

BRIEF_EXAMPLE = (
    "Установка кондиционеров со скидкой 20% до конца месяца. "
    "Монтаж за 1 день, гарантия 3 года, бесплатный выезд мастера."
)

# Пример на экране входа (витрина качества генерации)
AUTH_DEMO_BRIEF = BRIEF_EXAMPLE
AUTH_DEMO_POST = """На улице +28°C. А дома — душно, как в сауне? 🌡️

Пока вы терпите жару, кондиционер «на потом» обходится дороже, чем кажется:
• ночи без сна → усталость и срывы на близких
• вентилятор гоняет горячий воздух по кругу
• в пик сезона мастера заняты на 2–3 недели вперёд

Мы — «КлиматКомфорт». Ставим кондиционеры под ключ за 24 часа.

🔥 До конца месяца — скидка 20% на монтаж:
→ бесплатный выезд и расчёт за 15 минут
→ подбор модели под вашу комнату (не переплатите за лишние «л.с.»)
→ гарантия 3 года + сервис, если что-то пойдёт не так

1 200+ семей в регионе уже встретили лето без духоты.

📲 Напишите «ХОЛОД» в Direct — закрепим скидку и свободное окно мастера.
Осталось 7 слотов по акции. Дальше — только по стандартной цене.

#кондиционер #монтажкондиционера #скидка #климат #комфортдома"""


@dataclass(frozen=True)
class GenerationOptions:
    platform: str
    tone: str
    length: str
    variant_count: int
    use_emoji: bool
    include_hashtags: bool
    include_cta: bool


def get_api_key() -> str | None:
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")


def get_admin_password() -> str:
    try:
        pwd = st.secrets.get("ADMIN_PASSWORD")
        if pwd:
            return str(pwd)
    except Exception:
        pass
    return os.getenv("ADMIN_PASSWORD", "")


def get_contact_telegram() -> str:
    try:
        contact = st.secrets.get("CONTACT_TELEGRAM")
        if contact:
            return str(contact).strip()
    except Exception:
        pass
    return os.getenv("CONTACT_TELEGRAM", "@your_contact").strip()


def get_telegram_link(contact: str | None = None) -> tuple[str, str]:
    """
    Возвращает (подпись для кнопки, URL).
    Поддерживает @ник, t.me/ник, https://t.me/ник.
    """
    raw = (contact or get_contact_telegram()).strip()
    if raw.startswith(("https://t.me/", "http://t.me/")):
        url = raw.replace("http://", "https://", 1)
        label = "@" + url.rstrip("/").split("/")[-1]
        return label, url
    if raw.startswith("t.me/"):
        username = raw.split("/")[-1]
        return f"@{username}", f"https://t.me/{username}"
    username = raw.lstrip("@").split("?")[0]
    return f"@{username}", f"https://t.me/{username}"
