from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.models import ToolIdempotency

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)


class ToolError(Exception):
    """Tool failed with a structured, model-readable message."""

    def __init__(self, code: str, message: str, *, retriable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retriable = retriable


@dataclass(slots=True)
class ToolContext:
    """Everything a tool needs to run, supplied by the orchestrator."""
    business_id: uuid.UUID
    customer_id: uuid.UUID
    conversation_id: uuid.UUID
    session: AsyncSession
    idempotency_key: str  # e.g. f"whatsapp:{message_id}:{tool_name}"


class Tool(Generic[I, O]):
    """Base class for every LLM-callable tool.

    Contract:
      • `name`, `description`, `input_model`, `output_model` are class-level.
      • `_execute(ctx, payload)` is the side-effecting body.
      • `run(...)` wraps execute with idempotency caching.
      • Tools must NOT call the LLM. Tools must NOT call other tools.
      • Tools own their transactional scope inside `_execute` if they
        need pessimistic locking — see tools/booking.py for the pattern.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    input_model: ClassVar[type[BaseModel]]
    output_model: ClassVar[type[BaseModel]]

    async def run(self, ctx: ToolContext, payload: I) -> O:
        cached = await self._lookup_cache(ctx)
        if cached is not None:
            return self.output_model.model_validate(cached)

        result = await self._execute(ctx, payload)
        await self._store_cache(ctx, result.model_dump(mode="json"))
        return result

    async def _execute(self, ctx: ToolContext, payload: I) -> O:
        raise NotImplementedError

    # ─── Idempotency cache ──
    async def _lookup_cache(self, ctx: ToolContext) -> dict[str, Any] | None:
        stmt = select(ToolIdempotency).where(
            ToolIdempotency.business_id == ctx.business_id,
            ToolIdempotency.tool_name == self.name,
            ToolIdempotency.idempotency_key == ctx.idempotency_key,
        )
        row = (await ctx.session.execute(stmt)).scalar_one_or_none()
        return row.result if row else None

    async def _store_cache(self, ctx: ToolContext, result: dict[str, Any]) -> None:
        ctx.session.add(ToolIdempotency(
            business_id=ctx.business_id,
            tool_name=self.name,
            idempotency_key=ctx.idempotency_key,
            result=result,
        ))
        await ctx.session.flush()


def anthropic_tool_definitions(tools: list[Tool]) -> list[dict[str, Any]]:
    """Render tools to the shape Anthropic's tool-use API expects."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_model.model_json_schema(),
        }
        for t in tools
    ]
