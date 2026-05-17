"""Landing routes — /einzelpraxis (outbound destination, single tier)."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[3].parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Languages we render today. The German copy needs native review before
# we flip the default — until then the page renders in Spanish for founder
# review with TRANSLATE-DE markers in the source.
SUPPORTED_LANGS = {"es", "de", "en"}


def _resolve_lang(request: Request) -> str:
    requested = request.query_params.get("lang")
    if requested and requested.lower() in SUPPORTED_LANGS:
        return requested.lower()
    return "es"


@router.get("/einzelpraxis", response_class=HTMLResponse)
async def einzelpraxis(request: Request):
    """Outbound landing — single-tier (Solo Plus €349) for digital-native dentists."""
    return templates.TemplateResponse(
        request,
        "landing/einzelpraxis.html.j2",
        {
            "html_lang": _resolve_lang(request),
        },
    )


@router.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request):
    """Public pricing page — comparative (Solo / Solo Plus / Multi coming soon).

    Distinct from /einzelpraxis: this is for organic traffic, referrals, and
    SEO. Multi-tier comparison + add-ons + pricing-specific FAQ.
    """
    return templates.TemplateResponse(
        request,
        "landing/pricing.html.j2",
        {
            "html_lang": _resolve_lang(request),
        },
    )
