from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from pantra.ratelimit import allow

RateLimiter = Callable[..., Awaitable[bool]]


class _BodyTooLarge(OSError):
    """Abort request streaming while letting Starlette close spooled files."""


class DemoRequestGuardMiddleware:
    """Protect public demo request bodies before FastAPI parses them.

    The guarded message and audio endpoints get endpoint-specific body limits
    plus per-IP burst and daily rate checks. Responses from those endpoints are
    buffered until request parsing finishes so FastAPI's generic parsing error
    cannot turn a streaming body overflow into a 400 response.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        message_max_body_bytes: int,
        audio_max_file_bytes: int,
        multipart_overhead_bytes: int,
        rate_per_minute: int,
        daily_cap: int,
        limiter: RateLimiter | None = None,
    ) -> None:
        if message_max_body_bytes <= 0:
            raise ValueError("message_max_body_bytes must be greater than zero")
        if audio_max_file_bytes <= 0:
            raise ValueError("audio_max_file_bytes must be greater than zero")
        if multipart_overhead_bytes < 0:
            raise ValueError("multipart_overhead_bytes cannot be negative")
        if rate_per_minute <= 0:
            raise ValueError("rate_per_minute must be greater than zero")
        if daily_cap <= 0:
            raise ValueError("daily_cap must be greater than zero")

        self.app = app
        self.message_max_body_bytes = message_max_body_bytes
        self.audio_max_body_bytes = audio_max_file_bytes + multipart_overhead_bytes
        self.rate_per_minute = rate_per_minute
        self.daily_cap = daily_cap
        self.limiter = limiter or allow

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        endpoint = self._guarded_endpoint(scope)
        if endpoint is None:
            await self.app(scope, receive, send)
            return

        max_body_bytes = (
            self.message_max_body_bytes
            if endpoint == "messages"
            else self.audio_max_body_bytes
        )
        content_length = self._content_length(scope)
        if content_length is not None and content_length > max_body_bytes:
            await self._reject(scope, receive, send, 413, "request_body_too_large")
            return

        rate_error = await self._ip_rate_error(scope)
        if rate_error is not None:
            await self._reject(scope, receive, send, 429, rate_error)
            return

        received = 0
        overflowed = False
        buffered_response: list[Message] = []

        async def limited_receive() -> Message:
            nonlocal overflowed, received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > max_body_bytes:
                    overflowed = True
                    # OSError makes Starlette close any UploadFile objects that
                    # were already spooled before this crossing chunk arrived.
                    raise _BodyTooLarge
            return message

        async def buffered_send(message: Message) -> None:
            buffered_response.append(message)

        try:
            await self.app(scope, limited_receive, buffered_send)
        except _BodyTooLarge:
            overflowed = True

        if overflowed:
            # FastAPI converts generic request parsing exceptions into a 400.
            # Because the downstream response was buffered, the boundary still
            # owns the final status and can reliably emit the intended 413.
            await self._reject(scope, receive, send, 413, "request_body_too_large")
            return

        for message in buffered_response:
            await send(message)

    async def _ip_rate_error(self, scope: Scope) -> str | None:
        client = scope.get("client")
        ip = client[0] if client else "unknown"
        if not await self.limiter(
            f"demo:ip:{ip}",
            limit=self.rate_per_minute,
            window_seconds=60,
        ):
            return "rate_limited"
        if not await self.limiter(
            f"demo:ip:{ip}:day",
            limit=self.daily_cap,
            window_seconds=86400,
        ):
            return "daily_limit_reached"
        return None

    @staticmethod
    def _guarded_endpoint(scope: Scope) -> str | None:
        if scope["type"] != "http" or scope.get("method") != "POST":
            return None
        parts = scope.get("path", "").rstrip("/").split("/")
        if len(parts) != 4 or parts[1] != "demo":
            return None
        endpoint = parts[3]
        return endpoint if endpoint in {"messages", "audio"} else None

    @staticmethod
    def _content_length(scope: Scope) -> int | None:
        for name, value in scope.get("headers", ()):
            if name.lower() != b"content-length":
                continue
            try:
                parsed = int(value)
            except ValueError:
                return None
            return parsed if parsed >= 0 else None
        return None

    @staticmethod
    async def _reject(
        scope: Scope,
        receive: Receive,
        send: Send,
        status_code: int,
        detail: str,
    ) -> None:
        response = JSONResponse({"detail": detail}, status_code=status_code)
        await response(scope, receive, send)
