from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pantra.channels.whatsapp.window import is_within_window


def test_no_inbound_means_closed() -> None:
    assert is_within_window(None) is False


def test_just_now_is_open() -> None:
    now = datetime.now(tz=timezone.utc)
    assert is_within_window(now, now) is True


def test_at_24h_boundary_is_open() -> None:
    now = datetime.now(tz=timezone.utc)
    last = now - timedelta(hours=24)
    assert is_within_window(last, now) is True


def test_just_past_24h_is_closed() -> None:
    now = datetime.now(tz=timezone.utc)
    last = now - timedelta(hours=24, seconds=1)
    assert is_within_window(last, now) is False
