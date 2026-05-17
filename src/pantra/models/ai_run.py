from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class AIRun(UUIDPK, TimestampMixin, Base):
    __tablename__ = "ai_runs"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # 'classifier' | 'main' | 'summarizer' | 'fast_reply'
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)

    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    # Anthropic prompt-caching telemetry. cache_read_tokens are billed at
    # ~10% of input rate; cache_creation_tokens at ~125%. Both nullable
    # because older rows + non-caching providers won't populate them.
    cache_read_tokens: Mapped[int | None] = mapped_column(Integer)
    cache_creation_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    cost_estimate: Mapped[float | None] = mapped_column(Numeric(10, 6))

    # PII-redacted snapshots — see privacy/pii.py.
    classifier_output: Mapped[dict | None] = mapped_column(JSONB)
    router_decision: Mapped[dict | None] = mapped_column(JSONB)
    redacted_prompt: Mapped[str | None] = mapped_column(String)
