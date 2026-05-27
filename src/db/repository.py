from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from src.billing.plans import SUBSCRIPTION_PERIOD_DAYS
from src.db.database import get_connection, init_database


@dataclass
class User:
    id: int
    email: str
    free_generations_used: int
    paid_until: date | None
    tokens_used_month: int
    token_month: str | None

    @classmethod
    def from_row(cls, row: Any) -> User:
        paid_raw = row["paid_until"]
        paid_until = None
        if paid_raw:
            paid_until = date.fromisoformat(paid_raw[:10])
        return cls(
            id=row["id"],
            email=row["email"],
            free_generations_used=row["free_generations_used"],
            paid_until=paid_until,
            tokens_used_month=row["tokens_used_month"],
            token_month=row["token_month"],
        )


class UserRepository:
    def __init__(self) -> None:
        init_database()

    def get_by_email(self, email: str) -> User | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
                (email.strip().lower(),),
            ).fetchone()
        return User.from_row(row) if row else None

    def get_by_id(self, user_id: int) -> User | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return User.from_row(row) if row else None

    def get_password_hash(self, email: str) -> str | None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE email = ? COLLATE NOCASE",
                (email.strip().lower(),),
            ).fetchone()
        return row["password_hash"] if row else None

    def create_user(self, email: str, password_hash: str) -> User:
        now = datetime.utcnow().isoformat()
        normalized = email.strip().lower()
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (normalized, password_hash, now),
            )
            conn.commit()
            user_id = cur.lastrowid
        user = self.get_by_id(int(user_id))
        if not user:
            raise RuntimeError("Не удалось создать пользователя")
        return user

    def increment_free_generation(self, user_id: int) -> None:
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET free_generations_used = free_generations_used + 1 WHERE id = ?",
                (user_id,),
            )
            conn.commit()

    def add_tokens(self, user_id: int, tokens: int, month_key: str) -> None:
        user = self.get_by_id(user_id)
        if not user:
            return
        if user.token_month != month_key:
            used = tokens
        else:
            used = user.tokens_used_month + tokens
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE users
                SET tokens_used_month = ?, token_month = ?
                WHERE id = ?
                """,
                (used, month_key, user_id),
            )
            conn.commit()

    def activate_paid(
        self,
        email: str,
        days: int = SUBSCRIPTION_PERIOD_DAYS,
    ) -> User | None:
        user = self.get_by_email(email)
        if not user:
            return None
        today = date.today()
        start = user.paid_until if user.paid_until and user.paid_until >= today else today
        paid_until = start + timedelta(days=days)
        month_key = today.strftime("%Y-%m")
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE users
                SET paid_until = ?, tokens_used_month = 0, token_month = ?
                WHERE id = ?
                """,
                (paid_until.isoformat(), month_key, user.id),
            )
            conn.commit()
        return self.get_by_id(user.id)

    def deactivate_paid(self, email: str) -> User | None:
        user = self.get_by_email(email)
        if not user:
            return None
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET paid_until = NULL WHERE id = ?",
                (user.id,),
            )
            conn.commit()
        return self.get_by_id(user.id)

    def reset_free_generations(self, email: str) -> User | None:
        user = self.get_by_email(email)
        if not user:
            return None
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET free_generations_used = 0 WHERE id = ?",
                (user.id,),
            )
            conn.commit()
        return self.get_by_id(user.id)

    def list_users(self, limit: int = 50) -> list[User]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [User.from_row(r) for r in rows]
