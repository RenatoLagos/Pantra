from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK
from pantra.models.channel import ChannelType


class ConversationStatus(str, enum.Enum):
    active = "active"
    waiting_customer = "waiting_customer"
    human_needed = "human_needed"
    closed = "closed"


class Conversation(UUIDPK, TimestampMixin, Base):
    __tablename__ = "conversations"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel_type: Mapped[ChannelType] = mapped_column(
        Enum(ChannelType, name="channel_type", create_type=False), nullable=False
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status"),
        default=ConversationStatus.active,
        nullable=False,
    )

    current_intent: Mapped[str | None] = mapped_column(String(64))
    language: Mapped[str | None] = mapped_column(String(8))

    # Closes the WhatsApp 24h customer-service window. Updated on every
    # inbound message — outbound free text is only allowed within 24h of this.
    last_inbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Rolling summary, refreshed by the memory summarizer worker.
    summary: Mapped[str | None] = mapped_column(Text)

    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)


class MessageSender(str, enum.Enum):
    customer = "customer"
    ai = "ai"
    human = "human"
    system = "system"


class Message(UUIDPK, TimestampMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint(
            "conversation_id", "channel_message_id",
            name="uq_message_conversation_external",
        ),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender: Mapped[MessageSender] = mapped_column(
        Enum(MessageSender, name="message_sender"),
        nullable=False,
    )
    # External (WhatsApp) message id — used for idempotent webhook delivery.
    channel_message_id: Mapped[str | None] = mapped_column(String(128))
    text: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)
    language: Mapped[str | None] = mapped_column(String(8))
