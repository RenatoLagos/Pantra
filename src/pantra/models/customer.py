from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK
from pantra.models.channel import ChannelType


class Customer(UUIDPK, TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint(
            "business_id", "channel_type", "external_user_id",
            name="uq_customer_business_channel_user",
        ),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_type: Mapped[ChannelType] = mapped_column(
        Enum(ChannelType, name="channel_type", create_type=False), nullable=False
    )
    external_user_id: Mapped[str] = mapped_column(String(128), nullable=False)

    name: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(32))
    instagram_username: Mapped[str | None] = mapped_column(String(64))
    preferred_language: Mapped[str | None] = mapped_column(String(8))

    # Structured customer memory: prior bookings, preferences, allergies,
    # property interests, etc. Lives across conversations.
    notes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    opted_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
