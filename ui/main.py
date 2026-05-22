import streamlit as st

from src.config import (
    EXAMPLE_PROMPTS,
    LENGTHS,
    PLATFORMS,
    TONES,
    VARIANT_COUNTS,
    GenerationOptions,
    get_api_key,
)
from src.services.gemini import PostGenerator
from src.utils.parser import split_variants
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


def render_sidebar() -> GenerationOptions:
    with st.sidebar:
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


def render_examples() -> None:
    st.markdown("**Быстрые примеры** — нажмите, чтобы подставить в бриф:")
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLE_PROMPTS):
        with cols[i % 2]:
            if st.button(example[:42] + ("…" if len(example) > 42 else ""), key=f"ex_{i}"):
                st.session_state["brief_input"] = example
                st.rerun()


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

    options = render_sidebar()
    max_chars = PLATFORMS[options.platform]["max_chars"]

    st.markdown(
        '<div class="hint-box">💡 Чем конкретнее бриф (цена, срок, география, УТП) — '
        "тем точнее посты.</div>",
        unsafe_allow_html=True,
    )

    if "brief_input" not in st.session_state:
        st.session_state["brief_input"] = ""

    brief = st.text_area(
        "Бриф: опишите предложение",
        placeholder="Например: доставка суши за 45 минут, промокод SUSHI20 на первый заказ",
        height=120,
        key="brief_input",
    )

    render_examples()

    col_gen, col_clear = st.columns([2, 1])
    with col_gen:
        generate_btn = st.button("⚡ Сгенерировать посты", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Очистить", use_container_width=True):
            st.session_state["variants"] = []
            st.session_state["generated"] = False
            st.rerun()

    generator = PostGenerator(api_key)

    if generate_btn:
        if not brief.strip():
            st.warning("Заполните бриф перед генерацией.")
        else:
            with st.spinner("Пишу варианты…"):
                try:
                    raw = generator.generate(brief.strip(), options)
                    variants = split_variants(raw, max_count=options.variant_count)
                    if not variants:
                        st.warning("Модель вернула пустой ответ. Попробуйте ещё раз.")
                    else:
                        st.session_state["variants"] = variants
                        st.session_state["generated"] = True
                        st.session_state["last_brief"] = brief.strip()
                        save_to_history(
                            brief.strip(),
                            variants,
                            {
                                "platform": options.platform,
                                "tone": options.tone,
                            },
                        )
                except RuntimeError as e:
                    st.error(f"Ошибка генерации: {e}")
                except Exception as e:
                    st.error(f"Непредвиденная ошибка: {e}")

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
            render_variant_card(i, variant, max_chars)
            c1, c2 = st.columns([3, 1])
            with c1:
                st.text_area(
                    f"Текст варианта {i} (выделите и Ctrl+C)",
                    value=variant,
                    height=160,
                    key=f"copy_{i}",
                    label_visibility="collapsed",
                )
            with c2:
                st.download_button(
                    f"Скачать #{i}",
                    data=variant,
                    file_name=f"post_variant_{i}.txt",
                    mime="text/plain",
                    key=f"dl_{i}",
                    use_container_width=True,
                )
            if st.button(f"🔄 Перегенерировать #{i}", key=f"regen_{i}"):
                with st.spinner(f"Обновляю вариант {i}…"):
                    try:
                        regen_options = GenerationOptions(
                            platform=options.platform,
                            tone=options.tone,
                            length=options.length,
                            variant_count=1,
                            use_emoji=options.use_emoji,
                            include_hashtags=options.include_hashtags,
                            include_cta=options.include_cta,
                        )
                        raw = generator.generate(
                            st.session_state.get("last_brief", brief),
                            regen_options,
                        )
                        new_variants = split_variants(raw, max_count=1)
                        if new_variants:
                            variants[i - 1] = new_variants[0]
                            st.session_state["variants"] = variants
                            st.rerun()
                    except Exception as e:
                        st.error(str(e))
            st.markdown("---")

    render_promo()
