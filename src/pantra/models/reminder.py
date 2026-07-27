from __future__ import annotations

import uuid
from datetime import date as date_t
from datetime import time as time_t

from sqlalchemy import Date, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import UUIDPK, Base, TimestampMixin


class SentReminder(UUIDPK, TimestampMixin, Base):
    """Best-effort idempotency ledger for appointment reminder occurrences.

    A rescheduled booking is a new occurrence and may receive the same reminder
    kind again, while scanner overlap and normal task retries for the exact same
    occurrence reuse one claim.
    """

    __tablename__ = "sent_reminders"
    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            "kind",
            "appointment_date",
            "appointment_time",
            name="uq_sent_reminder_booking_kind_occurrence",
        ),
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 'reminder_24h' | 'reminder_2h' — matches the WhatsApp template name.
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    appointment_date: Mapped[date_t] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time_t] = mapped_column(Time, nullable=False)
