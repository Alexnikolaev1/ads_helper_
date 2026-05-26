"""Ограничение частоты запросов к API в рамках одной сессии."""

from __future__ import annotations

import time

import streamlit as st

RATE_LIMIT_SECONDS = 3


def init_rate_limit() -> None:
    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0.0


def seconds_until_allowed() -> float:
    """Сколько секунд ждать до следующего запроса. 0 — можно отправлять."""
    init_rate_limit()
    elapsed = time.time() - float(st.session_state.last_request_time)
    remaining = RATE_LIMIT_SECONDS - elapsed
    return max(0.0, remaining)


def mark_request_started() -> None:
    """Фиксирует момент отправки запроса к API (вызывать перед вызовом Gemini)."""
    init_rate_limit()
    st.session_state.last_request_time = time.time()


def block_if_rate_limited() -> bool:
    """
    Блокирует слишком частые запросы.
    Возвращает True, если запрос нужно прервать (показано предупреждение).
    """
    wait = seconds_until_allowed()
    if wait > 0:
        st.warning(
            f"Пожалуйста, подождите **{wait:.1f}** сек. перед следующим запросом."
        )
        return True
    mark_request_started()
    return False
