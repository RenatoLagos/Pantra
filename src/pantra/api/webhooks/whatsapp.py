from __future__ import annotations

import hashlib
import hmac

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse

from pantra.channels.whatsapp.normalizer import parse_inbound
from pantra.config import settings
from pantra.logging import log
from pantra.services.conversation import handle_inbound_message

router = APIRouter()


def _constant_time_equal(left: str, right: str) -> bool:
    """Compare arbitrary Unicode text without compare_digest's str restriction."""
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge"),
) -> str:
    # Meta hands us this triple during webhook setup. Echo the challenge
    # only when our pre-shared verify token matches.
    token_ok = _constant_time_equal(token, settings.whatsapp_verify_token)
    if mode != "subscribe" or not token_ok:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return challenge


@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def receive(
    request: Request,
    background: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
) -> dict[str, str]:
    body = await request.body()
    _verify_signature(body, x_hub_signature_256)

    try:
        payload = await request.json()
    except Exception:
        log.warning("whatsapp.bad_json")
        return {"status": "ignored"}

    for inbound in parse_inbound(payload):
        # Reply asynchronously — Meta needs a 200 within ~5s.
        background.add_task(handle_inbound_message, inbound)

    return {"status": "received"}


def _verify_signature(body: bytes, header: str | None) -> None:
    if not settings.whatsapp_app_secret:
        if settings.environment == "production":
            # Never accept unauthenticated webhooks in prod. Config validation
            # should catch this at boot; this is the belt-and-suspenders guard.
            log.error("whatsapp.signature_no_secret_prod")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="webhook not configured",
            )
        # No secret configured (dev only). Skip verification but log loudly.
        log.warning("whatsapp.signature_skipped_no_secret")
        return
    if not header or not header.startswith("sha256="):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing signature")

    expected = hmac.new(
        settings.whatsapp_app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    received = header.removeprefix("sha256=")
    if not _constant_time_equal(expected, received):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad signature")
