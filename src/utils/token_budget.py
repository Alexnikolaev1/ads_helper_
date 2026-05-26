"""Ежемесячный бюджет токенов на сессию Streamlit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import streamlit as st

MONTHLY_TOKEN_BUDGET = 500_000
DEFAULT_TOKENS_PER_REQUEST = 500

LIMIT_MESSAGE = (
    "Ваш месячный лимит в 500 000 токенов исчерпан. "
    "Лимит обновится автоматически. "
    "Если вам нужен больший объем, напишите нам для обсуждения индивидуального тарифа."
)


@dataclass(frozen=True)
class TokenBudgetStatus:
    used: int
    budget: int
    remaining: int
    month_key: str
    exhausted: bool


def _current_month_key() -> str:
    return datetime.now().strftime("%Y-%m")


def init_token_budget() -> None:
    """Инициализирует или сбрасывает счётчик при смене календарного месяца."""
    month = _current_month_key()
    if st.session_state.get("token_month") != month:
        st.session_state["token_month"] = month
        st.session_state["tokens_used"] = 0
    elif "tokens_used" not in st.session_state:
        st.session_state["tokens_used"] = 0
        st.session_state["token_month"] = month


def get_budget_status() -> TokenBudgetStatus:
    init_token_budget()
    used = int(st.session_state.get("tokens_used", 0))
    remaining = max(0, MONTHLY_TOKEN_BUDGET - used)
    return TokenBudgetStatus(
        used=used,
        budget=MONTHLY_TOKEN_BUDGET,
        remaining=remaining,
        month_key=st.session_state.get("token_month", _current_month_key()),
        exhausted=remaining <= 0,
    )


def is_budget_exhausted() -> bool:
    return get_budget_status().exhausted


def record_token_usage(tokens: int) -> None:
    if tokens <= 0:
        return
    init_token_budget()
    st.session_state["tokens_used"] = int(st.session_state.get("tokens_used", 0)) + tokens


def extract_token_count(response: object) -> int:
    """Извлекает total_tokens из ответа Gemini; иначе — значение по умолчанию."""
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
