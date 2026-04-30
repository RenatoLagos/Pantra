from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin


class ToolIdempotency(TimestampMixin, Base):
    """Cached result of a tool call keyed by (business, tool, key).

    The LLM may retry the same tool call (network, restart, model retry).
    Before executing, the tool layer looks up this row; if present, it
    returns the cached result instead of re-running the side effect.
    """
    __tablename__ = "tool_idempotency"
    __table_args__ = (
        PrimaryKeyConstraint("business_id", "tool_name", "idempotency_key"),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )
    tool_name: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)
