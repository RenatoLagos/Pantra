from __future__ import annotations

import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class BusinessDomain(str, enum.Enum):
    restaurant = "restaurant"
    clinic = "clinic"
    dental = "dental"
    beauty = "beauty"
    real_estate = "real_estate"
    other = "other"


class Business(UUIDPK, TimestampMixin, Base):
    __tablename__ = "businesses"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[BusinessDomain] = mapped_column(
        Enum(BusinessDomain, name="business_domain"),
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Europe/Berlin")
    default_language: Mapped[str] = mapped_column(String(8), nullable=False, default="de")
    supported_languages: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=lambda: ["de", "en", "es", "tr"]
    )

    # tone_config drives the system prompt: tone, emoji_policy, handoff_policy,
    # opening_hours, booking_rules, faq snippets, integration secrets.
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Demo / sandbox flag. Demo businesses are isolated from prod metrics +
    # never trigger real Telegram/email handoffs.
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    # Stable slug for routing demo URLs (e.g. /demo/restaurant). Unique when set.
    slug: Mapped[str | None] = mapped_column(String(64), unique=True)
