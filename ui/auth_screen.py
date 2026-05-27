import streamlit as st

from src.auth.service import login_user, register_user
from ui.styles import CSS


def render_auth_screen() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero-wrap">
          <div class="hero-badge">⚡ Ads Helper</div>
          <h1 class="hero-title">Вход в<br><span>генератор постов</span></h1>
          <p class="hero-sub">3 бесплатные генерации · подписка после оплаты на карту</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["Вход", "Регистрация"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти", type="primary", use_container_width=True)
        if submitted:
            ok, msg = login_user(email, password)
            if ok:
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        with st.form("register_form"):
            email_r = st.text_input("Email", key="reg_email", placeholder="you@example.com")
            password_r = st.text_input("Пароль", type="password", key="reg_pass")
            password_r2 = st.text_input("Повторите пароль", type="password", key="reg_pass2")
            submitted_r = st.form_submit_button(
                "Создать аккаунт", type="primary", use_container_width=True
            )
        if submitted_r:
            ok, msg = register_user(email_r, password_r, password_r2)
            if ok:
                st.success("Аккаунт создан!")
                st.rerun()
            else:
                st.error(msg)
