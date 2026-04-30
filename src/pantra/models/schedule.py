from __future__ import annotations

import uuid
from datetime import time as time_t

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class PractitionerSchedule(UUIDPK, TimestampMixin, Base):
    """Weekly recurring availability for a practitioner.

    A practitioner may have several rows per day_of_week (e.g. morning shift
    + afternoon shift with a lunch gap).
    """
    __tablename__ = "practitioner_schedules"
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_schedule_day_of_week"),
        UniqueConstraint(
            "practitioner_id", "day_of_week", "start_time",
            name="uq_practitioner_dow_start",
        ),
    )

    practitioner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practitioners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # Monday=0 .. Sunday=6
    start_time: Mapped[time_t] = mapped_column(Time, nullable=False)
    end_time: Mapped[time_t] = mapped_column(Time, nullable=False)
