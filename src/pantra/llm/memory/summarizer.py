from __future__ import annotations

import uuid

from anthropic import AsyncAnthropic
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.config import settings
from pantra.llm.router import choose
from pantra.models import Conversation, Message
from pantra.privacy import pii

SUMMARIZER_SYSTEM = (
    "You compress a customer-service WhatsApp conversation into a 4-6 sentence "
    "summary for an AI assistant to keep context. Focus on: customer name, "
    "their goal, decisions made, dates/times, open questions. Drop pleasantries. "
    "Write in English regardless of conversation language."
)


async def maybe_summarise(
    session: AsyncSession, *, conversation_id: uuid.UUID
) -> str | None:
    """Refresh `conversations.summary` if the message count crossed the
    threshold. Caller is responsible for committing the session.
    """
    count = await session.scalar(
        select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
    )
    if count is None or count < settings.memory_summarize_after:
        return None

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    msgs = (await session.execute(stmt)).scalars().all()
    transcript = "\n".join(
        f"[{m.sender.value}] {pii.redact(m.text or '')}" for m in msgs
    )

    choice = choose("summarizer")
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    msg = await client.messages.create(
        model=choice.model,
        max_tokens=400,
        system=SUMMARIZER_SYSTEM,
        messages=[{"role": "user", "content": transcript}],
    )
    summary = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()

    convo = await session.get(Conversation, conversation_id)
    if convo:
        convo.summary = summary
    return summary
