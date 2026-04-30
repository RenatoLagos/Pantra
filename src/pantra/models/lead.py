from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class LeadStatus(str, enum.Enum):
    new = "new"
    qualified = "qualified"
    contacted = "contacted"
    won = "won"
    lost = "lost"


class Lead(UUIDPK, TimestampMixin, Base):
    __tablename__ = "leads"

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

    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status"),
        default=LeadStatus.new,
        nullable=False,
    )
    score: Mapped[int | None] = mapped_column(Integer)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    value_estimate: Mapped[float | None] = mapped_column(Numeric(12, 2))
    next_action: Mapped[str | None] = mapped_column(String(256))
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
