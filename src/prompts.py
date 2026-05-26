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
- Не более {platform["max_chars"]} символов на вариант.
- Пиши на русском языке.
- Текст должен быть готов к публикации: без номеров, без слова «вариант», без рамок из символов (═, ─, =, *).

Формат ответа (строго):
- Ровно {options.variant_count} поста подряд.
- Между постами — отдельная строка из трёх дефисов: ---
- Каждый пост — только продающий текст, без заголовков и пояснений для редактора.
Отвечай ТОЛЬКО текстом постов."""


def build_user_prompt(brief: str, options: GenerationOptions) -> str:
    return f"""Бриф от клиента:
{brief.strip()}

Дополнительно: платформа {options.platform}, тон «{options.tone}»."""
