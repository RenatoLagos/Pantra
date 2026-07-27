from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, cast

import redis.asyncio as aioredis

from pantra.config import settings
from pantra.logging import log

_client: aioredis.Redis | None = None

_FIXED_WINDOW_SCRIPT = """
local count = redis.call("INCR", KEYS[1])
local ttl = redis.call("TTL", KEYS[1])
if count == 1 or ttl < 0 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end
return count
"""


def _redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.demo_ratelimit_redis_timeout_seconds,
            socket_timeout=settings.demo_ratelimit_redis_timeout_seconds,
        )
    return _client


async def allow(key: str, *, limit: int, window_seconds: int) -> bool:
    """Fixed-window rate check. Returns True when the action is allowed.

    Fails OPEN: if Redis is unreachable this returns True and logs a warning.
    These limits guard the LLM cost budget on public demo endpoints — they are
    not an authentication boundary, so a broker outage must not take the demo
    offline. The cost exposure during a Redis outage is an accepted trade-off.
    """
    try:
        client = _redis()
        # A Lua script executes atomically in Redis. There is no crash window
        # between INCR and EXPIRE that could leave a permanent counter behind;
        # the TTL check also repairs counters stranded by an older deployment.
        raw_count = await cast(
            Awaitable[Any],
            client.eval(_FIXED_WINDOW_SCRIPT, 1, key, str(window_seconds)),
        )
        count = int(raw_count)
        return count <= limit
    except Exception as exc:
        # Degrade gracefully on any Redis error (connection, timeout, ...).
        log.warning("ratelimit.unavailable", key=key, error=str(exc))
        return True
