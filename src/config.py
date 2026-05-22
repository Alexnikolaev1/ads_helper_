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

EXAMPLE_PROMPTS = [
    "Установка кондиционеров со скидкой 20% до конца месяца",
    "Онлайн-курс по Python для начинающих, старт 1 июня",
    "Доставка цветов за 2 часа по Москве, букет от 1990 ₽",
    "Стоматология: бесплатная консультация и снимок при записи",
]


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
