"""Admin endpoints — token-guarded, internal use only.

All routes here require a bearer token matching ``settings.admin_token``.
If ``admin_token`` is empty (default), every request 403s so a forgotten
secret can't accidentally expose data in production. The token guard is
not auth — it's a "don't expose this externally" check; put a real
auth layer in front of /admin/* if you ever route public traffic here.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.config import settings
from pantra.db import session_scope
from pantra.models import Business
from pantra.services import cost as cost_svc
from pantra.services import usage as usage_svc

router = APIRouter(prefix="/admin", tags=["admin"])

TEMPLATES_DIR = Path(__file__).resolve().parents[3].parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _require_admin(authorization: str | None = Header(default=None)) -> None:
    """Bearer-token guard. Empty token (default) blocks all access."""
    if not settings.admin_token:
        raise HTTPException(status_code=403, detail="admin endpoints disabled")
    expected = f"Bearer {settings.admin_token}"
    if authorization != expected:
        raise HTTPException(status_code=403, detail="invalid admin token")


async def _open_session():
    """Yield an async session via the existing session_scope() helper.

    FastAPI's dependency-injection expects an async generator, but
    session_scope is an async context manager — we adapt here.
    """
    async with session_scope() as session:
        yield session


@router.get("/usage", dependencies=[Depends(_require_admin)])
async def get_usage(
    business_id: str | None = Query(default=None, description="Filter to a single business UUID"),
    session: AsyncSession = Depends(_open_session),
) -> dict:
    """Current-month usage + cost summary.

    Aggregates ai_runs since the start of the current UTC month. If
    ``business_id`` is omitted, returns the global rollup across all
    tenants.
    """
    biz_uuid = None
    if business_id:
        try:
            biz_uuid = uuid.UUID(business_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"invalid business_id: {e}") from e

    summary = await cost_svc.summarize_runs(session, business_id=biz_uuid)

    return {
        "period": {
            "since": cost_svc._month_start_utc().isoformat(),
            "until": datetime.now(tz=timezone.utc).isoformat(),
        },
        "filter": {"business_id": str(biz_uuid) if biz_uuid else None},
        "runs": summary.runs,
        "tokens": {
            "input": summary.input_tokens,
            "output": summary.output_tokens,
            "cache_read": summary.cache_read_tokens,
            "cache_creation": summary.cache_creation_tokens,
        },
        "cost": {
            "actual_usd": round(summary.cost_usd, 4),
            "actual_eur": round(summary.cost_eur, 4),
            "baseline_no_cache_usd": round(summary.baseline_cost_no_cache_usd, 4),
            "cache_savings_usd": round(summary.cache_savings_usd, 4),
            "cache_savings_pct": round(
                (summary.cache_savings_usd / summary.baseline_cost_no_cache_usd * 100)
                if summary.baseline_cost_no_cache_usd > 0 else 0.0,
                2,
            ),
        },
        "cache_hit_rate_pct": round(summary.cache_hit_rate * 100, 2),
        "by_role": summary.by_role,
        "by_model": summary.by_model,
    }


async def _build_quotas_rows(session: AsyncSession) -> list[dict]:
    """Quota status per non-demo business, sorted by utilization desc."""
    biz_stmt = select(Business).where(Business.is_demo.is_(False))
    businesses = (await session.execute(biz_stmt)).scalars().all()

    rows = []
    for biz in businesses:
        q = await usage_svc.quota_status(session, biz)
        rows.append({
            "business_id": str(biz.id),
            "business_name": biz.name,
            "plan": q.plan,
            "limit": q.limit,
            "used": q.used,
            "remaining": q.remaining,
            "exceeded": q.exceeded,
            "utilization_pct": round((q.used / q.limit * 100) if q.limit > 0 else 0.0, 1),
        })
    rows.sort(key=lambda r: r["utilization_pct"], reverse=True)
    return rows


@router.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(_require_admin)])
async def dashboard(
    request: Request,
    session: AsyncSession = Depends(_open_session),
):
    """HTML dashboard — same data as /admin/usage + /admin/usage/quotas,
    rendered server-side. No JS deps. Refresh the page to reload."""
    summary = await cost_svc.summarize_runs(session)
    quotas = await _build_quotas_rows(session)

    usage_payload = {
        "runs": summary.runs,
        "tokens": {
            "input": summary.input_tokens,
            "output": summary.output_tokens,
            "cache_read": summary.cache_read_tokens,
            "cache_creation": summary.cache_creation_tokens,
        },
        "cost": {
            "actual_usd": summary.cost_usd,
            "actual_eur": summary.cost_eur,
            "cache_savings_usd": summary.cache_savings_usd,
            "cache_savings_pct": (
                summary.cache_savings_usd / summary.baseline_cost_no_cache_usd * 100
                if summary.baseline_cost_no_cache_usd > 0 else 0.0
            ),
        },
        "cache_hit_rate_pct": summary.cache_hit_rate * 100,
        "by_role": summary.by_role,
        "by_model": summary.by_model,
    }

    return templates.TemplateResponse(
        request,
        "admin/dashboard.html.j2",
        {
            "period": {
                "since": cost_svc._month_start_utc().strftime("%Y-%m-%d"),
                "until": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            },
            "usage": usage_payload,
            "quotas": quotas,
        },
    )


@router.get("/usage/quotas", dependencies=[Depends(_require_admin)])
async def get_quotas(
    session: AsyncSession = Depends(_open_session),
) -> dict:
    """Quota status (pricing v4 hard limits) for every non-demo business."""
    rows = await _build_quotas_rows(session)
    return {
        "period": {
            "since": cost_svc._month_start_utc().isoformat(),
            "until": datetime.now(tz=timezone.utc).isoformat(),
        },
        "businesses": rows,
    }
