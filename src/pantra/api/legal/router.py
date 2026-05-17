"""Legal pages routes — /datenschutz, /impressum, /agb.

These are placeholders until the AVV from the lawyer arrives (see
docs/AVV_LAWYER_BRIEF.md). The current content explicitly flags the
placeholder state with a visible banner so visitors understand it's
work-in-progress. The structure + design match the rest of the landing
(Duna design system + same nav/footer) so the final swap is just a copy
update, not a redesign.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[3].parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/datenschutz", response_class=HTMLResponse)
async def datenschutz(request: Request):
    return templates.TemplateResponse(
        request, "legal/datenschutz.html.j2", {"html_lang": "es"}
    )


@router.get("/impressum", response_class=HTMLResponse)
async def impressum(request: Request):
    return templates.TemplateResponse(
        request, "legal/impressum.html.j2", {"html_lang": "es"}
    )


@router.get("/agb", response_class=HTMLResponse)
async def agb(request: Request):
    return templates.TemplateResponse(
        request, "legal/agb.html.j2", {"html_lang": "es"}
    )
