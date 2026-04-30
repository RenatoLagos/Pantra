from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.config import settings
from pantra.models import Message, MessageSender


@dataclass(frozen=True, slots=True)
class WindowMessage:
    role: str        # 'user' | 'assistant'
    content: str


_SENDER_TO_ROLE = {
    MessageSender.customer: "user",
    MessageSender.ai: "assistant",
    MessageSender.human: "assistant",
    MessageSender.system: "system",
}


async def load_window(
    session: AsyncSession,
    *,
    conversation_id: uuid.UUID,
    limit: int | None = None,
) -> list[WindowMessage]:
    """Last N messages, oldest first, mapped to OpenAI/Anthropic chat shape.

    The rolling summary is injected separately (see prompts/system.py) so
    older messages aren't duplicated.
    """
    n = limit or settings.memory_window_messages
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(n)
    )
    rows = (await session.execute(stmt)).scalars().all()
    rows = list(reversed(rows))
    return [
        WindowMessage(role=_SENDER_TO_ROLE[m.sender], content=m.text or "")
        for m in rows
        if m.text
    ]
