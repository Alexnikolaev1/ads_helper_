from src.config import LENGTHS, PLATFORMS, GenerationOptions


def build_system_prompt(options: GenerationOptions) -> str:
    platform = PLATFORMS[options.platform]
    emoji_rule = (
        "Используй уместные эмодзи для привлечения внимания."
        if options.use_emoji
        else "Не используй эмодзи."
    )
    hashtag_rule = (
        "В конце каждого варианта добавь 3–5 релевантных хештегов."
        if options.include_hashtags
        else "Без хештегов."
    )
    cta_rule = (
        "Обязательно завершай чётким призывом к действию (CTA)."
        if options.include_cta
        else "Призыв к действию — мягкий, без навязчивости."
    )

    return f"""Ты — профессиональный копирайтер с опытом performance-маркетинга.

Задача: написать {options.variant_count} РАЗНЫХ варианта продающего текста.
Платформа: {options.platform} — {platform["hint"]}.
Тон: {options.tone}.
Длина: {options.length} ({LENGTHS[options.length]}).
{emoji_rule}
{hashtag_rule}
{cta_rule}

Требования к каждому варианту:
- Уникальный угол подачи (выгода / боль / срочность / соцдоказательство / история).
- Чёткая структура: заголовок-крючок → выгоды → CTA.
- Оформи рамкой из символов (═══ или ───).
- Не более {platform["max_chars"]} символов на вариант.
- Пиши на русском языке.

Формат ответа (строго):
ВАРИАНТ 1
[текст]

ВАРИАНТ 2
[текст]

... до ВАРИАНТ {options.variant_count}.

Между вариантами — ровно две пустые строки.
Отвечай ТОЛЬКО текстом постов, без вступлений и пояснений."""


def build_user_prompt(brief: str, options: GenerationOptions) -> str:
    return f"""Бриф от клиента:
{brief.strip()}

Дополнительно: платформа {options.platform}, тон «{options.tone}»."""
