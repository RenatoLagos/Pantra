"""Cost estimation for LLM runs (analytics).

Anthropic prompt-caching pricing model:
  - input tokens:          full rate
  - cache_read_tokens:     ~10% of input rate
  - cache_creation_tokens: ~125% of input rate (one-time write penalty)
  - output tokens:         full output rate

All rates per 1M tokens, in USD. We convert to EUR at the end using a
fixed conversion (no FX lookup in this module — the rate is documented
as a constant so it's easy to update when needed).

This module is read-only over ``ai_runs``. It never writes. The cost
column on AIRun is left null on the write path; cost is computed on
read so we can re-price historical rows after Anthropic price changes
without backfilling.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.models import AIRun

# USD per 1 million tokens (Anthropic published rates, May 2026).
# Update here when Anthropic price-drops a tier.
RATES: dict[str, dict[str, float]] = {
    "claude-sonnet-4-6":       {"input": 3.00, "output": 15.00},
    "claude-sonnet-4-5":       {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output":  5.00},
    "claude-haiku-4-5":        {"input": 1.00, "output":  5.00},
    "claude-opus-4-7":         {"input": 5.00, "output": 25.00},
    "claude-opus-4-6":         {"input": 5.00, "output": 25.00},
}

# Cache multipliers — Anthropic ephemeral cache.
CACHE_READ_MULTIPLIER = 0.10      # 10% of input rate for cache hits
CACHE_CREATION_MULTIPLIER = 1.25  # 125% of input rate for cache writes

# Approximate USD→EUR. Hard-coded; FX volatility is small relative to
# precision needed for unit-economics. Update via env if needed later.
USD_TO_EUR = 0.92


@dataclass(frozen=True, slots=True)
class RunCost:
    """USD + EUR cost for a single AIRun, broken down by token category."""

    input_cost_usd: float
    cache_read_cost_usd: float
    cache_creation_cost_usd: float
    output_cost_usd: float

    @property
    def total_usd(self) -> float:
        return (
            self.input_cost_usd
            + self.cache_read_cost_usd
            + self.cache_creation_cost_usd
            + self.output_cost_usd
        )

    @property
    def total_eur(self) -> float:
        return self.total_usd * USD_TO_EUR


def cost_for_run(run: AIRun) -> RunCost:
    """Compute USD + EUR cost for a single AIRun.

    Unknown models return zero cost (logged at analytics time). Missing
    tokens are treated as zero.
    """
    rate = RATES.get(run.model)
    if rate is None:
        return RunCost(0.0, 0.0, 0.0, 0.0)

    input_tokens = run.input_tokens or 0
    cache_read = run.cache_read_tokens or 0
    cache_creation = run.cache_creation_tokens or 0
    output_tokens = run.output_tokens or 0

    # Anthropic's `input_tokens` field excludes cache_read + cache_creation
    # (they're reported as separate counters), so we don't need to
    # subtract them here.
    input_rate = rate["input"]
    output_rate = rate["output"]

    return RunCost(
        input_cost_usd=(input_tokens / 1_000_000) * input_rate,
        cache_read_cost_usd=(cache_read / 1_000_000) * input_rate * CACHE_READ_MULTIPLIER,
        cache_creation_cost_usd=(cache_creation / 1_000_000) * input_rate * CACHE_CREATION_MULTIPLIER,
        output_cost_usd=(output_tokens / 1_000_000) * output_rate,
    )


@dataclass(frozen=True, slots=True)
class UsageSummary:
    """Aggregated usage + cost for a window (business or global)."""

    runs: int
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    cost_usd: float
    by_role: dict[str, int]            # runs per role (classifier/main/fast_reply)
    by_model: dict[str, int]           # runs per model
    cache_hit_rate: float              # cache_read / (cache_read + input)

    @property
    def cost_eur(self) -> float:
        return self.cost_usd * USD_TO_EUR

    @property
    def baseline_cost_no_cache_usd(self) -> float:
        """What we would have paid if cache_read tokens were billed at full input rate.

        Useful to quantify the saving from prompt caching.
        """
        # We don't know each row's model here, so this is an approximation
        # using the average input rate weighted by runs. For the MVP admin
        # endpoint, an upper-bound estimate is fine.
        # Conservative: assume Sonnet-tier ($3/Mtok) as worst-case input rate.
        sonnet_input_rate = RATES["claude-sonnet-4-6"]["input"]
        return self.cost_usd + (
            self.cache_read_tokens / 1_000_000
        ) * sonnet_input_rate * (1.0 - CACHE_READ_MULTIPLIER)

    @property
    def cache_savings_usd(self) -> float:
        return self.baseline_cost_no_cache_usd - self.cost_usd


def _month_start_utc(now: datetime | None = None) -> datetime:
    n = now or datetime.now(tz=timezone.utc)
    return n.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def summarize_runs(
    session: AsyncSession,
    *,
    business_id: uuid.UUID | None = None,
    since: datetime | None = None,
) -> UsageSummary:
    """Aggregate ai_runs in the window.

    No business_id → global summary across all businesses.
    No `since` → current calendar month (UTC).
    """
    since = since or _month_start_utc()

    # Pull aggregated columns in one query.
    base = select(
        func.count(AIRun.id).label("runs"),
        func.coalesce(func.sum(AIRun.input_tokens), 0).label("input_tokens"),
        func.coalesce(func.sum(AIRun.output_tokens), 0).label("output_tokens"),
        func.coalesce(func.sum(AIRun.cache_read_tokens), 0).label("cache_read"),
        func.coalesce(func.sum(AIRun.cache_creation_tokens), 0).label("cache_creation"),
    ).where(AIRun.created_at >= since)

    if business_id is not None:
        # AIRun lives under conversation → business. We filter via subquery
        # to avoid joining for the totals.
        from pantra.models import Conversation
        conv_subq = select(Conversation.id).where(
            Conversation.business_id == business_id
        ).scalar_subquery()
        base = base.where(AIRun.conversation_id.in_(conv_subq))

    totals = (await session.execute(base)).one()

    # Group-by role and model for breakdown.
    role_stmt = (
        select(AIRun.role, func.count(AIRun.id))
        .where(AIRun.created_at >= since)
        .group_by(AIRun.role)
    )
    model_stmt = (
        select(AIRun.model, func.count(AIRun.id))
        .where(AIRun.created_at >= since)
        .group_by(AIRun.model)
    )
    if business_id is not None:
        from pantra.models import Conversation
        conv_subq = select(Conversation.id).where(
            Conversation.business_id == business_id
        ).scalar_subquery()
        role_stmt = role_stmt.where(AIRun.conversation_id.in_(conv_subq))
        model_stmt = model_stmt.where(AIRun.conversation_id.in_(conv_subq))

    by_role = {row[0]: row[1] for row in (await session.execute(role_stmt)).all()}
    by_model = {row[0]: row[1] for row in (await session.execute(model_stmt)).all()}

    # Total cost via per-row replay (so the rates dict is the source of truth).
    cost_query = select(AIRun).where(AIRun.created_at >= since)
    if business_id is not None:
        from pantra.models import Conversation
        conv_subq = select(Conversation.id).where(
            Conversation.business_id == business_id
        ).scalar_subquery()
        cost_query = cost_query.where(AIRun.conversation_id.in_(conv_subq))

    runs_objs = (await session.execute(cost_query)).scalars().all()
    total_cost_usd = sum(cost_for_run(r).total_usd for r in runs_objs)

    cache_read = int(totals.cache_read or 0)
    input_t = int(totals.input_tokens or 0)
    cache_hit_rate = cache_read / (cache_read + input_t) if (cache_read + input_t) > 0 else 0.0

    return UsageSummary(
        runs=int(totals.runs or 0),
        input_tokens=input_t,
        output_tokens=int(totals.output_tokens or 0),
        cache_read_tokens=cache_read,
        cache_creation_tokens=int(totals.cache_creation or 0),
        cost_usd=total_cost_usd,
        by_role=by_role,
        by_model=by_model,
        cache_hit_rate=cache_hit_rate,
    )
