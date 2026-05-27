import streamlit as st


def setup_page(*, logged_in: bool) -> None:
    """
    logged_in=False — экран входа: узкая колонка, сайдбар скрыт.
    logged_in=True — рабочий стол: wide + сайдбар с настройками.
    """
    if logged_in:
        st.set_page_config(
            page_title="Ads Helper — генератор постов",
            page_icon="⚡",
            layout="wide",
            initial_sidebar_state="expanded",
        )
    else:
        st.set_page_config(
            page_title="Ads Helper — вход",
            page_icon="⚡",
            layout="centered",
            initial_sidebar_state="collapsed",
        )
