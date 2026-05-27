from __future__ import annotations

import re

import streamlit as st

from src.auth.passwords import hash_password, verify_password
from src.db.repository import User, UserRepository

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_SESSION_USER_ID = "auth_user_id"
_SESSION_USER_EMAIL = "auth_user_email"


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_current_user() -> User | None:
    user_id = st.session_state.get(_SESSION_USER_ID)
    if not user_id:
        return None
    return UserRepository().get_by_id(int(user_id))


def require_user() -> User:
    user = get_current_user()
    if not user:
        st.stop()
    return user


def login_user(email: str, password: str) -> tuple[bool, str]:
    normalized = _normalize_email(email)
    if not _EMAIL_RE.match(normalized):
        return False, "Введите корректный email."

    repo = UserRepository()
    stored_hash = repo.get_password_hash(normalized)
    if not stored_hash:
        return False, "Пользователь не найден. Зарегистрируйтесь."

    if not verify_password(password, stored_hash):
        return False, "Неверный пароль."

    user = repo.get_by_email(normalized)
    if not user:
        return False, "Ошибка входа."

    st.session_state[_SESSION_USER_ID] = user.id
    st.session_state[_SESSION_USER_EMAIL] = user.email
    return True, ""


def register_user(email: str, password: str, password_confirm: str) -> tuple[bool, str]:
    normalized = _normalize_email(email)
    if not _EMAIL_RE.match(normalized):
        return False, "Введите корректный email."
    if len(password) < 6:
        return False, "Пароль — минимум 6 символов."
    if password != password_confirm:
        return False, "Пароли не совпадают."

    repo = UserRepository()
    if repo.get_by_email(normalized):
        return False, "Этот email уже зарегистрирован."

    user = repo.create_user(normalized, hash_password(password))
    st.session_state[_SESSION_USER_ID] = user.id
    st.session_state[_SESSION_USER_EMAIL] = user.email
    return True, ""


def logout_user() -> None:
    for key in (
        _SESSION_USER_ID,
        _SESSION_USER_EMAIL,
        "variants",
        "generated",
        "last_brief",
        "history",
        "brief_input",
        "admin_unlocked",
    ):
        st.session_state.pop(key, None)
