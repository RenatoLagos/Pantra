from __future__ import annotations

import enum
import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class KnowledgeCategory(str, enum.Enum):
    faq = "faq"
    policy = "policy"
    treatment_detail = "treatment_detail"
    insurance = "insurance"
    pricing = "pricing"
    practical = "practical"
    safety = "safety"
    other = "other"


class KnowledgeEntry(UUIDPK, TimestampMixin, Base):
    """A single piece of knowledge: FAQ, policy, treatment detail, etc.

    Phase 1 uses Postgres full-text search via `to_tsvector('simple', ...)`.
    Phase 2 will add an `embedding` Vector column for semantic search; the
    public tool interface stays identical.
    """
    __tablename__ = "knowledge_entries"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(8), nullable=False, index=True)

    # `title` doubles as the FAQ question. `body` is the full answer (markdown OK).
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Optional link to a service (when the entry is about a specific treatment).
    related_service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
