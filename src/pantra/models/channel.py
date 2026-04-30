from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class ChannelType(str, enum.Enum):
    whatsapp = "whatsapp"
    web = "web"               # demo/sandbox channel — no Meta, no 24h window
    instagram = "instagram"   # reserved for Phase 2


class ChannelStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    disconnected = "disconnected"


class Channel(UUIDPK, TimestampMixin, Base):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("type", "external_account_id", name="uq_channel_type_account"),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[ChannelType] = mapped_column(Enum(ChannelType, name="channel_type"), nullable=False)
    external_account_id: Mapped[str] = mapped_column(String(128), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[ChannelStatus] = mapped_column(
        Enum(ChannelStatus, name="channel_status"),
        default=ChannelStatus.active,
        nullable=False,
    )
    # credentials_reference points to a secrets-manager key, NEVER raw tokens.
    credentials_reference: Mapped[str | None] = mapped_column(String(256))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
