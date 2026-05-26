import html
from datetime import datetime

import streamlit as st


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


def render_promo(contact: str = "@your_contact") -> None:
    st.markdown(
        f"""
        <hr>
        <div class="promo-banner">
          <h3>🚀 Нужен безлимит и шаблоны под нишу?</h3>
          <p>
            Подписка <strong style="color:#10B981">990 ₽/мес</strong> —
            неограниченные генерации, приоритет и кастомные промпты.<br><br>
            Telegram: <strong style="color:#10B981">{html.escape(contact)}</strong>
          </p>
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
