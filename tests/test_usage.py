"""Unit tests for services.usage — pricing v4 hard limits.

DB-backed paths (count_conversations_this_month, maybe_notify_quota_exceeded)
need a real Postgres + the schema; those are exercised in integration tests.
Here we only cover the pure helpers + the QuotaStatus invariants.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from pantra.services import usage


def _biz(plan_value):
    """Build a stand-in business with the bare attributes usage cares about."""
    config = {"plan": plan_value} if plan_value is not None else None
    return SimpleNamespace(config=config)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("solo", "solo"),
        ("solo_plus", "solo_plus"),
        # Unknown values fall back to the conservative default (solo, 600 cap).
        ("enterprise", "solo"),
        ("", "solo"),
        (None, "solo"),
        # Non-strings are ignored too.
        (42, "solo"),
    ],
)
def test_get_plan_resolves(raw, expected):
    assert usage.get_plan(_biz(raw)) == expected


def test_get_plan_when_config_is_none():
    biz = SimpleNamespace(config=None)
    assert usage.get_plan(biz) == usage.DEFAULT_PLAN


def test_get_plan_when_config_has_no_plan_key():
    biz = SimpleNamespace(config={"opening_hours": "9-17"})
    assert usage.get_plan(biz) == usage.DEFAULT_PLAN


def test_get_limit_known_plans():
    assert usage.get_limit("solo") == 600
    assert usage.get_limit("solo_plus") == 2000


def test_get_limit_unknown_plan_falls_back():
    # Unknown tier falls back to the default plan's cap (Solo). This is
    # intentionally conservative: a bug that drops a tier should never
    # uncap a tenant.
    assert usage.get_limit("whatever") == usage.PLAN_LIMITS[usage.DEFAULT_PLAN]


def test_quota_status_exceeded_at_or_above_limit():
    # At the boundary, the plan is considered exceeded (used == limit means
    # the cap has been spent — no more room).
    s = usage.QuotaStatus(plan="solo", limit=600, used=600)
    assert s.exceeded is True
    assert s.remaining == 0


def test_quota_status_below_limit():
    s = usage.QuotaStatus(plan="solo_plus", limit=2000, used=1500)
    assert s.exceeded is False
    assert s.remaining == 500


def test_quota_status_well_above_limit():
    s = usage.QuotaStatus(plan="solo", limit=600, used=750)
    assert s.exceeded is True
    # Remaining is clamped to 0 — never negative.
    assert s.remaining == 0
