from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import time
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    BadRequestError,
)
from pydantic import ValidationError

import pantra.main as pantra_main
from pantra.api.webhooks.openai_realtime import (
    DeliveryClaim,
    WebhookDeduplicator,
    WebhookDeduplicatorCapacityError,
    get_voice_gateway,
    get_webhook_deduplicator,
    router,
)
from pantra.config import Settings, settings
from pantra.voice.openai_realtime import (
    OpenAIRealtimeGateway,
    _is_retryable_openai_error,
)

WEBHOOK_SECRET = "test-webhook-secret"


class _NotifyingDeduplicator(WebhookDeduplicator):
    def __init__(self) -> None:
        super().__init__()
        self.duplicate_claimed = asyncio.Event()

    async def claim(self, webhook_id: str) -> DeliveryClaim:
        claim = await super().claim(webhook_id)
        if not claim.owner:
            self.duplicate_claimed.set()
        return claim


class _FakeCalls:
    def __init__(self) -> None:
        self.accept = AsyncMock()
        self.reject = AsyncMock()


class _FakeRealtime:
    def __init__(self, calls: _FakeCalls) -> None:
        self.calls = calls


class _FakeOpenAIClient:
    def __init__(self) -> None:
        verifier = AsyncOpenAI(api_key="test", webhook_secret=WEBHOOK_SECRET)
        self.webhooks = verifier.webhooks
        self.calls = _FakeCalls()
        self.realtime = _FakeRealtime(self.calls)
        self.close = AsyncMock()


def _signed_request(
    payload: dict[str, object],
    *,
    webhook_id: str = "wh_test",
    signature: str | None = None,
    timestamp: int | None = None,
) -> tuple[bytes, dict[str, str]]:
    body = json.dumps(payload, separators=(",", ":")).encode()
    timestamp_value = str(int(time.time()) if timestamp is None else timestamp)
    signed_payload = b".".join((webhook_id.encode(), timestamp_value.encode(), body))
    valid_signature = base64.b64encode(
        hmac.new(WEBHOOK_SECRET.encode(), signed_payload, hashlib.sha256).digest()
    ).decode()
    return body, {
        "content-type": "application/json",
        "webhook-id": webhook_id,
        "webhook-timestamp": timestamp_value,
        "webhook-signature": f"v1,{signature or valid_signature}",
    }


def _incoming_payload(*, call_id: str = "rtc_test") -> dict[str, object]:
    return {
        "object": "event",
        "id": "evt_test",
        "type": "realtime.call.incoming",
        "created_at": int(time.time()),
        "data": {"call_id": call_id, "sip_headers": []},
    }


def _status_error(
    status_code: int,
    *,
    should_retry: str | None = None,
) -> APIStatusError:
    request = httpx.Request("POST", "https://api.openai.com/v1/realtime/calls/test/accept")
    headers = {"x-should-retry": should_retry} if should_retry is not None else None
    response = httpx.Response(status_code, request=request, headers=headers)
    return APIStatusError("provider error", response=response, body=None)


def _gateway() -> tuple[OpenAIRealtimeGateway, AsyncMock, AsyncMock]:
    client = _FakeOpenAIClient()
    gateway = OpenAIRealtimeGateway(client=cast(Any, client))
    return gateway, client.calls.accept, client.calls.reject


def _app(
    gateway: OpenAIRealtimeGateway,
    *,
    deduplicator: WebhookDeduplicator | None = None,
) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/webhooks")
    app.dependency_overrides[get_voice_gateway] = lambda: gateway
    shared_deduplicator = deduplicator or WebhookDeduplicator()
    app.dependency_overrides[get_webhook_deduplicator] = lambda: shared_deduplicator
    return app


def _client(gateway: OpenAIRealtimeGateway) -> TestClient:
    return TestClient(_app(gateway))


async def _async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


def test_rejects_invalid_signature() -> None:
    gateway, accept, reject = _gateway()
    body, headers = _signed_request(_incoming_payload(), signature="invalid")

    response = _client(gateway).post("/webhooks/openai/realtime", content=body, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid webhook signature"}
    accept.assert_not_awaited()
    reject.assert_not_awaited()


def test_rejects_expired_signature_timestamp() -> None:
    gateway, accept, reject = _gateway()
    body, headers = _signed_request(
        _incoming_payload(),
        timestamp=int(time.time()) - 301,
    )

    response = _client(gateway).post("/webhooks/openai/realtime", content=body, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid webhook signature"}
    accept.assert_not_awaited()
    reject.assert_not_awaited()


def test_ignores_irrelevant_event(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, reject = _gateway()
    payload = {
        "object": "event",
        "id": "evt_other",
        "type": "response.completed",
        "created_at": int(time.time()),
        "data": {"id": "resp_test"},
    }
    body, headers = _signed_request(payload)

    response = _client(gateway).post("/webhooks/openai/realtime", content=body, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}
    accept.assert_not_awaited()
    reject.assert_not_awaited()


def test_rejects_incoming_call_when_acceptance_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", False)
    gateway, accept, reject = _gateway()
    body, headers = _signed_request(_incoming_payload())

    response = _client(gateway).post("/webhooks/openai/realtime", content=body, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"status": "rejected"}
    reject.assert_awaited_once_with("rtc_test", status_code=503)
    accept.assert_not_awaited()


def test_webhook_configuration_requires_credentials_and_single_worker_ack() -> None:
    base: dict[str, Any] = {
        "database_url": "postgresql+asyncpg://test:test@localhost/test",
        "database_url_sync": "postgresql+psycopg2://test:test@localhost/test",
        "voice_webhook_enabled": True,
    }
    with pytest.raises(ValidationError, match="OPENAI_API_KEY"):
        Settings.model_validate(base)

    configured = Settings.model_validate(
        {
            **base,
            "openai_api_key": "test",
            "openai_webhook_secret": "whsec_test",
            "voice_webhook_single_worker": True,
            "voice_enabled": False,
        }
    )
    assert configured.voice_webhook_enabled is True
    assert configured.voice_enabled is False


def test_accepts_incoming_call_with_configured_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    monkeypatch.setattr(settings, "voice_realtime_model", "gpt-realtime")
    monkeypatch.setattr(settings, "voice_realtime_voice", "cedar")
    monkeypatch.setattr(settings, "voice_realtime_instructions", "Answer in German.")
    gateway, accept, reject = _gateway()
    body, headers = _signed_request(_incoming_payload())

    response = _client(gateway).post("/webhooks/openai/realtime", content=body, headers=headers)

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}
    accept.assert_awaited_once_with(
        "rtc_test",
        type="realtime",
        model="gpt-realtime",
        instructions="Answer in German.",
        output_modalities=["audio"],
        audio={"output": {"voice": "cedar"}},
    )
    reject.assert_not_awaited()


@pytest.mark.asyncio
async def test_concurrent_duplicate_waits_for_owner_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, _ = _gateway()
    started = asyncio.Event()
    release = asyncio.Event()

    async def delayed_accept(*args: object, **kwargs: object) -> None:
        started.set()
        await release.wait()

    accept.side_effect = delayed_accept
    deduplicator = _NotifyingDeduplicator()
    app = _app(gateway, deduplicator=deduplicator)
    body, headers = _signed_request(_incoming_payload(), webhook_id="wh_concurrent")

    async for client in _async_client(app):
        owner = asyncio.create_task(
            client.post("/webhooks/openai/realtime", content=body, headers=headers)
        )
        await started.wait()
        duplicate = asyncio.create_task(
            client.post("/webhooks/openai/realtime", content=body, headers=headers)
        )
        await deduplicator.duplicate_claimed.wait()
        assert not duplicate.done()
        release.set()
        first, second = await asyncio.gather(owner, duplicate)

    assert first.json() == {"status": "accepted"}
    assert second.json() == {"status": "accepted"}
    accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrent_duplicate_receives_retryable_owner_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, _ = _gateway()
    started = asyncio.Event()
    release = asyncio.Event()

    async def failed_accept(*args: object, **kwargs: object) -> None:
        started.set()
        await release.wait()
        raise APIConnectionError(request=httpx.Request("POST", "https://api.openai.com"))

    accept.side_effect = failed_accept
    deduplicator = _NotifyingDeduplicator()
    app = _app(gateway, deduplicator=deduplicator)
    body, headers = _signed_request(_incoming_payload(), webhook_id="wh_failed")

    async for client in _async_client(app):
        owner = asyncio.create_task(
            client.post("/webhooks/openai/realtime", content=body, headers=headers)
        )
        await started.wait()
        duplicate = asyncio.create_task(
            client.post("/webhooks/openai/realtime", content=body, headers=headers)
        )
        await deduplicator.duplicate_claimed.wait()
        release.set()
        first, second = await asyncio.gather(owner, duplicate)

    assert first.status_code == 503
    assert second.status_code == 503
    accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_owner_cancellation_releases_claim_and_cancels_waiter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, _ = _gateway()
    started = asyncio.Event()
    never_release = asyncio.Event()

    async def blocked_accept(*args: object, **kwargs: object) -> None:
        started.set()
        await never_release.wait()

    accept.side_effect = blocked_accept
    deduplicator = _NotifyingDeduplicator()
    app = _app(gateway, deduplicator=deduplicator)
    body, headers = _signed_request(_incoming_payload(), webhook_id="wh_cancelled")

    async for client in _async_client(app):
        owner = asyncio.create_task(
            client.post("/webhooks/openai/realtime", content=body, headers=headers)
        )
        await started.wait()
        duplicate = asyncio.create_task(
            client.post("/webhooks/openai/realtime", content=body, headers=headers)
        )
        await deduplicator.duplicate_claimed.wait()
        owner.cancel()
        with pytest.raises(asyncio.CancelledError):
            await owner
        with pytest.raises(asyncio.CancelledError):
            await duplicate

        accept.side_effect = None
        retried = await client.post(
            "/webhooks/openai/realtime",
            content=body,
            headers=headers,
        )

    assert retried.json() == {"status": "accepted"}
    assert accept.await_count == 2


def test_permanent_openai_error_is_acknowledged_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, _ = _gateway()
    request = httpx.Request("POST", "https://api.openai.com/v1/realtime/calls/test/accept")
    accept.side_effect = BadRequestError(
        "invalid call",
        response=httpx.Response(400, request=request),
        body=None,
    )
    app = _app(gateway, deduplicator=WebhookDeduplicator())
    client = TestClient(app)
    body, headers = _signed_request(_incoming_payload(), webhook_id="wh_permanent")

    first = client.post("/webhooks/openai/realtime", content=body, headers=headers)
    duplicate = client.post("/webhooks/openai/realtime", content=body, headers=headers)

    assert first.json() == {"status": "failed_permanent"}
    assert duplicate.json() == {"status": "failed_permanent"}
    accept.assert_awaited_once()


def test_retryable_openai_error_releases_claim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, _ = _gateway()
    accept.side_effect = [
        APIConnectionError(request=httpx.Request("POST", "https://api.openai.com")),
        None,
    ]
    app = _app(gateway, deduplicator=WebhookDeduplicator())
    client = TestClient(app)
    body, headers = _signed_request(_incoming_payload(), webhook_id="wh_retryable")

    first = client.post("/webhooks/openai/realtime", content=body, headers=headers)
    retried = client.post("/webhooks/openai/realtime", content=body, headers=headers)

    assert first.status_code == 503
    assert retried.json() == {"status": "accepted"}
    assert accept.await_count == 2


def test_openai_409_is_retryable() -> None:
    assert _is_retryable_openai_error(_status_error(409)) is True


@pytest.mark.parametrize("status_code", [408, 429, 500])
def test_openai_retryable_status_defaults(status_code: int) -> None:
    assert _is_retryable_openai_error(_status_error(status_code)) is True


def test_openai_timeout_is_retryable() -> None:
    error = APITimeoutError(request=httpx.Request("POST", "https://api.openai.com"))

    assert _is_retryable_openai_error(error) is True


def test_x_should_retry_true_overrides_permanent_status() -> None:
    assert _is_retryable_openai_error(_status_error(400, should_retry="true")) is True


def test_x_should_retry_false_overrides_retryable_status() -> None:
    assert _is_retryable_openai_error(_status_error(500, should_retry="false")) is False


@pytest.mark.asyncio
async def test_pending_capacity_does_not_evict_owner_and_recovers_after_release() -> None:
    deduplicator = WebhookDeduplicator(max_entries=1)
    owner = await deduplicator.claim("wh_owner")

    with pytest.raises(WebhookDeduplicatorCapacityError):
        await deduplicator.claim("wh_over_capacity")

    duplicate = await deduplicator.claim("wh_owner")
    assert duplicate.owner is False
    assert duplicate.delivery is owner.delivery

    deduplicator.fail(owner, RuntimeError("release capacity"))
    recovered = await deduplicator.claim("wh_recovered")
    assert recovered.owner is True


@pytest.mark.asyncio
async def test_capacity_saturation_returns_503_and_recovers_after_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "voice_enabled", True)
    gateway, accept, _ = _gateway()
    started = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    async def block_first_accept(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            started.set()
            await release.wait()

    accept.side_effect = block_first_accept
    app = _app(gateway, deduplicator=WebhookDeduplicator(max_entries=1))
    first_body, first_headers = _signed_request(
        _incoming_payload(call_id="rtc_first"),
        webhook_id="wh_first",
    )
    second_body, second_headers = _signed_request(
        _incoming_payload(call_id="rtc_second"),
        webhook_id="wh_second",
    )

    async for client in _async_client(app):
        first = asyncio.create_task(
            client.post(
                "/webhooks/openai/realtime",
                content=first_body,
                headers=first_headers,
            )
        )
        await started.wait()

        saturated = await client.post(
            "/webhooks/openai/realtime",
            content=second_body,
            headers=second_headers,
        )
        assert saturated.status_code == 503
        assert saturated.json() == {"detail": "voice webhook temporarily overloaded"}
        assert accept.await_count == 1

        release.set()
        completed = await first
        recovered = await client.post(
            "/webhooks/openai/realtime",
            content=second_body,
            headers=second_headers,
        )

    assert completed.json() == {"status": "accepted"}
    assert recovered.json() == {"status": "accepted"}
    assert accept.await_count == 2


@pytest.mark.asyncio
async def test_lifespan_closes_voice_gateway(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    client = _FakeOpenAIClient()
    gateway = OpenAIRealtimeGateway(client=cast(Any, client))
    monkeypatch.setattr(settings, "voice_webhook_enabled", True)
    monkeypatch.setattr(settings, "audio_storage_path", str(tmp_path))
    monkeypatch.setattr(pantra_main, "create_voice_gateway", lambda: gateway)
    test_app = FastAPI()

    async with pantra_main.lifespan(test_app):
        assert test_app.state.voice_gateway is gateway
        client.close.assert_not_awaited()

    client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_lifespan_does_not_create_gateway_when_ingestion_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    create_gateway = Mock()
    monkeypatch.setattr(settings, "voice_webhook_enabled", False)
    monkeypatch.setattr(settings, "audio_storage_path", str(tmp_path))
    monkeypatch.setattr(pantra_main, "create_voice_gateway", create_gateway)
    test_app = FastAPI()

    async with pantra_main.lifespan(test_app):
        assert not hasattr(test_app.state, "voice_gateway")

    create_gateway.assert_not_called()


def test_rejects_oversized_chunked_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "voice_webhook_max_body_bytes", 8)
    gateway, accept, reject = _gateway()

    def chunks() -> Iterator[bytes]:
        yield b"12345678"
        yield b"9"

    response = _client(gateway).post(
        "/webhooks/openai/realtime",
        content=chunks(),
        headers={"transfer-encoding": "chunked"},
    )

    assert response.status_code == 413
    accept.assert_not_awaited()
    reject.assert_not_awaited()
