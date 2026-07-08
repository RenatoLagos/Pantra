"""Landing routes — /einzelpraxis (outbound, single tier) and /pricing (organic).

Language resolution and translation live in the shared ``pantra.api.i18n``
module; both pages render DE (default) or EN via the central catalog.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from pantra.api.i18n import render

router = APIRouter()


@router.get("/einzelpraxis", response_class=HTMLResponse)
async def einzelpraxis(request: Request):
    """Outbound landing — single-tier (Solo Plus €349) for digital-native dentists."""
    return render(request, "landing/einzelpraxis.html.j2")


@router.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    """Public pricing page — comparative (Solo / Solo Plus / Multi coming soon).

    Distinct from /einzelpraxis: this is for organic traffic, referrals, and
    SEO. Multi-tier comparison + add-ons + pricing-specific FAQ.
    """
    return render(request, "landing/pricing.html.j2")
