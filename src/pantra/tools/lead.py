from __future__ import annotations

import uuid

from pydantic import BaseModel

from pantra.models import Lead, LeadStatus
from pantra.tools.base import Tool, ToolContext


class CreateLeadIn(BaseModel):
    type: str
    summary: str
    status: LeadStatus = LeadStatus.new
    score: int | None = None
    value_estimate: float | None = None
    next_action: str | None = None


class CreateLeadOut(BaseModel):
    lead_id: uuid.UUID
    status: LeadStatus


class CreateLeadTool(Tool[CreateLeadIn, CreateLeadOut]):
    name = "create_lead"
    description = (
        "Capture a sales lead (private event, apartment viewing, custom "
        "service request). Use when the customer's intent is clearly NOT a "
        "standard booking."
    )
    input_model = CreateLeadIn
    output_model = CreateLeadOut

    async def _execute(self, ctx: ToolContext, payload: CreateLeadIn) -> CreateLeadOut:
        lead = Lead(
            business_id=ctx.business_id,
            customer_id=ctx.customer_id,
            conversation_id=ctx.conversation_id,
            type=payload.type,
            status=payload.status,
            score=payload.score,
            summary=payload.summary,
            value_estimate=payload.value_estimate,
            next_action=payload.next_action,
        )
        ctx.session.add(lead)
        await ctx.session.flush()
        return CreateLeadOut(lead_id=lead.id, status=lead.status)
