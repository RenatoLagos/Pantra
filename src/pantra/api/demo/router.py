from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Cookie, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, update

from pantra.channels.web.normalizer import WebInbound, to_inbound_message
from pantra.config import settings
from pantra.db import session_scope
from pantra.logging import log
from pantra.models import Business, ChannelType, Conversation, ConversationStatus, Customer
from pantra.services.conversation import OutboundMessage, process_inbound

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[3].parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

VERTICALS = {
    "dental": {"slug": "demo-dental", "name": "Clínica Dental Berlin Mitte", "emoji": "🦷"},
}

SESSION_COOKIE = "pantra_demo_session"


@router.get("/demo")
async def landing() -> Response:
    # MVP focuses on dental clinics only — skip the selector and go straight in.
    return RedirectResponse(url="/demo/dental")


@router.get("/demo/{vertical}", response_class=HTMLResponse)
async def chat_page(vertical: str, request: Request, response: Response):
    if vertical not in VERTICALS:
        raise HTTPException(status_code=404, detail="unknown vertical")

    # Demo UX: every page load starts a fresh chat. Prevents stale context
    # from a previous visit leaking into what the prospect perceives as a
    # new conversation. The cookie is rotated; the prior conversation stays
    # in DB for analytics.
    session_id = uuid.uuid4().hex
    info = VERTICALS[vertical]

    resp = templates.TemplateResponse(
        request,
        "demo/chat.html",
        {
            "vertical": vertical,
            "vertical_slug": info["slug"],
            "business_name": info["name"],
            "session_id": session_id,
        },
    )
    resp.set_cookie(
        SESSION_COOKIE,
        session_id,
        max_age=settings.demo_session_days * 86400,
        httponly=True,
        samesite="lax",
    )
    return resp


@router.post("/demo/{vertical}/messages")
async def post_message(
    vertical: str,
    payload: dict,
    pantra_demo_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> JSONResponse:
    info = _vertical_or_404(vertical)
    session_id = pantra_demo_session or payload.get("session_id") or uuid.uuid4().hex
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text required")

    outcome = await _run_pipeline(
        WebInbound(
            business_slug=info["slug"],
            session_id=session_id,
            text=text,
            audio_path=None,
            inbound_kind="text",
        )
    )
    return JSONResponse(_serialize(outcome))


@router.post("/demo/{vertical}/reset")
async def reset_session(
    vertical: str,
    pantra_demo_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> JSONResponse:
    """Close the prospect's active conversation for this vertical and rotate
    the cookie so the next message starts a fresh thread.
    """
    info = _vertical_or_404(vertical)

    if pantra_demo_session:
        async with session_scope() as session:
            biz = (
                await session.execute(select(Business).where(Business.slug == info["slug"]))
            ).scalar_one_or_none()
            if biz:
                cust = (
                    await session.execute(
                        select(Customer).where(
                            Customer.business_id == biz.id,
                            Customer.channel_type == ChannelType.web,
                            Customer.external_user_id == pantra_demo_session,
                        )
                    )
                ).scalar_one_or_none()
                if cust:
                    await session.execute(
                        update(Conversation)
                        .where(
                            Conversation.business_id == biz.id,
                            Conversation.customer_id == cust.id,
                            Conversation.status.in_(
                                [
                                    ConversationStatus.active,
                                    ConversationStatus.waiting_customer,
                                    ConversationStatus.human_needed,
                                ]
                            ),
                        )
                        .values(status=ConversationStatus.closed)
                    )

    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE)
    return resp


@router.post("/demo/{vertical}/audio")
async def post_audio(
    vertical: str,
    audio: UploadFile = File(...),
    session_id: str = Form(...),
) -> JSONResponse:
    info = _vertical_or_404(vertical)

    # Persist the inbound audio to disk so the transcriber can read it.
    inbound_dir = Path(settings.audio_storage_path) / "inbound"
    inbound_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(audio.filename or "audio.webm").suffix or ".webm"
    audio_path = inbound_dir / f"{uuid.uuid4().hex}{suffix}"
    with audio_path.open("wb") as out:
        shutil.copyfileobj(audio.file, out)

    outcome = await _run_pipeline(
        WebInbound(
            business_slug=info["slug"],
            session_id=session_id,
            text=None,
            audio_path=str(audio_path),
            inbound_kind="audio",
        )
    )
    return JSONResponse(_serialize(outcome))


# ─── Helpers ────────────────────────────────────────────────────────────

def _vertical_or_404(vertical: str) -> dict:
    if vertical not in VERTICALS:
        raise HTTPException(status_code=404, detail="unknown vertical")
    return VERTICALS[vertical]


async def _run_pipeline(web: WebInbound) -> OutboundMessage:
    inbound = to_inbound_message(web)
    try:
        async with session_scope() as session:
            return await process_inbound(session, inbound)
    except ValueError as e:
        # Most likely: demo business slug not seeded yet.
        log.warning("demo.pipeline_value_error", error=str(e))
        raise HTTPException(status_code=503, detail="demo not ready — run seed_demos.py") from e


def _serialize(outcome: OutboundMessage) -> dict:
    return {
        "text": outcome.text,
        "audio_url": outcome.audio_url,
        "handoff": outcome.handoff_triggered,
        "skipped": outcome.skipped_reason,
    }
