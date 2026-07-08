"""Legal pages routes — /datenschutz, /impressum, /agb.

These are placeholders until the AVV from the lawyer arrives (see
docs/AVV_LAWYER_BRIEF.md). They are German-only by design: Impressum,
Datenschutzerklärung and AGB are German legal documents, so they always
render in German (``lang="de"``) regardless of the visitor's UI language.
The structure + design match the rest of the landing (Duna design system +
same nav/footer) so the final swap is just a copy update, not a redesign.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from pantra.api.i18n import render

router = APIRouter()


@router.get("/datenschutz", response_class=HTMLResponse)
async def datenschutz(request: Request):
    return render(request, "legal/datenschutz.html.j2", lang="de")


@router.get("/impressum", response_class=HTMLResponse)
async def impressum(request: Request):
    return render(request, "legal/impressum.html.j2", lang="de")


@router.get("/agb", response_class=HTMLResponse)
async def agb(request: Request):
    return render(request, "legal/agb.html.j2", lang="de")
