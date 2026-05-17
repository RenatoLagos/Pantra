"""Conversation quota enforcement (pricing v4 hard limits).

Pantra prices by conversations/month per tier. This module owns:
  - Plan resolution from `business.config["plan"]` (no schema field at MVP).
  - Counting non-demo conversations created this calendar month.
  - The quota check that gates inbound processing when the cap is hit.
  - The owner notification (one Telegram/email per day, via HandoffTask).

Demo businesses are never quota-checked — same `is_demo` bypass used
elsewhere in the pipeline. Their LLM cost is treated as marketing.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.models import Business, Conversation, HandoffStatus, HandoffTask

# Hard limits per pricing v4 tier. Hard-coded for MVP — when we wire
# Stripe metered billing we'll move these to a Plan table or config.
PLAN_LIMITS: dict[str, int] = {
    "solo": 600,
    "solo_plus": 2000,
}

# Plan applied when business.config has no explicit "plan" key. Solo is
# the conservative default — caps cost on any unconfigured tenant.
DEFAULT_PLAN = "solo"


@dataclass(frozen=True, slots=True)
class QuotaStatus:
    plan: str
    limit: int
    used: int

    @property
    def exceeded(self) -> bool:
        return self.used >= self.limit

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)


def get_plan(business: Business) -> str:
    plan = (business.config or {}).get("plan")
    if isinstance(plan, str) and plan in PLAN_LIMITS:
        return plan
    return DEFAULT_PLAN


def get_limit(plan: str) -> int:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS[DEFAULT_PLAN])


def _utc_month_start(now: datetime | None = None) -> datetime:
    n = now or datetime.now(tz=timezone.utc)
    return n.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _utc_today_start(now: datetime | None = None) -> datetime:
    n = now or datetime.now(tz=timezone.utc)
    return n.replace(hour=0, minute=0, second=0, microsecond=0)


async def count_conversations_this_month(
    session: AsyncSession,
    business_id: uuid.UUID,
) -> int:
    stmt = select(func.count(Conversation.id)).where(
        Conversation.business_id == business_id,
        Conversation.created_at >= _utc_month_start(),
        Conversation.is_demo.is_(False),
    )
    return int((await session.execute(stmt)).scalar_one() or 0)


async def quota_status(session: AsyncSession, business: Business) -> QuotaStatus:
    plan = get_plan(business)
    limit = get_limit(plan)
    used = await count_conversations_this_month(session, business.id)
    return QuotaStatus(plan=plan, limit=limit, used=used)


async def maybe_notify_quota_exceeded(
    session: AsyncSession,
    business: Business,
    conversation: Conversation,
    status: QuotaStatus,
) -> bool:
    """Create + dispatch ONE HandoffTask per day for this business.

    Uses the existing HandoffTask + dispatch wiring so the owner sees the
    alert on Telegram and email. Returns True iff a new task was created.
    """
    existing = await session.execute(
        select(HandoffTask.id).where(
            HandoffTask.business_id == business.id,
            HandoffTask.reason == "quota_exceeded",
            HandoffTask.created_at >= _utc_today_start(),
        )
    )
    if existing.first():
        return False

    task = HandoffTask(
        business_id=business.id,
        conversation_id=conversation.id,
        reason="quota_exceeded",
        priority=1,
        status=HandoffStatus.open,
        summary=(
            f"Cuota mensual excedida — plan '{status.plan}' "
            f"({status.used}/{status.limit} conversaciones este mes). "
            f"Pantra dejó de procesar mensajes nuevos. "
            f"Upgradeá el plan o activá billing de excedente "
            f"(€0,15/conversación) para reanudar."
        ),
    )
    session.add(task)
    await session.flush()

    # Avoid an import cycle: handoff.dispatch pulls in services indirectly
    # through the email/telegram modules.
    from pantra.handoff import dispatch as dispatch_handoff

    await dispatch_handoff(
        task,
        business_id=business.id,
        conversation_id=conversation.id,
        is_demo=business.is_demo,
    )
    return True
