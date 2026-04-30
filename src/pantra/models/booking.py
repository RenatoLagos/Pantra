from __future__ import annotations

import enum
import uuid
from datetime import date as date_t
from datetime import time as time_t

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    rescheduled = "rescheduled"
    no_show = "no_show"


class Booking(UUIDPK, TimestampMixin, Base):
    __tablename__ = "bookings"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True,
    )

    # resource_id is opaque per business: 'table-12', 'doctor-anna',
    # 'apartment-charlottenburg-1'. Slot uniqueness lives at the tool layer.
    resource_id: Mapped[str | None] = mapped_column(String(64), index=True)
    service_type: Mapped[str | None] = mapped_column(String(64))

    # Structured links — populated when the business has them in catalog.
    # Resource_id stays for free-form fallbacks.
    practitioner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practitioners.id", ondelete="SET NULL"),
        index=True,
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        index=True,
    )

    date: Mapped[date_t] = mapped_column(Date, nullable=False, index=True)
    time: Mapped[time_t] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    party_size: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status"),
        default=BookingStatus.pending,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)

    external_calendar_event_id: Mapped[str | None] = mapped_column(String(256))
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
