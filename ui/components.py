import html
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.config import AUTH_DEMO_BRIEF, AUTH_DEMO_POST, get_telegram_link

LOGO_VIDEO_PATH = Path(__file__).resolve().parent.parent / "ads_helper.mp4"


def render_auth_logo() -> None:
    """Логотип-ролик над формой входа / регистрации."""
    if not LOGO_VIDEO_PATH.is_file():
        return

    _pad, col, _pad2 = st.columns([1, 1, 1])
    with col:
        st.video(
            str(LOGO_VIDEO_PATH),
            format="video/mp4",
            loop=True,
            autoplay=True,
            muted=True,
        )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-wrap">
          <div class="hero-badge">⚡ AI-копирайтер · Ads Helper</div>
          <h1 class="hero-title">Рекламные посты<br><span>под вашу площадку</span></h1>
          <p class="hero-sub">
            Бриф + настройки тона и платформы → готовые варианты с CTA и хештегами
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth_demo_post() -> None:
    """Пример готового поста под формой входа."""
    brief = html.escape(AUTH_DEMO_BRIEF)
    post = html.escape(AUTH_DEMO_POST)
    st.markdown(
        f"""
        <div class="demo-showcase">
          <p class="demo-showcase-title">Пример результата · так же будет у вас</p>
          <div class="demo-brief-row">
            <span class="demo-brief-icon">✏️</span>
            <p class="demo-brief-text">
              <strong>Ваш бриф:</strong> {brief}
            </p>
          </div>
          <div class="demo-connector">↓</div>
          <div class="demo-post-shell">
            <div class="demo-post-header">
              <div class="demo-avatar">❄️</div>
              <div>
                <p class="demo-channel-name">КлиматКомфорт</p>
                <p class="demo-channel-meta">готовый пост для соцсетей</p>
              </div>
            </div>
            <div class="demo-post-body">{post}</div>
          </div>
          <p class="demo-footnote">
            Войдите и опишите своё предложение — получите несколько вариантов за секунды
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_variant_card(text: str) -> None:
    safe = html.escape(text)
    st.markdown(
        f"""
        <div class="post-card">
          <div class="post-text">{safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_promo(contact: str, show: bool = True) -> None:
    if not show:
        return
    label, url = get_telegram_link(contact)
    safe_label = html.escape(label)
    safe_url = html.escape(url, quote=True)
    st.markdown(
        f"""
        <hr>
        <div class="promo-banner">
          <h3>📩 Подписка Ads Helper</h3>
          <p>
            <strong style="color:#10B981">990 ₽ / 30 дней</strong> —
            до <strong>100 000 токенов</strong> в месяц на генерации постов
            (примерно сотни постов, в зависимости от длины).<br><br>
            Оплата переводом на карту → напишите нам в Telegram
            с email вашего аккаунта — активируем доступ в течение суток.
          </p>
          <a class="tg-link-btn" href="{safe_url}" target="_blank" rel="noopener noreferrer">
            ✈️ {safe_label}
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_to_history(brief: str, variants: list[str], options_dict: dict) -> None:
    history = st.session_state.setdefault("history", [])
    history.insert(
        0,
        {
            "time": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "brief": brief[:120],
            "variants": variants,
            "options": options_dict,
        },
    )
    st.session_state["history"] = history[:10]


def export_all_text(variants: list[str]) -> str:
    return "\n\n---\n\n".join(variants)
