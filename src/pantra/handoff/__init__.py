"""Human handoff dispatchers (Telegram bot + email).

`dispatch()` is the single entry point used by tools/handoff.py. It picks
the right transport(s) based on what's configured in settings.
"""
from __future__ import annotations

import uuid

from pantra.config import settings
from pantra.handoff.email import send_email
from pantra.handoff.telegram import send_telegram
from pantra.logging import log
from pantra.models import HandoffTask


async def dispatch(
    task: HandoffTask,
    *,
    business_id: uuid.UUID,
    conversation_id: uuid.UUID,
    is_demo: bool = False,
) -> None:
    """Notify the business owner.

    Demo conversations skip real notifications by default — prospect tests
    must not page the prod owner. If `DEMO_HANDOFF_TELEGRAM_CHAT_ID` is set,
    demo handoffs go there instead of the regular Telegram chat.
    """
    if is_demo and not settings.demo_handoff_telegram_chat_id:
        log.info(
            "handoff.demo_logged_only",
            handoff_id=str(task.id),
            business_id=str(business_id),
        )
        return

    target_chat_id = (
        settings.demo_handoff_telegram_chat_id if is_demo else settings.telegram_chat_id
    )

    sent_any = False
    if settings.telegram_bot_token and target_chat_id:
        await send_telegram(
            task,
            business_id=business_id,
            conversation_id=conversation_id,
            chat_id_override=target_chat_id if is_demo else None,
        )
        sent_any = True
    if not is_demo and settings.handoff_email_to:
        await send_email(task, business_id=business_id, conversation_id=conversation_id)
        sent_any = True
    if not sent_any:
        log.warning(
            "handoff.no_transport_configured",
            handoff_id=str(task.id),
            business_id=str(business_id),
        )


__all__ = ["dispatch"]
