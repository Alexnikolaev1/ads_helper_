import streamlit as st

from src.config import (
    BRIEF_EXAMPLE,
    LENGTHS,
    PLATFORMS,
    TONES,
    VARIANT_COUNTS,
    GenerationOptions,
    get_api_key,
)
from src.services.gemini import PostGenerator
from src.utils.parser import split_variants
from src.utils.rate_limit import (
    RATE_LIMIT_SECONDS,
    block_if_rate_limited,
    init_rate_limit,
    seconds_until_allowed,
)
from src.utils.token_budget import (
    LIMIT_MESSAGE,
    get_budget_status,
    init_token_budget,
    is_budget_exhausted,
    record_token_usage,
)
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
    init_token_budget()
    init_rate_limit()


def render_token_budget_sidebar() -> None:
    status = get_budget_status()
    used_pct = min(status.used / status.budget, 1.0) if status.budget else 0.0

    st.markdown("### 📊 Бюджет токенов")
    st.caption(f"Период: {status.month_key} (обновляется каждый месяц)")

    st.progress(
        used_pct,
        text=f"{status.used:,} / {status.budget:,} токенов".replace(",", " "),
    )
    st.caption(f"Осталось: **{status.remaining:,}** токенов".replace(",", " "))

    if status.exhausted:
        st.error(LIMIT_MESSAGE)

    wait = seconds_until_allowed()
    if wait > 0:
        st.caption(f"⏱ Следующий запрос через **{wait:.1f}** сек.")
    else:
        st.caption(f"Интервал между запросами: **{RATE_LIMIT_SECONDS}** сек.")


def render_sidebar() -> GenerationOptions:
    with st.sidebar:
        render_token_budget_sidebar()
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
            st.markdown("### 📜 История")
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
    brief: str,
    options: GenerationOptions,
) -> bool:
    """Генерация с учётом лимита токенов и rate limit. Возвращает True при успехе."""
    if is_budget_exhausted():
        st.error(LIMIT_MESSAGE)
        return False

    if block_if_rate_limited():
        return False

    with st.spinner("Пишу варианты…"):
        try:
            result = generator.generate(brief.strip(), options)
            record_token_usage(result.tokens_used)
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
            st.caption(f"Списано токенов за запрос: **{result.tokens_used:,}**".replace(",", " "))
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
    st.markdown(CSS, unsafe_allow_html=True)
    init_session()
    render_hero()

    api_key = get_api_key()
    if not api_key:
        st.error(
            "API-ключ Gemini не найден. Создайте `.streamlit/secrets.toml` "
            "или файл `.env` с `GEMINI_API_KEY` (см. README)."
        )
        st.stop()

    budget_exhausted = is_budget_exhausted()
    options = render_sidebar()

    st.markdown(
        '<div class="hint-box">💡 Чем конкретнее бриф (цена, срок, география, УТП) — '
        "тем точнее посты.</div>",
        unsafe_allow_html=True,
    )

    if budget_exhausted:
        st.error(LIMIT_MESSAGE)

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
            disabled=budget_exhausted,
        )
    with col_clear:
        if st.button("Очистить", use_container_width=True):
            st.session_state["variants"] = []
            st.session_state["generated"] = False
            st.rerun()

    generator = PostGenerator(api_key)

    if generate_btn:
        if budget_exhausted:
            st.error(LIMIT_MESSAGE)
        elif not brief.strip():
            st.warning("Заполните бриф перед генерацией.")
        else:
            run_generation(generator, brief, options)

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
                    disabled=budget_exhausted,
                    use_container_width=True,
                )
            if regen_clicked:
                if is_budget_exhausted():
                    st.error(LIMIT_MESSAGE)
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
                            record_token_usage(result.tokens_used)
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

    render_promo()
