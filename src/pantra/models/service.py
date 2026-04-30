from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class Service(UUIDPK, TimestampMixin, Base):
    __tablename__ = "services"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Stable code for tool calls / classifier keywords (e.g. 'checkup',
    # 'cleaning', 'filling', 'implant'). Unique per business.
    code: Mapped[str] = mapped_column(String(64), nullable=False)

    # Default name (in the business's default language) + translations.
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_translations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    description: Mapped[str | None] = mapped_column(String(1000))

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    price_cents: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")

    # If non-empty, only practitioners with at least one of these specialties
    # can perform the service.
    required_specialties: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Long-form treatment information. All multilanguage dicts: {"de": "...", "en": "..."}.
    # Populated by the seed and surfaced via the get_treatment_details tool.
    details_long: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    pre_care: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    post_care: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    contraindications: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    insurance_notes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    def localized_name(self, language: str | None) -> str:
        if not language:
            return self.name
        return (self.name_translations or {}).get(language) or self.name

    def localized(self, field: str, language: str) -> str | None:
        """Return the localized version of a multilanguage JSONB field."""
        value = getattr(self, field, None) or {}
        return value.get(language) or value.get("de") or value.get("en")
