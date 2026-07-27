from __future__ import annotations

import pytest
from redis import asyncio as aioredis

import pantra.ratelimit as ratelimit
from pantra.config import settings


class FakeRedis:
    def __init__(
        self,
        counts: list[int] | None = None,
        error: Exception | None = None,
    ) -> None:
        self.counts = iter(counts or [])
        self.error = error
        self.calls: list[tuple[str, int, str, str]] = []

    async def eval(self, script: str, numkeys: int, key: str, window_seconds: str) -> int:
        self.calls.append((script, numkeys, key, window_seconds))
        if self.error:
            raise self.error
        return next(self.counts)


async def test_fixed_window_uses_atomic_script_with_ttl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedis([1])
    monkeypatch.setattr(ratelimit, "_redis", lambda: redis)

    assert await ratelimit.allow("demo:test", limit=2, window_seconds=60) is True

    script, numkeys, key, ttl = redis.calls[0]
    assert 'redis.call("INCR", KEYS[1])' in script
    assert 'redis.call("TTL", KEYS[1])' in script
    assert "ttl < 0" in script
    assert 'redis.call("EXPIRE", KEYS[1], ARGV[1])' in script
    assert (numkeys, key, ttl) == (1, "demo:test", "60")


async def test_fixed_window_rejects_count_over_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedis([3])
    monkeypatch.setattr(ratelimit, "_redis", lambda: redis)

    assert await ratelimit.allow("demo:test", limit=2, window_seconds=60) is False


async def test_rate_limit_fails_open_when_redis_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedis(error=ConnectionError("redis unavailable"))
    monkeypatch.setattr(ratelimit, "_redis", lambda: redis)

    assert await ratelimit.allow("demo:test", limit=1, window_seconds=60) is True


def test_redis_client_uses_bounded_timeouts(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    sentinel = object()

    def fake_from_url(url: str, **kwargs: object) -> object:
        captured["url"] = url
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(ratelimit, "_client", None)
    monkeypatch.setattr(settings, "redis_url", "redis://rate-limit.test/0")
    monkeypatch.setattr(
        settings,
        "demo_ratelimit_redis_timeout_seconds",
        0.25,
    )
    monkeypatch.setattr(aioredis, "from_url", fake_from_url)

    assert ratelimit._redis() is sentinel
    assert captured == {
        "url": "redis://rate-limit.test/0",
        "decode_responses": True,
        "socket_connect_timeout": 0.25,
        "socket_timeout": 0.25,
    }
