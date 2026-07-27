"""Reminder scheduling logic.

The pure tests below need no DB and pin down timezone offsets, DST
gaps/overlaps, and midnight/date rollover. Idempotency claim tests are
DB-backed because they exercise PostgreSQL ON CONFLICT and rollback behavior.
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy.dialects import postgresql

import pantra.workers.reminders as reminders
from pantra.workers.reminders import (
    InvalidAppointmentWallTimeError,
    _claim,
    _enqueue_reminder,
    _send_reminder,
    appointment_instant_utc,
    is_reminder_due,
    reminder_language,
    send_reminder,
)

BERLIN = "Europe/Berlin"  # UTC+2 in July (CEST)
LEAD_24H = timedelta(hours=24)
LEAD_2H = timedelta(hours=2)
TOL = 90


# ─── appointment_instant_utc ────────────────────────────────────────────


def test_local_time_converts_to_utc():
    # 10:00 in Berlin during July == 08:00 UTC.
    assert appointment_instant_utc(date(2026, 7, 9), time(10, 0), BERLIN) == datetime(
        2026, 7, 9, 8, 0, tzinfo=timezone.utc
    )


def test_local_time_respects_winter_offset():
    # Berlin is UTC+1 in January, not the UTC+2 summer offset.
    assert appointment_instant_utc(date(2026, 1, 9), time(10, 0), BERLIN) == datetime(
        2026, 1, 9, 9, 0, tzinfo=timezone.utc
    )


@pytest.mark.parametrize(
    ("booking_date", "booking_time", "expected"),
    [
        (
            date(2026, 3, 29),
            time(1, 30),
            datetime(2026, 3, 29, 0, 30, tzinfo=timezone.utc),
        ),
        (
            date(2026, 3, 29),
            time(3, 30),
            datetime(2026, 3, 29, 1, 30, tzinfo=timezone.utc),
        ),
        (
            date(2026, 10, 25),
            time(1, 30),
            datetime(2026, 10, 24, 23, 30, tzinfo=timezone.utc),
        ),
        (
            date(2026, 10, 25),
            time(3, 30),
            datetime(2026, 10, 25, 2, 30, tzinfo=timezone.utc),
        ),
    ],
)
def test_valid_times_around_dst_transitions(booking_date, booking_time, expected):
    assert appointment_instant_utc(booking_date, booking_time, BERLIN) == expected


def test_nonexistent_spring_wall_time_is_rejected():
    with pytest.raises(InvalidAppointmentWallTimeError, match="nonexistent"):
        appointment_instant_utc(date(2026, 3, 29), time(2, 30), BERLIN)


def test_ambiguous_autumn_wall_time_is_rejected():
    with pytest.raises(InvalidAppointmentWallTimeError, match="ambiguous"):
        appointment_instant_utc(date(2026, 10, 25), time(2, 30), BERLIN)


def test_bad_timezone_falls_back_to_utc():
    assert appointment_instant_utc(date(2026, 7, 9), time(10, 0), "Not/AZone") == datetime(
        2026, 7, 9, 10, 0, tzinfo=timezone.utc
    )


# ─── is_reminder_due: the timezone bug ──────────────────────────────────


def test_due_accounts_for_timezone_offset():
    # Appointment 10:00 Berlin == 08:00 UTC. 24h before is 2026-07-08 08:00 UTC.
    now = datetime(2026, 7, 8, 8, 0, tzinfo=timezone.utc)
    assert is_reminder_due(
        booking_date=date(2026, 7, 9),
        booking_time=time(10, 0),
        tz_name=BERLIN,
        now=now,
        lead=LEAD_24H,
        tol_seconds=TOL,
    )


def test_not_due_at_the_naive_utc_time_the_old_code_would_have_matched():
    # The old scan compared a UTC time-of-day (10:00) to the local booking time
    # (10:00), firing 2 hours late. Prove that 10:00 UTC is NOT the due moment.
    now = datetime(2026, 7, 8, 10, 0, tzinfo=timezone.utc)
    assert not is_reminder_due(
        booking_date=date(2026, 7, 9),
        booking_time=time(10, 0),
        tz_name=BERLIN,
        now=now,
        lead=LEAD_24H,
        tol_seconds=TOL,
    )


# ─── is_reminder_due: the midnight bug ──────────────────────────────────


def test_due_across_midnight_rollover():
    # Appointment 00:30 Berlin on the 10th == 22:30 UTC on the 9th. The 2h
    # reminder target is 20:30 UTC on the 9th — a different calendar day than
    # the appointment, which the old time-of-day window mishandled.
    now = datetime(2026, 7, 9, 20, 30, tzinfo=timezone.utc)
    assert is_reminder_due(
        booking_date=date(2026, 7, 10),
        booking_time=time(0, 30),
        tz_name=BERLIN,
        now=now,
        lead=LEAD_2H,
        tol_seconds=TOL,
    )


# ─── is_reminder_due: window boundaries ─────────────────────────────────


def test_due_within_tolerance():
    # 60 seconds before the exact target, tolerance 90s → still due.
    now = datetime(2026, 7, 8, 7, 59, 0, tzinfo=timezone.utc)
    assert is_reminder_due(
        booking_date=date(2026, 7, 9),
        booking_time=time(10, 0),
        tz_name=BERLIN,
        now=now,
        lead=LEAD_24H,
        tol_seconds=TOL,
    )


def test_not_due_outside_tolerance():
    now = datetime(2026, 7, 8, 7, 56, 0, tzinfo=timezone.utc)  # 4 min early
    assert not is_reminder_due(
        booking_date=date(2026, 7, 9),
        booking_time=time(10, 0),
        tz_name=BERLIN,
        now=now,
        lead=LEAD_24H,
        tol_seconds=TOL,
    )


def test_not_due_when_far_away():
    now = datetime(2026, 7, 1, 8, 0, tzinfo=timezone.utc)
    assert not is_reminder_due(
        booking_date=date(2026, 7, 9),
        booking_time=time(10, 0),
        tz_name=BERLIN,
        now=now,
        lead=LEAD_24H,
        tol_seconds=TOL,
    )


async def test_scanner_skips_invalid_legacy_wall_time(monkeypatch):
    business_id = uuid.uuid4()
    booking = SimpleNamespace(
        id=uuid.uuid4(),
        business_id=business_id,
        date=date(2026, 3, 29),
        time=time(2, 30),
    )
    business = SimpleNamespace(id=business_id, timezone=BERLIN)
    results = [[booking], [business], []]
    warnings: list[tuple[str, dict[str, object]]] = []

    class Result:
        def __init__(self, values):
            self.values = values

        def scalars(self):
            return self.values

    class Session:
        async def execute(self, _statement):
            return Result(results.pop(0))

    @asynccontextmanager
    async def fake_session_scope():
        yield Session()

    def unexpected_enqueue(*_args, **_kwargs):
        raise AssertionError("invalid wall time must not be enqueued")

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)
    monkeypatch.setattr(reminders, "_enqueue_reminder", unexpected_enqueue)
    monkeypatch.setattr(
        reminders.log,
        "warning",
        lambda event, **context: warnings.append((event, context)),
    )

    counts = await reminders._scan_upcoming()

    assert counts == {"reminder_24h": 0, "reminder_2h": 0}
    assert warnings == [
        (
            "reminders.skip_invalid_wall_time",
            {
                "booking_id": str(booking.id),
                "kind": "reminder_24h",
                "appointment_date": "2026-03-29",
                "appointment_time": "02:30:00",
                "timezone": BERLIN,
                "reason": "nonexistent",
            },
        )
    ]


# ─── reminder_language ──────────────────────────────────────────────────


def test_language_prefers_customer_language_when_supported():
    assert reminder_language("en", "de", "reminder_24h") == "en"


def test_language_falls_back_to_business_default():
    assert reminder_language("pt", "de", "reminder_24h") == "de"  # pt not in template


def test_language_falls_back_to_first_supported():
    assert reminder_language("pt", "xx", "reminder_2h") in ("de", "en", "es", "tr")


# ─── Idempotency (DB-backed) ────────────────────────────────────────────


async def test_claim_is_idempotent(session, sample_booking):
    first = await _claim(
        session,
        sample_booking.id,
        "reminder_24h",
        sample_booking.date,
        sample_booking.time,
    )
    second = await _claim(
        session,
        sample_booking.id,
        "reminder_24h",
        sample_booking.date,
        sample_booking.time,
    )
    assert first is True
    assert second is False


async def test_claim_is_per_kind(session, sample_booking):
    assert (
        await _claim(
            session,
            sample_booking.id,
            "reminder_24h",
            sample_booking.date,
            sample_booking.time,
        )
        is True
    )
    # A different reminder kind for the same booking is a separate claim.
    assert (
        await _claim(
            session,
            sample_booking.id,
            "reminder_2h",
            sample_booking.date,
            sample_booking.time,
        )
        is True
    )


async def test_claim_rearms_after_reschedule(session, sample_booking):
    assert (
        await _claim(
            session,
            sample_booking.id,
            "reminder_24h",
            sample_booking.date,
            sample_booking.time,
        )
        is True
    )
    assert (
        await _claim(
            session,
            sample_booking.id,
            "reminder_24h",
            date(2026, 7, 10),
            time(11, 30),
        )
        is True
    )


async def test_claim_can_retry_after_transaction_rollback(session, sample_booking):
    savepoint = await session.begin_nested()
    assert (
        await _claim(
            session,
            sample_booking.id,
            "reminder_24h",
            sample_booking.date,
            sample_booking.time,
        )
        is True
    )
    await savepoint.rollback()

    # The failed task's claim disappeared with its transaction, so a Celery
    # retry can reserve the same occurrence again.
    assert (
        await _claim(
            session,
            sample_booking.id,
            "reminder_24h",
            sample_booking.date,
            sample_booking.time,
        )
        is True
    )


# ─── Occurrence snapshot + stale-task locking ───────────────────────────


def test_enqueue_snapshots_expected_occurrence(monkeypatch):
    delayed: list[tuple[str, str, str, str]] = []
    monkeypatch.setattr(
        reminders.send_reminder,
        "delay",
        lambda *args: delayed.append(args),
    )
    booking = SimpleNamespace(
        id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        date=date(2026, 7, 9),
        time=time(10, 15),
    )

    _enqueue_reminder(booking, "reminder_2h")

    assert delayed == [
        (
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "reminder_2h",
            "2026-07-09",
            "10:15:00",
        )
    ]


def test_legacy_task_without_occurrence_is_safely_discarded(monkeypatch):
    run_calls: list[object] = []
    monkeypatch.setattr(reminders.asyncio, "run", run_calls.append)

    send_reminder("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", "reminder_2h")

    assert run_calls == []


async def test_stale_task_locks_booking_then_skips(monkeypatch):
    booking = SimpleNamespace(
        status=reminders.BookingStatus.rescheduled,
        is_demo=False,
        date=date(2026, 7, 10),
        time=time(11, 0),
    )

    class Result:
        def scalar_one_or_none(self):
            return booking

    class Session:
        statement = None

        async def execute(self, statement):
            self.statement = statement
            return Result()

    session = Session()

    @asynccontextmanager
    async def fake_session_scope():
        yield session

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)

    await _send_reminder(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "reminder_24h",
        date(2026, 7, 9),
        time(10, 0),
    )

    sql = str(session.statement.compile(dialect=postgresql.dialect()))
    assert "FOR UPDATE" in sql


@pytest.mark.parametrize(
    "status",
    [
        reminders.BookingStatus.pending,
        reminders.BookingStatus.cancelled,
        reminders.BookingStatus.no_show,
    ],
)
async def test_inactive_booking_is_not_sent(monkeypatch, status):
    booking = SimpleNamespace(
        status=status,
        is_demo=False,
        date=date(2026, 7, 9),
        time=time(10, 0),
    )

    class Result:
        def scalar_one_or_none(self):
            return booking

    class Session:
        async def execute(self, _statement):
            return Result()

        async def get(self, *_args):
            raise AssertionError("recipient lookup must not run")

    @asynccontextmanager
    async def fake_session_scope():
        yield Session()

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)

    await _send_reminder(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "reminder_24h",
        booking.date,
        booking.time,
    )


async def test_non_whatsapp_customer_is_not_sent(monkeypatch):
    customer_id = uuid.uuid4()
    business_id = uuid.uuid4()
    booking = SimpleNamespace(
        status=reminders.BookingStatus.confirmed,
        is_demo=False,
        date=date(2026, 7, 9),
        time=time(10, 0),
        customer_id=customer_id,
        business_id=business_id,
    )
    customer = SimpleNamespace(
        channel_type=reminders.ChannelType.web,
        external_user_id="web-session",
        opted_out=False,
    )
    business = SimpleNamespace(id=business_id)

    class Result:
        def scalar_one_or_none(self):
            return booking

    class Session:
        async def execute(self, _statement):
            return Result()

        async def get(self, model, _identifier):
            if model is reminders.Customer:
                return customer
            if model is reminders.Business:
                return business
            raise AssertionError("unexpected model lookup")

    @asynccontextmanager
    async def fake_session_scope():
        yield Session()

    async def unexpected_claim(*_args, **_kwargs):
        raise AssertionError("ineligible customer must not be claimed")

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)
    monkeypatch.setattr(reminders, "_claim", unexpected_claim)

    await _send_reminder(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "reminder_24h",
        booking.date,
        booking.time,
    )


async def test_opted_out_customer_is_not_claimed_or_sent(monkeypatch):
    customer_id = uuid.uuid4()
    business_id = uuid.uuid4()
    booking = SimpleNamespace(
        status=reminders.BookingStatus.confirmed,
        is_demo=False,
        date=date(2026, 7, 9),
        time=time(10, 0),
        customer_id=customer_id,
        business_id=business_id,
    )
    customer = SimpleNamespace(
        channel_type=reminders.ChannelType.whatsapp,
        external_user_id="4915100000000",
        opted_out=True,
    )
    business = SimpleNamespace(id=business_id, timezone=BERLIN)
    adapter_calls: list[str] = []

    class Result:
        def scalar_one_or_none(self):
            return booking

    class Session:
        async def execute(self, _statement):
            return Result()

        async def get(self, model, _identifier):
            if model is reminders.Customer:
                return customer
            if model is reminders.Business:
                return business
            raise AssertionError("unexpected model lookup")

    @asynccontextmanager
    async def fake_session_scope():
        yield Session()

    async def unexpected_claim(*_args, **_kwargs):
        raise AssertionError("opted-out customer must not be claimed")

    class UnexpectedAdapter:
        def __init__(self, **_kwargs):
            adapter_calls.append("adapter")

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)
    monkeypatch.setattr(reminders, "_claim", unexpected_claim)
    monkeypatch.setattr(reminders, "WhatsAppAdapter", UnexpectedAdapter)

    await _send_reminder(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "reminder_24h",
        booking.date,
        booking.time,
    )

    assert adapter_calls == []


async def test_channel_lookup_requires_active_whatsapp_channel(monkeypatch):
    customer_id = uuid.uuid4()
    business_id = uuid.uuid4()
    booking = SimpleNamespace(
        status=reminders.BookingStatus.confirmed,
        is_demo=False,
        date=date(2026, 7, 9),
        time=time(10, 0),
        customer_id=customer_id,
        business_id=business_id,
    )
    customer = SimpleNamespace(
        channel_type=reminders.ChannelType.whatsapp,
        external_user_id="4915100000000",
        opted_out=False,
    )
    business = SimpleNamespace(id=business_id, timezone=BERLIN)
    statements: list[object] = []

    class BookingResult:
        def scalar_one_or_none(self):
            return booking

    class EmptyChannelScalars:
        def first(self):
            return None

    class EmptyChannelResult:
        def scalars(self):
            return EmptyChannelScalars()

    class Session:
        async def execute(self, statement):
            statements.append(statement)
            return BookingResult() if len(statements) == 1 else EmptyChannelResult()

        async def get(self, model, _identifier):
            if model is reminders.Customer:
                return customer
            if model is reminders.Business:
                return business
            raise AssertionError("unexpected model lookup")

    @asynccontextmanager
    async def fake_session_scope():
        yield Session()

    async def unexpected_claim(*_args, **_kwargs):
        raise AssertionError("missing active channel must not be claimed")

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)
    monkeypatch.setattr(reminders, "_claim", unexpected_claim)

    await _send_reminder(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "reminder_24h",
        booking.date,
        booking.time,
    )

    channel_query = statements[1].compile(dialect=postgresql.dialect())
    assert reminders.ChannelType.whatsapp in channel_query.params.values()
    assert reminders.ChannelStatus.active in channel_query.params.values()


async def test_send_skips_invalid_wall_time_without_claim_or_adapter(monkeypatch):
    customer_id = uuid.uuid4()
    business_id = uuid.uuid4()
    booking = SimpleNamespace(
        status=reminders.BookingStatus.confirmed,
        is_demo=False,
        date=date(2026, 10, 25),
        time=time(2, 30),
        customer_id=customer_id,
        business_id=business_id,
    )
    customer = SimpleNamespace(
        channel_type=reminders.ChannelType.whatsapp,
        external_user_id="4915100000000",
        opted_out=False,
    )
    business = SimpleNamespace(id=business_id, timezone=BERLIN)
    warnings: list[tuple[str, dict[str, object]]] = []
    adapter_calls: list[str] = []

    class Result:
        def scalar_one_or_none(self):
            return booking

    class Session:
        async def execute(self, _statement):
            return Result()

        async def get(self, model, _identifier):
            if model is reminders.Customer:
                return customer
            if model is reminders.Business:
                return business
            raise AssertionError("unexpected model lookup")

    @asynccontextmanager
    async def fake_session_scope():
        yield Session()

    async def unexpected_claim(*_args, **_kwargs):
        raise AssertionError("invalid wall time must not be claimed")

    class UnexpectedAdapter:
        def __init__(self, **_kwargs):
            adapter_calls.append("adapter")

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)
    monkeypatch.setattr(reminders, "_claim", unexpected_claim)
    monkeypatch.setattr(reminders, "WhatsAppAdapter", UnexpectedAdapter)
    monkeypatch.setattr(
        reminders.log,
        "warning",
        lambda event, **context: warnings.append((event, context)),
    )

    await _send_reminder(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "reminder_24h",
        booking.date,
        booking.time,
    )

    assert adapter_calls == []
    assert warnings == [
        (
            "reminders.skip_invalid_wall_time",
            {
                "booking_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "kind": "reminder_24h",
                "appointment_date": "2026-10-25",
                "appointment_time": "02:30:00",
                "timezone": BERLIN,
                "reason": "ambiguous",
            },
        )
    ]


async def test_send_failure_rolls_back_claim_and_retry_can_send(monkeypatch):
    customer_id = uuid.uuid4()
    business_id = uuid.uuid4()
    booking = SimpleNamespace(
        id=uuid.uuid4(),
        status=reminders.BookingStatus.confirmed,
        is_demo=False,
        date=date(2026, 7, 9),
        time=time(10, 0),
        customer_id=customer_id,
        business_id=business_id,
        service_id=None,
    )
    customer = SimpleNamespace(
        channel_type=reminders.ChannelType.whatsapp,
        external_user_id="4915100000000",
        preferred_language="de",
        name="Anna",
        opted_out=False,
    )
    business = SimpleNamespace(id=business_id, default_language="de", timezone=BERLIN)
    channel = SimpleNamespace(external_account_id="phone-id")
    transaction_events: list[str] = []
    claim_calls: list[str] = []
    send_calls: list[str] = []

    class BookingResult:
        def scalar_one_or_none(self):
            return booking

    class ChannelScalars:
        def first(self):
            return channel

    class ChannelResult:
        def scalars(self):
            return ChannelScalars()

    class Session:
        execute_calls = 0

        async def execute(self, _statement):
            self.execute_calls += 1
            return BookingResult() if self.execute_calls == 1 else ChannelResult()

        async def get(self, model, _identifier):
            if model is reminders.Customer:
                return customer
            if model is reminders.Business:
                return business
            raise AssertionError("unexpected model lookup")

    @asynccontextmanager
    async def fake_session_scope():
        try:
            yield Session()
        except Exception:
            transaction_events.append("rollback")
            raise
        else:
            transaction_events.append("commit")

    async def fake_claim(*_args, **_kwargs):
        claim_calls.append("claim")
        return True

    class FakeAdapter:
        def __init__(self, *, phone_number_id):
            assert phone_number_id == "phone-id"

        async def send_template(self, **_kwargs):
            send_calls.append("send")
            if len(send_calls) == 1:
                raise RuntimeError("provider unavailable")

    monkeypatch.setattr(reminders, "session_scope", fake_session_scope)
    monkeypatch.setattr(reminders, "_claim", fake_claim)
    monkeypatch.setattr(reminders, "WhatsAppAdapter", FakeAdapter)

    args = (
        str(booking.id),
        "reminder_24h",
        booking.date,
        booking.time,
    )
    with pytest.raises(RuntimeError, match="provider unavailable"):
        await _send_reminder(*args)
    await _send_reminder(*args)

    assert transaction_events == ["rollback", "commit"]
    assert claim_calls == ["claim", "claim"]
    assert send_calls == ["send", "send"]


def test_sent_reminders_migration_chain_and_operations():
    path = (
        Path(__file__).parents[1]
        / "alembic"
        / "versions"
        / "20260708_0100_a1b2c3d4e5f6_sent_reminders.py"
    )
    spec = spec_from_file_location("sent_reminders_migration", path)
    assert spec is not None and spec.loader is not None
    migration = module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "a1b2c3d4e5f6"
    assert migration.down_revision == "c9d4a7e1b8f3"

    operations: list[tuple[str, str]] = []

    class FakeOp:
        def create_table(self, name, *_args, **_kwargs):
            operations.append(("create_table", name))

        def create_index(self, name, *_args, **_kwargs):
            operations.append(("create_index", name))

        def drop_index(self, name, *_args, **_kwargs):
            operations.append(("drop_index", name))

        def drop_table(self, name, *_args, **_kwargs):
            operations.append(("drop_table", name))

    migration.op = FakeOp()
    migration.upgrade()
    migration.downgrade()

    assert operations == [
        ("create_table", "sent_reminders"),
        ("create_index", "ix_sent_reminders_booking_id"),
        ("drop_index", "ix_sent_reminders_booking_id"),
        ("drop_table", "sent_reminders"),
    ]
