from __future__ import annotations

import html
import uuid

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pantra.config import settings
from pantra.logging import log
from pantra.models import HandoffTask

_PRIORITY_LABELS = {1: "🔴 high", 2: "🟡 normal", 3: "🟢 low"}


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, max=4),
    reraise=True,
)
async def send_telegram(
    task: HandoffTask,
    *,
    business_id: uuid.UUID,
    conversation_id: uuid.UUID,
    chat_id_override: str | None = None,
) -> None:
    """Push a handoff notification to the business owner's Telegram chat.

    MVP keeps the bot token + chat_id in env. Phase 2 moves chat_id to
    business.config so each tenant owns their own destination.

    `chat_id_override` is used by the demo flow to redirect notifications
    to a separate "demo" chat without touching prod settings.
    """
    chat_id = chat_id_override or settings.telegram_chat_id
    if not settings.telegram_bot_token or not chat_id:
        return

    priority_label = _PRIORITY_LABELS.get(task.priority, "normal")

    text = (
        f"<b>Handoff requested</b> — {html.escape(task.reason)} ({priority_label})\n\n"
        f"<b>Reason:</b> {html.escape(task.reason)}\n"
        f"<b>Priority:</b> {priority_label}\n"
        f"<b>Business:</b> <code>{business_id}</code>\n"
        f"<b>Conversation:</b> <code>{conversation_id}</code>\n\n"
        f"<b>Summary</b>\n<pre>{html.escape(task.summary)}</pre>\n\n"
        f"<i>handoff_id: {task.id}</i>"
    )

    url = f"{settings.telegram_api_base}/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
    log.info("handoff.telegram.sent", handoff_id=str(task.id))
