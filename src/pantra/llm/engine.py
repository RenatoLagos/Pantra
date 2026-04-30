from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from anthropic import AsyncAnthropic

from pantra.config import settings
from pantra.llm.memory.window import WindowMessage
from pantra.llm.router import choose


@dataclass(frozen=True, slots=True)
class EngineResult:
    reply_text: str | None
    tool_calls: list[dict[str, Any]]
    # Raw assistant content blocks (text + tool_use) — needed by the
    # orchestrator to append the assistant turn before sending tool_results
    # back. Anthropic rejects tool_result blocks whose tool_use_id has no
    # matching tool_use in the previous message.
    assistant_blocks: list[dict[str, Any]]
    input_tokens: int | None
    output_tokens: int | None
    latency_ms: int


class ConversationEngine:
    """Main LLM that drives the customer reply.

    The engine is stateless across turns. The orchestrator
    (services/conversation.py) builds the `messages` list, calls
    `step()`, appends the resulting assistant_blocks + any tool_result
    blocks, and calls `step()` again until tool_calls is empty.
    """

    def __init__(self) -> None:
        self.choice = choose("main")
        if self.choice.provider != "anthropic":
            raise NotImplementedError(
                f"Engine provider {self.choice.provider!r} not wired yet."
            )
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def step(
        self,
        *,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tool_definitions: list[dict[str, Any]],
    ) -> EngineResult:
        t0 = time.perf_counter()
        resp = await self._client.messages.create(
            model=self.choice.model,
            max_tokens=settings.llm_main_max_tokens,
            temperature=settings.llm_main_temperature,
            system=system_prompt,
            tools=tool_definitions,
            messages=messages,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)

        text_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        assistant_blocks: list[dict[str, Any]] = []
        for block in resp.content:
            t = getattr(block, "type", "")
            if t == "text":
                text_parts.append(block.text)
                assistant_blocks.append({"type": "text", "text": block.text})
            elif t == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
                assistant_blocks.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return EngineResult(
            reply_text="\n".join(text_parts).strip() or None,
            tool_calls=tool_calls,
            assistant_blocks=assistant_blocks,
            input_tokens=getattr(resp.usage, "input_tokens", None),
            output_tokens=getattr(resp.usage, "output_tokens", None),
            latency_ms=latency_ms,
        )
