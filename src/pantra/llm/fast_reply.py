"""Cheap Haiku-only path for trivial intents (smalltalk).

The classifier already runs Haiku and labels intent; if the message is just
a greeting / thanks / "ok" / goodbye, sending it through the full Sonnet
tool-use loop is overkill. We answer directly with Haiku at ~5x lower cost
and ~3x lower latency.

This module is intentionally narrow — it handles ONE intent (smalltalk).
Anything that might need tools, knowledge lookups, or business context goes
through `ConversationEngine` as before.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from textwrap import dedent

from anthropic import AsyncAnthropic

from pantra.config import settings
from pantra.llm.router import choose

FAST_REPLY_SYSTEM = dedent(
    """\
    You are Pantra, the AI assistant for {business_name}.
    The customer just said something trivial — a greeting, a thank you,
    "ok", a goodbye, or similar small talk. Reply briefly in the
    customer's language ({language}).

    Rules:
    - 1-2 short sentences. Warm, natural tone.
    - No corporate phrasing. No emoji unless the message has one.
    - If they greet you, greet back and offer to help with their visit
      (booking, questions, etc.) — keep the door open without pushing.
    - If they thank you, acknowledge briefly and stay available.
    - If they say goodbye, say goodbye warmly.
    - Never invent business facts or schedules. If they ask anything
      concrete, say you'll check and that someone from the team will follow
      up — but in this path the orchestrator will already have routed away
      from smalltalk, so this should not happen.
    """
)


@dataclass(frozen=True, slots=True)
class FastReplyResult:
    reply_text: str
    input_tokens: int | None
    output_tokens: int | None
    cache_read_tokens: int | None
    cache_creation_tokens: int | None
    latency_ms: int
    model: str


async def reply_smalltalk(
    *,
    text: str,
    language: str,
    business_name: str,
) -> FastReplyResult:
    choice = choose("classifier")  # Haiku tier
    if choice.provider != "anthropic":
        raise NotImplementedError(
            f"Fast-reply provider {choice.provider!r} not wired yet."
        )
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    system_text = FAST_REPLY_SYSTEM.format(
        business_name=business_name,
        language=language,
    )

    t0 = time.perf_counter()
    resp = await client.messages.create(
        model=choice.model,
        max_tokens=200,
        temperature=0.5,
        system=[
            {
                "type": "text",
                "text": system_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": text}],
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)

    reply = "".join(
        block.text for block in resp.content if getattr(block, "type", "") == "text"
    ).strip()

    return FastReplyResult(
        reply_text=reply,
        input_tokens=getattr(resp.usage, "input_tokens", None),
        output_tokens=getattr(resp.usage, "output_tokens", None),
        cache_read_tokens=getattr(resp.usage, "cache_read_input_tokens", None),
        cache_creation_tokens=getattr(resp.usage, "cache_creation_input_tokens", None),
        latency_ms=latency_ms,
        model=choice.model,
    )
