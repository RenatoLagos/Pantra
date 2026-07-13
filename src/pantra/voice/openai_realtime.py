from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    InvalidWebhookSignatureError,
    OpenAIError,
)


class InvalidVoiceWebhookSignature(ValueError):
    """Raised when an inbound voice webhook cannot be authenticated."""


class VoiceProviderError(RuntimeError):
    """Normalized OpenAI error with an explicit webhook retry decision."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


@dataclass(frozen=True, slots=True)
class VoiceWebhookEvent:
    type: str
    call_id: str | None = None


class _WebhookVerifier(Protocol):
    def unwrap(self, payload: str | bytes, headers: Mapping[str, str]) -> Any: ...


class _RealtimeCalls(Protocol):
    async def accept(self, call_id: str, **kwargs: Any) -> None: ...

    async def reject(self, call_id: str, **kwargs: Any) -> None: ...


class _Realtime(Protocol):
    calls: _RealtimeCalls


class _OpenAIClient(Protocol):
    webhooks: _WebhookVerifier
    realtime: _Realtime

    async def close(self) -> None: ...


def _is_retryable_openai_error(exc: OpenAIError) -> bool:
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return True
    if not isinstance(exc, APIStatusError):
        return False

    # Mirror OpenAI SDK 2.44.0's BaseClient._should_retry semantics. The
    # provider's explicit response header overrides the status-code defaults.
    should_retry = exc.response.headers.get("x-should-retry")
    if should_retry == "true":
        return True
    if should_retry == "false":
        return False
    return exc.status_code in {408, 409, 429} or exc.status_code >= 500


class OpenAIRealtimeGateway:
    """Small adapter around the OpenAI webhook and Realtime SIP APIs."""

    _SIGNATURE_HEADERS = ("webhook-id", "webhook-timestamp", "webhook-signature")

    def __init__(
        self,
        *,
        api_key: str | None = None,
        webhook_secret: str | None = None,
        timeout_seconds: float = 5.0,
        client: _OpenAIClient | None = None,
    ) -> None:
        if client is None and (not api_key or not webhook_secret):
            raise ValueError("OpenAI API key and webhook secret are required")
        self._client = client or AsyncOpenAI(
            api_key=api_key,
            webhook_secret=webhook_secret,
            max_retries=0,
            timeout=timeout_seconds,
        )

    def unwrap_webhook(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> VoiceWebhookEvent:
        if any(not headers.get(name) for name in self._SIGNATURE_HEADERS):
            raise InvalidVoiceWebhookSignature("missing webhook signature headers")

        try:
            event = self._client.webhooks.unwrap(body, headers)
        except InvalidWebhookSignatureError as exc:
            raise InvalidVoiceWebhookSignature("invalid webhook signature") from exc

        call_id_value = (
            getattr(event.data, "call_id", None)
            if event.type == "realtime.call.incoming"
            else None
        )
        call_id = str(call_id_value) if call_id_value else None
        return VoiceWebhookEvent(type=str(event.type), call_id=call_id)

    async def accept_call(
        self,
        call_id: str,
        *,
        model: str,
        voice: str,
        instructions: str,
    ) -> None:
        try:
            await self._client.realtime.calls.accept(
                call_id,
                type="realtime",
                model=model,
                instructions=instructions,
                output_modalities=["audio"],
                audio={"output": {"voice": voice}},
            )
        except OpenAIError as exc:
            raise VoiceProviderError(
                "OpenAI failed to accept the Realtime call",
                retryable=_is_retryable_openai_error(exc),
            ) from exc

    async def reject_call(self, call_id: str, *, status_code: int = 503) -> None:
        try:
            await self._client.realtime.calls.reject(call_id, status_code=status_code)
        except OpenAIError as exc:
            raise VoiceProviderError(
                "OpenAI failed to reject the Realtime call",
                retryable=_is_retryable_openai_error(exc),
            ) from exc

    async def close(self) -> None:
        await self._client.close()
