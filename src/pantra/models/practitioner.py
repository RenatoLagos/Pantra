from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pantra.models.base import Base, TimestampMixin, UUIDPK


class Practitioner(UUIDPK, TimestampMixin, Base):
    __tablename__ = "practitioners"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "Dr." / "Dra." / "Hyg." / ""
    title: Mapped[str | None] = mapped_column(String(16))
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # Free-text specialties: ["Implantology", "Orthodontics", ...]
    specialties: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    languages: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    photo_url: Mapped[str | None] = mapped_column(String(512))
    bio: Mapped[str | None] = mapped_column(String(2000))

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Demo flag inherited from business at creation time for fast filtering.
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    @property
    def display_name(self) -> str:
        return f"{self.title} {self.name}".strip() if self.title else self.name
