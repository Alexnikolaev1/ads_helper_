from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from src.billing.plans import (
    FREE_GENERATIONS_LIMIT,
    FREE_LIMIT_MESSAGE,
    PAID_EXPIRED_MESSAGE,
    PAID_MONTHLY_TOKEN_BUDGET,
    PAID_TOKEN_LIMIT_MESSAGE,
)
from src.db.repository import User, UserRepository
from src.utils.token_budget import extract_token_count


@dataclass(frozen=True)
class UsageStatus:
    plan: str  # "free" | "paid"
    can_generate: bool
    block_message: str
    free_used: int
    free_limit: int
    tokens_used: int
    tokens_budget: int
    paid_until: date | None
    month_key: str


def _current_month_key() -> str:
    return datetime.now().strftime("%Y-%m")


def _is_paid_active(user: User) -> bool:
    if not user.paid_until:
        return False
    return user.paid_until >= date.today()


def get_usage_status(user: User) -> UsageStatus:
    month_key = _current_month_key()
    if _is_paid_active(user):
        tokens_used = (
            user.tokens_used_month if user.token_month == month_key else 0
        )
        remaining = PAID_MONTHLY_TOKEN_BUDGET - tokens_used
        exhausted = remaining <= 0
        return UsageStatus(
            plan="paid",
            can_generate=not exhausted,
            block_message=PAID_TOKEN_LIMIT_MESSAGE if exhausted else "",
            free_used=user.free_generations_used,
            free_limit=FREE_GENERATIONS_LIMIT,
            tokens_used=tokens_used,
            tokens_budget=PAID_MONTHLY_TOKEN_BUDGET,
            paid_until=user.paid_until,
            month_key=month_key,
        )

    free_exhausted = user.free_generations_used >= FREE_GENERATIONS_LIMIT
    expired_paid = user.paid_until is not None and user.paid_until < date.today()
    block = FREE_LIMIT_MESSAGE
    if expired_paid and free_exhausted:
        block = PAID_EXPIRED_MESSAGE + " " + FREE_LIMIT_MESSAGE

    return UsageStatus(
        plan="free",
        can_generate=not free_exhausted,
        block_message=block if free_exhausted else "",
        free_used=user.free_generations_used,
        free_limit=FREE_GENERATIONS_LIMIT,
        tokens_used=0,
        tokens_budget=0,
        paid_until=user.paid_until,
        month_key=month_key,
    )


def can_generate(user: User) -> tuple[bool, str]:
    status = get_usage_status(user)
    if status.can_generate:
        return True, ""
    return False, status.block_message


def record_generation(user_id: int, tokens: int) -> None:
    repo = UserRepository()
    user = repo.get_by_id(user_id)
    if not user:
        return

    month_key = _current_month_key()
    if _is_paid_active(user):
        repo.add_tokens(user_id, tokens, month_key)
    else:
        repo.increment_free_generation(user_id)


def record_generation_from_response(user_id: int, response: object) -> int:
    tokens = extract_token_count(response)
    record_generation(user_id, tokens)
    return tokens
