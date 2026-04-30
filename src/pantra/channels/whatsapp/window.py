from __future__ import annotations

from datetime import datetime, timedelta, timezone

WHATSAPP_WINDOW = timedelta(hours=24)


def is_within_window(last_inbound_at: datetime | None, now: datetime | None = None) -> bool:
    """Free-text replies are only allowed inside the 24h customer service window.

    Outside the window only approved templates can be sent.
    """
    if last_inbound_at is None:
        return False
    now = now or datetime.now(tz=timezone.utc)
    return (now - last_inbound_at) <= WHATSAPP_WINDOW
