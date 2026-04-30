from __future__ import annotations

import uuid

from pydantic import BaseModel, Field
from sqlalchemy import select

from pantra.models import Practitioner, Service
from pantra.tools.base import Tool, ToolContext


# ─── list_services ──────────────────────────────────────────────────────
class ListServicesIn(BaseModel):
    language: str | None = Field(
        default=None,
        description="ISO 639-1 hint to localise service names. Falls back to default name.",
    )


class ServiceItem(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None = None
    duration_minutes: int
    price_eur: float | None = None


class ListServicesOut(BaseModel):
    services: list[ServiceItem]


class ListServicesTool(Tool[ListServicesIn, ListServicesOut]):
    name = "list_services"
    description = (
        "List the active services this business offers (name, duration, "
        "price). Call this when the customer asks 'what do you offer?' or "
        "before check_availability if you don't already know the service_id."
    )
    input_model = ListServicesIn
    output_model = ListServicesOut

    async def _execute(self, ctx: ToolContext, payload: ListServicesIn) -> ListServicesOut:
        rows = (
            await ctx.session.execute(
                select(Service)
                .where(Service.business_id == ctx.business_id, Service.is_active.is_(True))
                .order_by(Service.name)
            )
        ).scalars().all()
        items = [
            ServiceItem(
                id=s.id,
                code=s.code,
                name=s.localized_name(payload.language),
                description=s.description,
                duration_minutes=s.duration_minutes,
                price_eur=(s.price_cents / 100) if s.price_cents else None,
            )
            for s in rows
        ]
        return ListServicesOut(services=items)


# ─── list_practitioners ─────────────────────────────────────────────────
class ListPractitionersIn(BaseModel):
    service_id: uuid.UUID | None = Field(
        default=None,
        description="Filter to practitioners qualified for this service.",
    )
    language: str | None = Field(
        default=None,
        description="Filter to practitioners that speak this language.",
    )


class PractitionerItem(BaseModel):
    id: uuid.UUID
    name: str
    specialties: list[str]
    languages: list[str]
    bio: str | None = None


class ListPractitionersOut(BaseModel):
    practitioners: list[PractitionerItem]


class ListPractitionersTool(Tool[ListPractitionersIn, ListPractitionersOut]):
    name = "list_practitioners"
    description = (
        "List the practitioners (dentists / doctors / agents) this business "
        "has. Optionally filter by service or language. Use when the customer "
        "wants a specific person or asks 'who can attend me?'."
    )
    input_model = ListPractitionersIn
    output_model = ListPractitionersOut

    async def _execute(
        self, ctx: ToolContext, payload: ListPractitionersIn
    ) -> ListPractitionersOut:
        stmt = (
            select(Practitioner)
            .where(
                Practitioner.business_id == ctx.business_id,
                Practitioner.is_active.is_(True),
            )
            .order_by(Practitioner.name)
        )
        rows = (await ctx.session.execute(stmt)).scalars().all()

        # Service filter — only keep practitioners with at least one of the
        # service's required_specialties (or any practitioner if the service
        # has no requirements).
        if payload.service_id:
            service = await ctx.session.get(Service, payload.service_id)
            if service and service.required_specialties:
                req = set(service.required_specialties)
                rows = [p for p in rows if req.intersection(p.specialties or [])]

        if payload.language:
            rows = [p for p in rows if payload.language in (p.languages or [])]

        items = [
            PractitionerItem(
                id=p.id,
                name=p.display_name,
                specialties=p.specialties or [],
                languages=p.languages or [],
                bio=p.bio,
            )
            for p in rows
        ]
        return ListPractitionersOut(practitioners=items)
