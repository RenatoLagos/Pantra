from __future__ import annotations

import hashlib
import uuid
from datetime import date as date_t
from datetime import datetime, time as time_t, timedelta

from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from pantra.models import (
    Booking,
    BookingStatus,
    Practitioner,
    PractitionerSchedule,
    Service,
)
from pantra.tools.base import Tool, ToolContext, ToolError

SLOT_STEP = timedelta(minutes=30)


# ─── check_availability ─────────────────────────────────────────────────
class CheckAvailabilityIn(BaseModel):
    date: date_t = Field(description="Day to check. ISO format YYYY-MM-DD.")
    service_id: uuid.UUID | None = Field(
        default=None,
        description="Service to perform — drives duration + practitioner filter.",
    )
    duration_minutes: int | None = Field(
        default=None, description="Override duration when service_id isn't given."
    )
    time_from: time_t | None = Field(
        default=None,
        description="Window start (e.g. 08:00 for 'morning').",
    )
    time_to: time_t | None = Field(default=None, description="Window end.")
    practitioner_id: uuid.UUID | None = Field(
        default=None, description="Restrict to a specific practitioner."
    )
    max_results: int = 6


class AvailableSlot(BaseModel):
    practitioner_id: uuid.UUID
    practitioner_name: str
    start_time: time_t
    end_time: time_t


class CheckAvailabilityOut(BaseModel):
    slots: list[AvailableSlot]
    requested_practitioner_unavailable: bool = False
    note: str | None = None


class CheckAvailabilityTool(Tool[CheckAvailabilityIn, CheckAvailabilityOut]):
    name = "check_availability"
    description = (
        "Check actual slot availability against the clinic calendar. "
        "Returns up to N concrete slots (practitioner + start time) the "
        "patient can pick from. Always call this BEFORE proposing times."
    )
    input_model = CheckAvailabilityIn
    output_model = CheckAvailabilityOut

    async def _execute(
        self, ctx: ToolContext, payload: CheckAvailabilityIn
    ) -> CheckAvailabilityOut:
        duration = payload.duration_minutes or 30
        if payload.service_id:
            service = await ctx.session.get(Service, payload.service_id)
            if service and service.business_id == ctx.business_id:
                duration = service.duration_minutes

        pq = select(Practitioner).where(
            Practitioner.business_id == ctx.business_id,
            Practitioner.is_active.is_(True),
        )
        if payload.practitioner_id:
            pq = pq.where(Practitioner.id == payload.practitioner_id)
        practitioners = (await ctx.session.execute(pq)).scalars().all()

        if not practitioners:
            return CheckAvailabilityOut(
                slots=[],
                requested_practitioner_unavailable=bool(payload.practitioner_id),
                note="no_practitioners_available",
            )

        dow = payload.date.weekday()
        sq = select(PractitionerSchedule).where(
            PractitionerSchedule.practitioner_id.in_([p.id for p in practitioners]),
            PractitionerSchedule.day_of_week == dow,
        )
        schedules = (await ctx.session.execute(sq)).scalars().all()
        if not schedules:
            return CheckAvailabilityOut(slots=[], note="closed_on_this_day")

        bq = select(Booking).where(
            Booking.business_id == ctx.business_id,
            Booking.date == payload.date,
            Booking.practitioner_id.in_([p.id for p in practitioners]),
            Booking.status.in_(
                [BookingStatus.pending, BookingStatus.confirmed, BookingStatus.rescheduled]
            ),
        )
        existing = (await ctx.session.execute(bq)).scalars().all()
        by_p: dict[uuid.UUID, list[Booking]] = {}
        for b in existing:
            if b.practitioner_id:
                by_p.setdefault(b.practitioner_id, []).append(b)

        p_by_id = {p.id: p for p in practitioners}
        candidates: list[AvailableSlot] = []

        for sched in schedules:
            pract = p_by_id[sched.practitioner_id]
            slot_start = datetime.combine(payload.date, sched.start_time)
            sched_end = datetime.combine(payload.date, sched.end_time)
            if payload.time_from:
                slot_start = max(slot_start, datetime.combine(payload.date, payload.time_from))
            if payload.time_to:
                sched_end = min(sched_end, datetime.combine(payload.date, payload.time_to))

            while slot_start + timedelta(minutes=duration) <= sched_end:
                slot_end = slot_start + timedelta(minutes=duration)
                if not _has_conflict(by_p.get(pract.id, []), slot_start, slot_end):
                    candidates.append(
                        AvailableSlot(
                            practitioner_id=pract.id,
                            practitioner_name=pract.display_name,
                            start_time=slot_start.time(),
                            end_time=slot_end.time(),
                        )
                    )
                slot_start += SLOT_STEP

        candidates.sort(key=lambda s: (s.start_time, s.practitioner_name))
        return CheckAvailabilityOut(
            slots=candidates[: payload.max_results],
            requested_practitioner_unavailable=bool(payload.practitioner_id) and not candidates,
        )


# ─── create_booking ─────────────────────────────────────────────────────
class CreateBookingIn(BaseModel):
    date: date_t
    time: time_t
    practitioner_id: uuid.UUID | None = None
    service_id: uuid.UUID | None = None
    duration_minutes: int | None = None
    notes: str | None = None


class CreateBookingOut(BaseModel):
    booking_id: uuid.UUID
    status: BookingStatus
    practitioner_id: uuid.UUID | None = None
    service_id: uuid.UUID | None = None


class CreateBookingTool(Tool[CreateBookingIn, CreateBookingOut]):
    name = "create_booking"
    description = (
        "Create a booking. MUST be called only AFTER check_availability "
        "returned the chosen slot AND the patient confirmed."
    )
    input_model = CreateBookingIn
    output_model = CreateBookingOut

    async def _execute(self, ctx: ToolContext, payload: CreateBookingIn) -> CreateBookingOut:
        duration = payload.duration_minutes or 30
        if payload.service_id:
            service = await ctx.session.get(Service, payload.service_id)
            if service and service.business_id == ctx.business_id:
                duration = service.duration_minutes

        await _slot_lock(
            ctx.session, ctx.business_id, payload.practitioner_id, payload.date, payload.time
        )

        if payload.practitioner_id:
            slot_start = datetime.combine(payload.date, payload.time)
            slot_end = slot_start + timedelta(minutes=duration)

            bq = select(Booking).where(
                Booking.business_id == ctx.business_id,
                Booking.practitioner_id == payload.practitioner_id,
                Booking.date == payload.date,
                Booking.status.in_(
                    [BookingStatus.pending, BookingStatus.confirmed, BookingStatus.rescheduled]
                ),
            )
            same_day = (await ctx.session.execute(bq)).scalars().all()
            if _has_conflict(same_day, slot_start, slot_end):
                raise ToolError(
                    "slot_taken",
                    "The requested slot is no longer available.",
                    retriable=False,
                )

        booking = Booking(
            business_id=ctx.business_id,
            customer_id=ctx.customer_id,
            conversation_id=ctx.conversation_id,
            practitioner_id=payload.practitioner_id,
            service_id=payload.service_id,
            date=payload.date,
            time=payload.time,
            duration_minutes=duration,
            notes=payload.notes,
            status=BookingStatus.confirmed,
        )
        ctx.session.add(booking)
        await ctx.session.flush()
        return CreateBookingOut(
            booking_id=booking.id,
            status=booking.status,
            practitioner_id=booking.practitioner_id,
            service_id=booking.service_id,
        )


# ─── reschedule_booking ─────────────────────────────────────────────────
class RescheduleBookingIn(BaseModel):
    booking_id: uuid.UUID
    new_date: date_t
    new_time: time_t


class RescheduleBookingOut(BaseModel):
    booking_id: uuid.UUID
    status: BookingStatus


class RescheduleBookingTool(Tool[RescheduleBookingIn, RescheduleBookingOut]):
    name = "reschedule_booking"
    description = "Move an existing booking to a new date/time."
    input_model = RescheduleBookingIn
    output_model = RescheduleBookingOut

    async def _execute(
        self, ctx: ToolContext, payload: RescheduleBookingIn
    ) -> RescheduleBookingOut:
        booking = await ctx.session.get(Booking, payload.booking_id, with_for_update=True)
        if not booking or booking.business_id != ctx.business_id:
            raise ToolError("not_found", "Booking not found.")
        if booking.status in (BookingStatus.cancelled, BookingStatus.no_show):
            raise ToolError(
                "invalid_state", f"Cannot reschedule a {booking.status.value} booking."
            )

        await _slot_lock(
            ctx.session,
            ctx.business_id,
            booking.practitioner_id,
            payload.new_date,
            payload.new_time,
        )

        if booking.practitioner_id:
            new_start = datetime.combine(payload.new_date, payload.new_time)
            new_end = new_start + timedelta(minutes=booking.duration_minutes)
            bq = select(Booking).where(
                Booking.business_id == ctx.business_id,
                Booking.practitioner_id == booking.practitioner_id,
                Booking.date == payload.new_date,
                Booking.id != booking.id,
                Booking.status.in_(
                    [BookingStatus.pending, BookingStatus.confirmed, BookingStatus.rescheduled]
                ),
            )
            same_day = (await ctx.session.execute(bq)).scalars().all()
            if _has_conflict(same_day, new_start, new_end):
                raise ToolError("slot_taken", "The new slot is not available.")

        booking.date = payload.new_date
        booking.time = payload.new_time
        booking.status = BookingStatus.rescheduled
        await ctx.session.flush()
        return RescheduleBookingOut(booking_id=booking.id, status=booking.status)


# ─── cancel_booking ─────────────────────────────────────────────────────
class CancelBookingIn(BaseModel):
    booking_id: uuid.UUID
    reason: str | None = None


class CancelBookingOut(BaseModel):
    booking_id: uuid.UUID
    status: BookingStatus


class CancelBookingTool(Tool[CancelBookingIn, CancelBookingOut]):
    name = "cancel_booking"
    description = "Cancel a booking the patient no longer wants."
    input_model = CancelBookingIn
    output_model = CancelBookingOut

    async def _execute(self, ctx: ToolContext, payload: CancelBookingIn) -> CancelBookingOut:
        booking = await ctx.session.get(Booking, payload.booking_id, with_for_update=True)
        if not booking or booking.business_id != ctx.business_id:
            raise ToolError("not_found", "Booking not found.")
        booking.status = BookingStatus.cancelled
        if payload.reason:
            booking.notes = ((booking.notes or "") + f"\nCancellation reason: {payload.reason}").strip()
        await ctx.session.flush()
        return CancelBookingOut(booking_id=booking.id, status=booking.status)


# ─── helpers ────────────────────────────────────────────────────────────
def _has_conflict(
    bookings: list[Booking], slot_start: datetime, slot_end: datetime
) -> bool:
    for b in bookings:
        b_start = datetime.combine(b.date, b.time)
        b_end = b_start + timedelta(minutes=b.duration_minutes)
        if not (b_end <= slot_start or b_start >= slot_end):
            return True
    return False


async def _slot_lock(
    session: AsyncSession,
    business_id: uuid.UUID,
    practitioner_id: uuid.UUID | None,
    d: date_t,
    t: time_t,
) -> None:
    """Postgres advisory lock keyed on (business, practitioner, date, time)."""
    raw = f"{business_id}|{practitioner_id or '_'}|{d.isoformat()}|{t.isoformat()}"
    h = hashlib.blake2b(raw.encode(), digest_size=8).digest()
    key = int.from_bytes(h, "big", signed=True)
    await session.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": key})
