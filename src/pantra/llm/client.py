from __future__ import annotations

from anthropic import AsyncAnthropic

from pantra.config import settings


def anthropic_client() -> AsyncAnthropic:
    """Shared Anthropic client factory with an explicit timeout and bounded
    retries.

    Prefer this over instantiating ``AsyncAnthropic`` directly so every LLM call
    (classifier, engine, fast-reply) shares one policy. The SDK
    retries connection errors, request timeouts, 429 (honoring ``Retry-After``)
    and 5xx up to ``max_retries`` with backoff — more correct than a blind
    tenacity wrapper. The timeout caps how long a hung call can hold a DB
    session open.
    """
    return AsyncAnthropic(
        api_key=settings.anthropic_api_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
