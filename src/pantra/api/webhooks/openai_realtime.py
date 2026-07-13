from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

from pantra.config import settings
from pantra.logging import log
from pantra.voice.openai_realtime import (
    InvalidVoiceWebhookSignature,
    OpenAIRealtimeGateway,
    VoiceProviderError,
    VoiceWebhookEvent,
)

router = APIRouter()
WebhookResult = dict[str, str]


class WebhookDeduplicatorCapacityError(RuntimeError):
    """Raised when every bounded idempotency slot is owned by pending work."""


class VoiceGateway(Protocol):
    def unwrap_webhook(
        self,
        body: bytes,
        headers: Mapping[str, str],
    ) -> VoiceWebhookEvent: ...

    async def accept_call(
        self,
        call_id: str,
        *,
        model: str,
        voice: str,
        instructions: str,
    ) -> None: ...

    async def reject_call(self, call_id: str, *, status_code: int = 503) -> None: ...


@dataclass(slots=True)
class _Delivery:
    future: asyncio.Future[WebhookResult]
    completed_at: float | None = None


@dataclass(frozen=True, slots=True)
class DeliveryClaim:
    webhook_id: str
    delivery: _Delivery
    owner: bool

    async def wait(self) -> WebhookResult:
        # A duplicate request being cancelled must not cancel the owner's shared result.
        return await asyncio.shield(self.delivery.future)


class WebhookDeduplicator:
    """Pending/completed idempotency state for the acknowledged single worker."""

    def __init__(self, *, ttl_seconds: float = 600, max_entries: int = 10_000) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries
        self._entries: dict[str, _Delivery] = {}
        self._lock = asyncio.Lock()

    async def claim(self, webhook_id: str) -> DeliveryClaim:
        async with self._lock:
            self._prune_completed()
            existing = self._entries.get(webhook_id)
            if existing is not None:
                return DeliveryClaim(webhook_id, existing, owner=False)

            self._evict_oldest_completed_if_full()
            if len(self._entries) >= self._max_entries:
                raise WebhookDeduplicatorCapacityError(
                    "webhook idempotency capacity is full"
                )
            future = asyncio.get_running_loop().create_future()
            # Consume owner-less failures to avoid "Future exception was never retrieved".
            future.add_done_callback(self._consume_exception)
            delivery = _Delivery(future=future)
            self._entries[webhook_id] = delivery
            return DeliveryClaim(webhook_id, delivery, owner=True)

    def complete(self, claim: DeliveryClaim, result: WebhookResult) -> None:
        if self._entries.get(claim.webhook_id) is not claim.delivery:
            return
        claim.delivery.completed_at = time.monotonic()
        if not claim.delivery.future.done():
            claim.delivery.future.set_result(result)

    def fail(self, claim: DeliveryClaim, exc: BaseException) -> None:
        if self._entries.get(claim.webhook_id) is claim.delivery:
            del self._entries[claim.webhook_id]
        if claim.delivery.future.done():
            return
        if isinstance(exc, asyncio.CancelledError):
            claim.delivery.future.cancel()
        else:
            claim.delivery.future.set_exception(exc)

    def _prune_completed(self) -> None:
        cutoff = time.monotonic() - self._ttl_seconds
        expired = [
            webhook_id
            for webhook_id, delivery in self._entries.items()
            if delivery.completed_at is not None and delivery.completed_at <= cutoff
        ]
        for webhook_id in expired:
            del self._entries[webhook_id]

    def _evict_oldest_completed_if_full(self) -> None:
        if len(self._entries) < self._max_entries:
            return
        completed = (
            (delivery.completed_at, webhook_id)
            for webhook_id, delivery in self._entries.items()
            if delivery.completed_at is not None
        )
        oldest = min(completed, default=None)
        if oldest is not None:
            del self._entries[oldest[1]]

    @staticmethod
    def _consume_exception(future: asyncio.Future[WebhookResult]) -> None:
        if not future.cancelled():
            future.exception()


_deduplicator = WebhookDeduplicator()


def create_voice_gateway() -> OpenAIRealtimeGateway:
    return OpenAIRealtimeGateway(
        api_key=settings.openai_api_key,
        webhook_secret=settings.openai_webhook_secret,
        timeout_seconds=settings.voice_api_timeout_seconds,
    )


def get_voice_gateway(request: Request) -> VoiceGateway:
    if not settings.voice_webhook_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="voice webhook disabled",
        )
    gateway = getattr(request.app.state, "voice_gateway", None)
    if gateway is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="voice gateway not initialized",
        )
    return cast(VoiceGateway, gateway)


def get_webhook_deduplicator() -> WebhookDeduplicator:
    return _deduplicator


async def _read_limited_body(request: Request) -> bytes:
    limit = settings.voice_webhook_max_body_bytes
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            if int(content_length) > limit:
                raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST) from exc

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > limit:
            raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE)
    return bytes(body)


def _retryable_provider_failure(exc: VoiceProviderError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="voice provider temporarily unavailable",
    )


@router.post("/openai/realtime", status_code=status.HTTP_200_OK)
async def receive_realtime_call(
    request: Request,
    gateway: VoiceGateway = Depends(get_voice_gateway),
    deduplicator: WebhookDeduplicator = Depends(get_webhook_deduplicator),
) -> WebhookResult:
    body = await _read_limited_body(request)
    try:
        event = gateway.unwrap_webhook(body, request.headers)
    except InvalidVoiceWebhookSignature as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid webhook signature",
        ) from exc

    if event.type != "realtime.call.incoming":
        return {"status": "ignored"}
    if not event.call_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing call id")

    try:
        claim = await deduplicator.claim(request.headers["webhook-id"])
    except WebhookDeduplicatorCapacityError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="voice webhook temporarily overloaded",
        ) from exc
    if not claim.owner:
        try:
            return await claim.wait()
        except VoiceProviderError as exc:
            if exc.retryable:
                raise _retryable_provider_failure(exc) from exc
            raise

    try:
        if not settings.voice_enabled:
            await gateway.reject_call(event.call_id, status_code=503)
            result = {"status": "rejected"}
            log.info("voice.call_rejected_disabled", call_id=event.call_id)
        else:
            await gateway.accept_call(
                event.call_id,
                model=settings.voice_realtime_model,
                voice=settings.voice_realtime_voice,
                instructions=settings.voice_realtime_instructions,
            )
            result = {"status": "accepted"}
            log.info("voice.call_accepted", call_id=event.call_id)
    except VoiceProviderError as exc:
        if exc.retryable:
            deduplicator.fail(claim, exc)
            raise _retryable_provider_failure(exc) from exc
        result = {"status": "failed_permanent"}
        log.error("voice.call_failed_permanent", call_id=event.call_id)
    except BaseException as exc:
        # Synchronous cleanup is cancellation-safe and releases the claim for retries.
        deduplicator.fail(claim, exc)
        raise

    deduplicator.complete(claim, result)
    return result
