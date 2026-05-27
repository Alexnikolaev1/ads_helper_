from datetime import date

import streamlit as st

from src.auth.service import get_current_user, logout_user
from src.billing.limits import can_generate, get_usage_status, record_generation
from src.billing.plans import FREE_GENERATIONS_LIMIT, SUBSCRIPTION_PRICE_RUB
from src.config import (
    BRIEF_EXAMPLE,
    LENGTHS,
    PLATFORMS,
    TONES,
    VARIANT_COUNTS,
    GenerationOptions,
    get_admin_password,
    get_api_key,
    get_contact_telegram,
)
from src.db.repository import User
from src.services.gemini import PostGenerator
from src.utils.parser import split_variants
from src.utils.rate_limit import (
    RATE_LIMIT_SECONDS,
    block_if_rate_limited,
    init_rate_limit,
    seconds_until_allowed,
)
from ui.admin import render_admin_panel, render_admin_unlock
from ui.auth_screen import render_auth_screen
from ui.components import (
    export_all_text,
    render_hero,
    render_promo,
    render_variant_card,
    save_to_history,
)
from ui.styles import CSS


def init_session() -> None:
    defaults = {
        "variants": [],
        "generated": False,
        "last_brief": "",
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    init_rate_limit()


def render_usage_sidebar(user: User) -> None:
    status = get_usage_status(user)
    st.markdown("### 📊 Ваш тариф")
    st.caption(f"Аккаунт: **{user.email}**")

    if status.plan == "paid":
        st.success(f"Подписка до **{status.paid_until}**")
        used_pct = (
            min(status.tokens_used / status.tokens_budget, 1.0)
            if status.tokens_budget
            else 0
        )
        st.progress(
            used_pct,
            text=f"{status.tokens_used:,} / {status.tokens_budget:,} токенов".replace(",", " "),
        )
        st.caption(
            f"Осталось **{status.tokens_budget - status.tokens_used:,}** токенов · "
            f"период {status.month_key}".replace(",", " ")
        )
    else:
        st.info("Бесплатный тариф")
        free_pct = min(status.free_used / status.free_limit, 1.0)
        st.progress(
            free_pct,
            text=f"{status.free_used} / {status.free_limit} генераций",
        )
        if status.paid_until and status.paid_until < date.today():
            st.warning("Подписка истекла — остался только бесплатный лимит.")

    if not status.can_generate and status.block_message:
        st.error(status.block_message)

    wait = seconds_until_allowed()
    if wait > 0:
        st.caption(f"⏱ Следующий запрос через **{wait:.1f}** сек.")
    else:
        st.caption(f"Пауза между запросами: **{RATE_LIMIT_SECONDS}** сек.")

    if st.button("Выйти", use_container_width=True):
        logout_user()
        st.rerun()


def render_sidebar(user: User) -> GenerationOptions:
    with st.sidebar:
        render_usage_sidebar(user)
        st.markdown("---")
        st.markdown("### ⚙️ Настройки генерации")
        platform = st.selectbox("Платформа", list(PLATFORMS.keys()))
        tone = st.selectbox("Тон текста", TONES)
        length = st.selectbox("Длина", list(LENGTHS.keys()))
        variant_count = st.selectbox("Количество вариантов", VARIANT_COUNTS, index=1)
        st.markdown("---")
        use_emoji = st.toggle("Эмодзи", value=True)
        include_hashtags = st.toggle("Хештеги", value=True)
        include_cta = st.toggle("Призыв к действию (CTA)", value=True)
        st.markdown("---")
        st.caption(f"Лимит символов: **{PLATFORMS[platform]['max_chars']}**")

        if st.session_state.get("history"):
            st.markdown("### 📜 История (сессия)")
            for i, item in enumerate(st.session_state["history"][:5]):
                label = f"{item['time']} — {item['brief'][:40]}…"
                if st.button(label, key=f"hist_{i}", use_container_width=True):
                    st.session_state["variants"] = item["variants"]
                    st.session_state["generated"] = True
                    st.rerun()

    return GenerationOptions(
        platform=platform,
        tone=tone,
        length=length,
        variant_count=int(variant_count),
        use_emoji=use_emoji,
        include_hashtags=include_hashtags,
        include_cta=include_cta,
    )


def run_generation(
    generator: PostGenerator,
    user: User,
    brief: str,
    options: GenerationOptions,
) -> bool:
    allowed, message = can_generate(user)
    if not allowed:
        st.error(message)
        return False

    if block_if_rate_limited():
        return False

    with st.spinner("Пишу варианты…"):
        try:
            result = generator.generate(brief.strip(), options)
            record_generation(user.id, result.tokens_used)
            variants = split_variants(result.text, max_count=options.variant_count)
            if not variants:
                st.warning("Модель вернула пустой ответ. Попробуйте ещё раз.")
                return False

            st.session_state["variants"] = variants
            st.session_state["generated"] = True
            st.session_state["last_brief"] = brief.strip()
            save_to_history(
                brief.strip(),
                variants,
                {
                    "platform": options.platform,
                    "tone": options.tone,
                    "tokens": result.tokens_used,
                },
            )
            st.caption(f"Списано токенов: **{result.tokens_used:,}**".replace(",", " "))
            return True
        except RuntimeError as e:
            st.error(f"Ошибка генерации: {e}")
        except Exception as e:
            st.error(f"Непредвиденная ошибка: {e}")
    return False


def run() -> None:
    st.set_page_config(
        page_title="Ads Helper — генератор постов",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    user = get_current_user()
    if not user:
        render_auth_screen()
        st.stop()

    st.markdown(CSS, unsafe_allow_html=True)
    init_session()
    render_admin_unlock()
    render_admin_panel()

    render_hero()

    api_key = get_api_key()
    if not api_key:
        st.error(
            "API-ключ Gemini не найден. Добавьте GEMINI_API_KEY в Secrets (см. README)."
        )
        st.stop()

    if not get_admin_password():
        st.warning(
            "ADMIN_PASSWORD не задан — админ-панель подписок недоступна. "
            "Добавьте в Secrets."
        )

    user = get_current_user()
    if not user:
        st.stop()

    usage = get_usage_status(user)
    options = render_sidebar(user)
    contact = get_contact_telegram()

    st.markdown(
        '<div class="hint-box">💡 Чем конкретнее бриф (цена, срок, география, УТП) — '
        "тем точнее посты.</div>",
        unsafe_allow_html=True,
    )

    if not usage.can_generate:
        st.error(usage.block_message)

    if "brief_input" not in st.session_state:
        st.session_state["brief_input"] = ""

    brief = st.text_area(
        "Бриф: опишите предложение",
        placeholder=BRIEF_EXAMPLE,
        height=120,
        key="brief_input",
    )
    st.caption(f"**Пример брифа:** {BRIEF_EXAMPLE}")

    col_gen, col_clear = st.columns([2, 1])
    with col_gen:
        generate_btn = st.button(
            "⚡ Сгенерировать посты",
            type="primary",
            use_container_width=True,
            disabled=not usage.can_generate,
        )
    with col_clear:
        if st.button("Очистить", use_container_width=True):
            st.session_state["variants"] = []
            st.session_state["generated"] = False
            st.rerun()

    generator = PostGenerator(api_key)

    if generate_btn:
        user = get_current_user()
        if not user:
            st.stop()
        if not brief.strip():
            st.warning("Заполните бриф перед генерацией.")
        else:
            run_generation(generator, user, brief, options)

    user = get_current_user()
    usage = get_usage_status(user) if user else usage

    if st.session_state.get("generated") and st.session_state.get("variants"):
        variants = st.session_state["variants"]
        st.markdown("### ✅ Готовые варианты")
        st.download_button(
            label="📥 Скачать все варианты (.txt)",
            data=export_all_text(variants),
            file_name="ads_helper_posts.txt",
            mime="text/plain",
            use_container_width=True,
        )

        for i, variant in enumerate(variants, 1):
            render_variant_card(variant)
            dl_col, regen_col = st.columns(2)
            with dl_col:
                st.download_button(
                    "📥 Скачать",
                    data=variant,
                    file_name=f"post_{i}.txt",
                    mime="text/plain",
                    key=f"dl_{i}",
                    use_container_width=True,
                )
            with regen_col:
                regen_clicked = st.button(
                    "🔄 Другой вариант",
                    key=f"regen_{i}",
                    disabled=not usage.can_generate,
                    use_container_width=True,
                )
            if regen_clicked and user:
                allowed, message = can_generate(user)
                if not allowed:
                    st.error(message)
                elif block_if_rate_limited():
                    pass
                else:
                    regen_options = GenerationOptions(
                        platform=options.platform,
                        tone=options.tone,
                        length=options.length,
                        variant_count=1,
                        use_emoji=options.use_emoji,
                        include_hashtags=options.include_hashtags,
                        include_cta=options.include_cta,
                    )
                    with st.spinner(f"Обновляю вариант {i}…"):
                        try:
                            result = generator.generate(
                                st.session_state.get("last_brief", brief),
                                regen_options,
                            )
                            record_generation(user.id, result.tokens_used)
                            new_variants = split_variants(result.text, max_count=1)
                            if new_variants:
                                variants[i - 1] = new_variants[0]
                                st.session_state["variants"] = variants
                                st.caption(
                                    f"Списано токенов: **{result.tokens_used:,}**".replace(",", " ")
                                )
                                st.rerun()
                        except Exception as e:
                            st.error(str(e))
            st.markdown("---")

    show_promo = usage.plan == "free" or not usage.can_generate
    render_promo(contact, show=show_promo)

    if usage.plan == "free" and usage.free_used < FREE_GENERATIONS_LIMIT:
        st.caption(
            f"Осталось бесплатных генераций: **{FREE_GENERATIONS_LIMIT - usage.free_used}**. "
            f"Подписка — **{SUBSCRIPTION_PRICE_RUB} ₽/мес** после оплаты на карту."
        )
