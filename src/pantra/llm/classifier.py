from __future__ import annotations

import json
from typing import Literal

from anthropic import AsyncAnthropic
from pydantic import BaseModel, Field

from pantra.config import settings
from pantra.llm.prompts.classifier import CLASSIFIER_SYSTEM_PROMPT, render_user_prompt
from pantra.llm.router import choose
from pantra.privacy import pii


class Extracted(BaseModel):
    date: str | None = None
    time: str | None = None
    party_size: int | None = None
    name: str | None = None
    phone: str | None = None


class ClassifierOutput(BaseModel):
    language: str | None
    intent: Literal[
        "booking_request", "reschedule", "cancel", "faq",
        "lead", "complaint", "smalltalk", "other",
    ] | None
    urgency: Literal["low", "normal", "high"] = "normal"
    needs_human: bool = False
    business_domain: str | None = None
    extracted: Extracted = Field(default_factory=Extracted)


class Classifier:
    """Single-model classifier. Anthropic for MVP; swap by env."""

    def __init__(self) -> None:
        self.choice = choose("classifier")
        if self.choice.provider != "anthropic":
            raise NotImplementedError(
                f"Classifier provider {self.choice.provider!r} not wired yet."
            )
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def classify(self, *, text: str, business_domain: str) -> ClassifierOutput:
        # Redact PII BEFORE sending to the LLM and before logging.
        safe_text = pii.redact(text) if settings.pii_redaction_enabled else text

        message = await self._client.messages.create(
            model=self.choice.model,
            max_tokens=400,
            system=[
                {
                    "type": "text",
                    "text": CLASSIFIER_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": render_user_prompt(safe_text, business_domain)}],
            # JSON-mode-equivalent: ask for JSON in the prompt and parse.
        )
        raw = "".join(
            block.text for block in message.content if getattr(block, "type", "") == "text"
        ).strip()
        return _parse(raw)


def _parse(raw: str) -> ClassifierOutput:
    # Models sometimes wrap JSON in ```json fences. Tolerate both.
    cleaned = raw
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        return ClassifierOutput.model_validate(json.loads(cleaned))
    except Exception:
        # Fallback: degrade gracefully so the engine can still reply, but
        # mark needs_human so a human can review.
        return ClassifierOutput(
            language=None,
            intent="other",
            urgency="normal",
            needs_human=True,
        )
