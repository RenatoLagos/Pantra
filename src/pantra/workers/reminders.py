from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from pantra.db import session_scope
from pantra.logging import log
from pantra.models import Booking, BookingStatus
from pantra.workers.celery_app import celery_app


@celery_app.task(name="pantra.workers.reminders.scan_upcoming")
def scan_upcoming() -> dict[str, int]:
    return asyncio.run(_scan_upcoming())


async def _scan_upcoming() -> dict[str, int]:
    """Find bookings that need a reminder (T-24h or T-2h) and enqueue.

    The check is window-based: a booking gets a reminder if its scheduled
    time falls inside (24h ± 1min) or (2h ± 1min) from now. This task runs
    every minute, so the ±1min window catches each booking exactly once.
    """
    now = datetime.now(tz=timezone.utc)
    counts = {"t24h": 0, "t2h": 0}

    async with session_scope() as session:
        for label, delta in (("t24h", timedelta(hours=24)), ("t2h", timedelta(hours=2))):
            target_low = (now + delta - timedelta(seconds=30)).time()
            target_high = (now + delta + timedelta(seconds=30)).time()
            target_date = (now + delta).date()

            stmt = select(Booking).where(
                Booking.date == target_date,
                Booking.time >= target_low,
                Booking.time <= target_high,
                Booking.status.in_([BookingStatus.confirmed, BookingStatus.rescheduled]),
            )
            for booking in (await session.execute(stmt)).scalars():
                send_reminder.delay(str(booking.id), label)
                counts[label] += 1

    log.info("reminders.scan", **counts)
    return counts


@celery_app.task(name="pantra.workers.reminders.send_reminder")
def send_reminder(booking_id: str, label: str) -> None:
    asyncio.run(_send_reminder(booking_id, label))


async def _send_reminder(booking_id: str, label: str) -> None:
    """Send the reminder via WhatsApp template (always — outside the 24h
    window we MUST use a template anyway, and inside the window using a
    template is still allowed).
    """
    # Wired in a follow-up change: load Customer, Channel, render
    # parameters from Booking, call WhatsAppAdapter.send_template.
    log.info("reminders.send.todo", booking_id=booking_id, label=label)
