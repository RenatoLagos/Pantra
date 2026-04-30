from __future__ import annotations

import uuid

from pydantic import BaseModel

from pantra.handoff import dispatch as send_handoff
from pantra.models import ConversationStatus, HandoffStatus, HandoffTask
from pantra.tools.base import Tool, ToolContext


class HandoffIn(BaseModel):
    reason: str
    summary: str
    priority: int = 2  # 1=high, 3=low


class HandoffOut(BaseModel):
    handoff_id: uuid.UUID
    status: HandoffStatus


class HandoffToHumanTool(Tool[HandoffIn, HandoffOut]):
    name = "handoff_to_human"
    description = (
        "Hand the conversation to a human teammate. Use when the customer is "
        "angry, asks for a person, raises legal/medical/financial questions, "
        "or sends documents. STOP replying after calling this tool."
    )
    input_model = HandoffIn
    output_model = HandoffOut

    async def _execute(self, ctx: ToolContext, payload: HandoffIn) -> HandoffOut:
        from pantra.models import Business, Conversation

        business = await ctx.session.get(Business, ctx.business_id)
        is_demo = bool(business and business.is_demo)

        task = HandoffTask(
            business_id=ctx.business_id,
            conversation_id=ctx.conversation_id,
            reason=payload.reason,
            priority=payload.priority,
            status=HandoffStatus.open,
            summary=payload.summary,
        )
        ctx.session.add(task)
        await ctx.session.flush()

        # Prod: freeze the conversation so a human can take over.
        # Demo: keep going so the prospect can keep evaluating the bot.
        if not is_demo:
            convo = await ctx.session.get(Conversation, ctx.conversation_id)
            if convo:
                convo.status = ConversationStatus.human_needed

        await send_handoff(
            task,
            business_id=ctx.business_id,
            conversation_id=ctx.conversation_id,
            is_demo=is_demo,
        )
        return HandoffOut(handoff_id=task.id, status=task.status)
