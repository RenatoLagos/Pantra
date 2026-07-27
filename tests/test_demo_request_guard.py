from __future__ import annotations

import json
from collections.abc import Iterator
from importlib import import_module
from typing import cast

import pytest
from fastapi import FastAPI
from starlette.datastructures import FormData
from starlette.formparsers import MultiPartParser
from starlette.types import ASGIApp, Message, Scope

from pantra.api.demo.body_limit import DemoRequestGuardMiddleware, RateLimiter

demo_router = import_module("pantra.api.demo.router")


async def _always_allow(
    key: str,
    *,
    limit: int,
    window_seconds: int,
) -> bool:
    return True


def _demo_app(limiter: RateLimiter = _always_allow) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        DemoRequestGuardMiddleware,
        message_max_body_bytes=64,
        audio_max_file_bytes=8,
        multipart_overhead_bytes=192,
        rate_per_minute=10,
        daily_cap=60,
        limiter=limiter,
    )
    app.include_router(demo_router.router)
    return app


async def _invoke_asgi(
    app: ASGIApp,
    *,
    path: str,
    headers: list[tuple[bytes, bytes]],
    chunks: list[bytes],
) -> tuple[int, bytes]:
    request_messages: Iterator[Message] = iter(
        [
            cast(
                Message,
                {
                    "type": "http.request",
                    "body": chunk,
                    "more_body": index < len(chunks) - 1,
                },
            )
            for index, chunk in enumerate(chunks)
        ]
    )
    sent: list[Message] = []

    async def receive() -> Message:
        return next(request_messages, {"type": "http.disconnect"})

    async def send(message: Message) -> None:
        sent.append(message)

    scope = cast(
        Scope,
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "headers": headers,
            "client": ("203.0.113.7", 1234),
            "server": ("testserver", 80),
        },
    )

    await app(scope, receive, send)

    response_start = next(message for message in sent if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"") for message in sent if message["type"] == "http.response.body"
    )
    return response_start["status"], body


def _audio_multipart_body() -> tuple[bytes, bytes]:
    boundary = b"pantra-test-boundary"
    body = (
        b"--"
        + boundary
        + b'\r\nContent-Disposition: form-data; name="session_id"\r\n\r\n'
        + b"session-1"
        + b"\r\n--"
        + boundary
        + b'\r\nContent-Disposition: form-data; name="audio"; filename="voice.webm"\r\n'
        + b"Content-Type: audio/webm\r\n\r\n"
        + (b"a" * 32)
        + b"\r\n--"
        + boundary
        + b"--\r\n"
    )
    return body, boundary


@pytest.mark.parametrize("declared_length", [True, False], ids=["content-length", "chunked"])
async def test_oversized_demo_message_is_rejected_before_json_parsing(
    declared_length: bool,
) -> None:
    body = b'{"text":"' + (b"x" * 80) + b'"}'
    headers = [(b"content-type", b"application/json")]
    chunks = [body]
    if declared_length:
        headers.append((b"content-length", str(len(body)).encode()))
    else:
        chunks = [body[:32], body[32:]]

    status, response_body = await _invoke_asgi(
        _demo_app(),
        path="/demo/dental/messages",
        headers=headers,
        chunks=chunks,
    )

    assert status == 413
    assert json.loads(response_body) == {"detail": "request_body_too_large"}


async def test_chunked_demo_audio_overflow_is_413_through_fastapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body, boundary = _audio_multipart_body()
    parse_calls = 0
    original_parse = MultiPartParser.parse

    async def tracked_parse(parser: MultiPartParser) -> FormData:
        nonlocal parse_calls
        parse_calls += 1
        return await original_parse(parser)

    monkeypatch.setattr(MultiPartParser, "parse", tracked_parse)

    status, response_body = await _invoke_asgi(
        _demo_app(),
        path="/demo/dental/audio",
        headers=[(b"content-type", b"multipart/form-data; boundary=" + boundary)],
        chunks=[body[:160], body[160:]],
    )

    assert len(body) > 200
    assert parse_calls == 1
    assert status == 413
    assert json.loads(response_body) == {"detail": "request_body_too_large"}


async def test_rate_rejected_demo_audio_never_enters_multipart_parser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body, boundary = _audio_multipart_body()
    rate_calls: list[tuple[str, int, int]] = []
    decisions = iter([True, False])
    parse_calls = 0
    original_parse = MultiPartParser.parse

    async def fake_limiter(key: str, *, limit: int, window_seconds: int) -> bool:
        rate_calls.append((key, limit, window_seconds))
        return next(decisions)

    async def tracked_parse(parser: MultiPartParser) -> FormData:
        nonlocal parse_calls
        parse_calls += 1
        return await original_parse(parser)

    monkeypatch.setattr(MultiPartParser, "parse", tracked_parse)

    status, response_body = await _invoke_asgi(
        _demo_app(fake_limiter),
        path="/demo/dental/audio",
        headers=[(b"content-type", b"multipart/form-data; boundary=" + boundary)],
        chunks=[body],
    )

    assert status == 429
    assert json.loads(response_body) == {"detail": "daily_limit_reached"}
    assert parse_calls == 0
    assert rate_calls == [
        ("demo:ip:203.0.113.7", 10, 60),
        ("demo:ip:203.0.113.7:day", 60, 86400),
    ]
