from datetime import date

import streamlit as st

from src.billing.plans import SUBSCRIPTION_PERIOD_DAYS, SUBSCRIPTION_PRICE_RUB
from src.config import get_admin_password
from src.db.repository import UserRepository


def is_admin_unlocked() -> bool:
    return bool(st.session_state.get("admin_unlocked"))


def render_admin_unlock() -> None:
    if is_admin_unlocked():
        return
    with st.sidebar.expander("🔐 Вход для администратора"):
        pwd = st.text_input("Пароль админа", type="password", key="admin_pwd_input")
        if st.button("Разблокировать", key="admin_unlock_btn"):
            if pwd == get_admin_password():
                st.session_state["admin_unlocked"] = True
                st.rerun()
            else:
                st.error("Неверный пароль")


def render_admin_panel() -> None:
    if not is_admin_unlocked():
        return

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠 Админ: подписки")

    repo = UserRepository()

    with st.sidebar.form("admin_activate"):
        st.caption("После оплаты на карту укажите email клиента")
        email = st.text_input("Email клиента", placeholder="client@mail.ru")
        days = st.number_input(
            "Дней подписки",
            min_value=1,
            max_value=365,
            value=SUBSCRIPTION_PERIOD_DAYS,
        )
        if st.form_submit_button("✅ Активировать подписку", use_container_width=True):
            user = repo.activate_paid(email, days=int(days))
            if user:
                st.sidebar.success(f"Подписка до {user.paid_until}")
                st.rerun()
            else:
                st.sidebar.error("Пользователь с таким email не найден")

    with st.sidebar.form("admin_deactivate"):
        email_off = st.text_input("Email (отключить)", key="admin_off_email")
        if st.form_submit_button("Отключить подписку", use_container_width=True):
            user = repo.deactivate_paid(email_off)
            if user:
                st.sidebar.success("Подписка отключена")
                st.rerun()
            else:
                st.sidebar.error("Пользователь не найден")

    with st.sidebar.expander("Проверить пользователя"):
        check_email = st.text_input("Email", key="admin_check_email")
        if st.button("Показать", key="admin_check_btn"):
            user = repo.get_by_email(check_email)
            if user:
                st.write(f"**Бесплатных использовано:** {user.free_generations_used}/3")
                st.write(f"**Подписка до:** {user.paid_until or '—'}")
                st.write(f"**Токены в месяце:** {user.tokens_used_month}")
            else:
                st.warning("Не найден")

    users = repo.list_users(30)
    if users:
        st.sidebar.caption(f"Последние пользователи ({len(users)})")
        for u in users[:8]:
            paid = u.paid_until.isoformat() if u.paid_until and u.paid_until >= date.today() else "free"
            st.sidebar.caption(f"`{u.email}` · {paid} · gen {u.free_generations_used}")

    if st.sidebar.button("Закрыть админ-панель"):
        st.session_state["admin_unlocked"] = False
        st.rerun()

    st.sidebar.caption(
        f"Тариф: **{SUBSCRIPTION_PRICE_RUB} ₽** / {SUBSCRIPTION_PERIOD_DAYS} дн. · "
        "100 000 токенов/мес"
    )
