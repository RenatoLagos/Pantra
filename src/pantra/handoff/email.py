from __future__ import annotations

import uuid

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pantra.config import settings
from pantra.logging import log
from pantra.models import HandoffTask


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, max=4),
    reraise=True,
)
async def send_resend_raw(
    *,
    to: str,
    subject: str,
    html: str | None = None,
    text: str | None = None,
) -> bool:
    """Generic Resend sender — used by handoff dispatcher and by marketing
    lead capture. Returns True iff the email was sent. No-ops cleanly when
    no API key is configured (dev / staging without Resend).
    """
    if not settings.resend_api_key:
        log.warning("email.no_api_key", to=to)
        return False

    payload: dict[str, object] = {
        "from": settings.handoff_email_from,
        "to": [to],
        "subject": subject,
    }
    if html:
        payload["html"] = html
    if text:
        payload["text"] = text
    if not html and not text:
        # Resend requires at least one body. Fall back to an empty text.
        payload["text"] = ""

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json=payload,
        )
        r.raise_for_status()
    log.info("email.sent", to=to, subject=subject)
    return True


async def send_email(
    task: HandoffTask,
    *,
    business_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> None:
    if not settings.handoff_email_to:
        return

    if settings.email_provider == "resend":
        await _send_handoff_via_resend(
            task, business_id=business_id, conversation_id=conversation_id
        )
    else:
        log.warning(
            "handoff.email.provider_not_supported",
            provider=settings.email_provider,
        )


async def _send_handoff_via_resend(
    task: HandoffTask,
    *,
    business_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> None:
    body_html = (
        f"<h2>Handoff requested</h2>"
        f"<p><strong>Reason:</strong> {task.reason}<br>"
        f"<strong>Priority:</strong> {task.priority}<br>"
        f"<strong>Business:</strong> {business_id}<br>"
        f"<strong>Conversation:</strong> {conversation_id}</p>"
        f"<h3>Summary</h3><pre>{task.summary}</pre>"
        f"<p><small>handoff_id: {task.id}</small></p>"
    )
    sent = await send_resend_raw(
        to=settings.handoff_email_to,
        subject=f"[Pantra] Handoff: {task.reason}",
        html=body_html,
    )
    if sent:
        log.info("handoff.email.sent", handoff_id=str(task.id))
