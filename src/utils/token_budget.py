"""Извлечение расхода токенов из ответа Gemini (лимиты — в src.billing)."""

DEFAULT_TOKENS_PER_REQUEST = 500


def extract_token_count(response: object) -> int:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return DEFAULT_TOKENS_PER_REQUEST

    total = getattr(usage, "total_token_count", None)
    if total is not None:
        try:
            total_int = int(total)
            if total_int > 0:
                return total_int
        except (TypeError, ValueError):
            pass

    prompt = getattr(usage, "prompt_token_count", None) or 0
    candidates = getattr(usage, "candidates_token_count", None) or 0
    try:
        combined = int(prompt) + int(candidates)
        if combined > 0:
            return combined
    except (TypeError, ValueError):
        pass

    return DEFAULT_TOKENS_PER_REQUEST
