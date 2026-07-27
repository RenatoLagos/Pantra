"""sent_reminders — idempotency ledger for appointment reminders

Revision ID: a1b2c3d4e5f6
Revises: c9d4a7e1b8f3
Create Date: 2026-07-08 01:00:00.000000

Backs best-effort reminder idempotency: one row per appointment occurrence and
kind suppresses scanner overlap and normal Celery retries while allowing the
same reminder kind after a booking is rescheduled.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "c9d4a7e1b8f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sent_reminders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("appointment_date", sa.Date(), nullable=False),
        sa.Column("appointment_time", sa.Time(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "booking_id",
            "kind",
            "appointment_date",
            "appointment_time",
            name="uq_sent_reminder_booking_kind_occurrence",
        ),
    )
    op.create_index("ix_sent_reminders_booking_id", "sent_reminders", ["booking_id"])


def downgrade() -> None:
    op.drop_index("ix_sent_reminders_booking_id", table_name="sent_reminders")
    op.drop_table("sent_reminders")
