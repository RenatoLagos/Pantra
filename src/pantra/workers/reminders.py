from __future__ import annotations

import asyncio
import uuid
from datetime import date as date_t
from datetime import datetime, timedelta, timezone
from datetime import time as time_t
from typing import Any, Literal, cast
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.channels.whatsapp import templates
from pantra.channels.whatsapp.adapter import WhatsAppAdapter
from pantra.config import settings
from pantra.db import session_scope
from pantra.logging import log
from pantra.models import (
    Booking,
    BookingStatus,
    Business,
    Channel,
    ChannelStatus,
    ChannelType,
    Customer,
    SentReminder,
    Service,
)
from pantra.workers.celery_app import celery_app

# (template name, lead time before the appointment). The template name doubles
# as the `kind` recorded in sent_reminders.
REMINDER_KINDS: tuple[tuple[str, timedelta], ...] = (
    ("reminder_24h", timedelta(hours=24)),
    ("reminder_2h", timedelta(hours=2)),
)

_ACTIVE_STATUSES = (BookingStatus.confirmed, BookingStatus.rescheduled)


# ─── Pure helpers (unit-testable, no I/O) ───────────────────────────────


class InvalidAppointmentWallTimeError(ValueError):
    """A local appointment time that cannot identify one real instant."""

    def __init__(self, reason: Literal["ambiguous", "nonexistent"]) -> None:
        self.reason = reason
        super().__init__(f"{reason} local appointment time")


def appointment_instant_utc(booking_date: date_t, booking_time: time_t, tz_name: str) -> datetime:
    """Resolve a booking's local (date, time) to an absolute UTC instant.

    Bookings are stored in the clinic's LOCAL wall-clock time (the LLM reasons
    in the business timezone) without an offset or PEP 495 fold. Reminders must
    never guess during DST gaps or overlaps, so both folds are validated by a
    UTC round-trip and ambiguous/nonexistent times are rejected. Scanner and
    sender callers catch that domain error and skip safely. A bad IANA name
    continues to degrade to UTC rather than crashing the scan.
    """
    try:
        tz: ZoneInfo | timezone = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc

    wall_time = datetime.combine(booking_date, booking_time)
    candidates: set[datetime] = set()
    for fold in (0, 1):
        localized = wall_time.replace(tzinfo=tz, fold=fold)
        instant = localized.astimezone(timezone.utc)
        round_trip = instant.astimezone(tz)
        if round_trip.replace(tzinfo=None) == wall_time and round_trip.fold == fold:
            candidates.add(instant)

    if not candidates:
        raise InvalidAppointmentWallTimeError("nonexistent")
    if len(candidates) > 1:
        raise InvalidAppointmentWallTimeError("ambiguous")
    return candidates.pop()


def is_reminder_due(
    *,
    booking_date: date_t,
    booking_time: time_t,
    tz_name: str,
    now: datetime,
    lead: timedelta,
    tol_seconds: int,
) -> bool:
    """True when the appointment is ~`lead` away from `now` (within tolerance).

    Working in absolute UTC instants (not time-of-day) is what makes this
    correct across midnight and across timezone offsets.
    """
    appt = appointment_instant_utc(booking_date, booking_time, tz_name)
    return abs((appt - (now + lead)).total_seconds()) <= tol_seconds


def reminder_language(preferred: str | None, business_default: str, kind: str) -> str:
    """Pick a template language the reminder template actually supports."""
    supported = templates.get(kind).languages
    for candidate in (preferred, business_default, "de"):
        if candidate and candidate in supported:
            return candidate
    return supported[0]


# ─── Scan (beat, every minute) ──────────────────────────────────────────


@celery_app.task(  # type: ignore[untyped-decorator]
    name="pantra.workers.reminders.scan_upcoming",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def scan_upcoming() -> dict[str, int]:
    return asyncio.run(_scan_upcoming())


async def _scan_upcoming() -> dict[str, int]:
    """Find bookings due for a T-24h / T-2h reminder and enqueue a send each.

    Idempotency lives in the send task, so it's fine (and safer) for the ±window
    to catch a booking in more than one scan.
    """
    now = datetime.now(tz=timezone.utc)
    tol = settings.reminder_window_seconds
    counts: dict[str, int] = {kind: 0 for kind, _ in REMINDER_KINDS}

    async with session_scope() as session:
        for kind, lead in REMINDER_KINDS:
            target = now + lead
            # Coarse date filter — a timezone offset can shift the LOCAL date by
            # a day at the edges, so scan ±1 day and let the precise instant
            # check below decide.
            candidate_dates = {(target + timedelta(days=d)).date() for d in (-1, 0, 1)}

            stmt = select(Booking).where(
                Booking.date.in_(candidate_dates),
                Booking.status.in_(_ACTIVE_STATUSES),
                Booking.is_demo.is_(False),
            )
            bookings = list((await session.execute(stmt)).scalars())
            if not bookings:
                continue

            business_ids = {b.business_id for b in bookings}
            businesses = {
                b.id: b
                for b in (
                    await session.execute(select(Business).where(Business.id.in_(business_ids)))
                ).scalars()
            }

            for booking in bookings:
                business = businesses.get(booking.business_id)
                tz_name = business.timezone if business else "UTC"
                try:
                    due = is_reminder_due(
                        booking_date=booking.date,
                        booking_time=booking.time,
                        tz_name=tz_name,
                        now=now,
                        lead=lead,
                        tol_seconds=tol,
                    )
                except InvalidAppointmentWallTimeError as exc:
                    _log_invalid_wall_time(
                        booking_id=str(booking.id),
                        kind=kind,
                        appointment_date=booking.date,
                        appointment_time=booking.time,
                        tz_name=tz_name,
                        reason=exc.reason,
                    )
                    continue
                if due:
                    _enqueue_reminder(booking, kind)
                    counts[kind] += 1

    log.info("reminders.scan", **counts)
    return counts


# ─── Send (one per appointment occurrence + kind) ──────────────────────


def _enqueue_reminder(booking: Booking, kind: str) -> None:
    """Snapshot the occurrence into the task so reschedules make it stale."""
    send_reminder.delay(
        str(booking.id),
        kind,
        booking.date.isoformat(),
        booking.time.isoformat(),
    )


@celery_app.task(  # type: ignore[untyped-decorator]
    name="pantra.workers.reminders.send_reminder",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_reminder(
    booking_id: str,
    kind: str,
    expected_date: str | None = None,
    expected_time: str | None = None,
) -> None:
    if expected_date is None or expected_time is None:
        # Safely discard tasks queued by a pre-occurrence-aware deployment.
        # The minute scanner will enqueue a fresh task with the snapshot.
        log.warning("reminders.skip_missing_occurrence", booking_id=booking_id, kind=kind)
        return
    asyncio.run(
        _send_reminder(
            booking_id,
            kind,
            date_t.fromisoformat(expected_date),
            time_t.fromisoformat(expected_time),
        )
    )


async def _send_reminder(
    booking_id: str,
    kind: str,
    expected_date: date_t,
    expected_time: time_t,
) -> None:
    """Deliver one reminder via an approved WhatsApp template.

    The booking row is locked before eligibility is checked and stays locked
    through the external send. PostgreSQL UPDATEs used by cancellation and
    rescheduling therefore serialize with this task: a stale task cannot send
    for an occurrence that changed first.

    The occurrence claim is committed only with a successful task transaction,
    so ordinary failures remain retryable and duplicate tasks for the same
    occurrence are suppressed. This is best-effort idempotency, NOT exactly-once
    delivery: a process/network failure after WhatsApp accepts the message but
    before the database commits can still produce a duplicate on retry.
    """
    async with session_scope() as session:
        stmt = select(Booking).where(Booking.id == uuid.UUID(booking_id)).with_for_update()
        booking = (await session.execute(stmt)).scalar_one_or_none()
        if (
            booking is None
            or booking.status not in _ACTIVE_STATUSES
            or booking.is_demo
            or booking.date != expected_date
            or booking.time != expected_time
        ):
            log.info(
                "reminders.skip_stale_or_inactive",
                booking_id=booking_id,
                kind=kind,
                expected_date=expected_date.isoformat(),
                expected_time=expected_time.isoformat(),
            )
            return

        customer = await session.get(Customer, booking.customer_id)
        business = await session.get(Business, booking.business_id)
        if (
            customer is None
            or business is None
            or customer.opted_out
            or customer.channel_type != ChannelType.whatsapp
            or not customer.external_user_id
        ):
            log.info("reminders.skip_no_recipient", booking_id=booking_id, kind=kind)
            return

        try:
            appointment_instant_utc(expected_date, expected_time, business.timezone)
        except InvalidAppointmentWallTimeError as exc:
            _log_invalid_wall_time(
                booking_id=booking_id,
                kind=kind,
                appointment_date=expected_date,
                appointment_time=expected_time,
                tz_name=business.timezone,
                reason=exc.reason,
            )
            return

        channel = (
            (
                await session.execute(
                    select(Channel).where(
                        Channel.business_id == business.id,
                        Channel.type == ChannelType.whatsapp,
                        Channel.status == ChannelStatus.active,
                    )
                )
            )
            .scalars()
            .first()
        )
        if channel is None:
            log.warning("reminders.no_whatsapp_channel", business_id=str(business.id))
            return

        if not await _claim(
            session,
            booking.id,
            kind,
            expected_date,
            expected_time,
        ):
            log.info("reminders.already_sent", booking_id=booking_id, kind=kind)
            return

        language = reminder_language(customer.preferred_language, business.default_language, kind)
        params = await _render_params(session, booking, customer, kind, language)

        adapter = WhatsAppAdapter(phone_number_id=channel.external_account_id)
        await adapter.send_template(
            to=customer.external_user_id,
            name=kind,
            language=language,
            params=params,
        )
        log.info("reminders.sent", booking_id=booking_id, kind=kind, language=language)


def _log_invalid_wall_time(
    *,
    booking_id: str,
    kind: str,
    appointment_date: date_t,
    appointment_time: time_t,
    tz_name: str,
    reason: Literal["ambiguous", "nonexistent"],
) -> None:
    log.warning(
        "reminders.skip_invalid_wall_time",
        booking_id=booking_id,
        kind=kind,
        appointment_date=appointment_date.isoformat(),
        appointment_time=appointment_time.isoformat(),
        timezone=tz_name,
        reason=reason,
    )


async def _claim(
    session: AsyncSession,
    booking_id: uuid.UUID,
    kind: str,
    appointment_date: date_t,
    appointment_time: time_t,
) -> bool:
    """Reserve one reminder kind for an appointment occurrence."""
    stmt = (
        pg_insert(SentReminder)
        .values(
            id=uuid.uuid4(),
            booking_id=booking_id,
            kind=kind,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )
        .on_conflict_do_nothing(
            index_elements=[
                "booking_id",
                "kind",
                "appointment_date",
                "appointment_time",
            ]
        )
    )
    result = await session.execute(stmt)
    return bool(cast(Any, result).rowcount)


async def _render_params(
    session: AsyncSession, booking: Booking, customer: Customer, kind: str, language: str
) -> list[str]:
    """Fill the template body parameters in the order the registry declares."""
    name = customer.name or "there"
    date_str = booking.date.isoformat()
    time_str = booking.time.strftime("%H:%M")

    if kind == "reminder_24h":
        service_name = "your appointment"
        if booking.service_id:
            service = await session.get(Service, booking.service_id)
            if service is not None:
                service_name = service.localized_name(language)
        return [name, service_name, date_str, time_str]

    # reminder_2h: (customer_name, date, time)
    return [name, date_str, time_str]
