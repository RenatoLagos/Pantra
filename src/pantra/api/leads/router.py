"""Marketing-lead capture endpoints (trial / demo).

These leads are PROSPECTS for Pantra (clinics interested in our product) —
distinct from the in-conversation ``Lead`` model under ``models/lead.py``,
which tracks leads that *Pantra* generates *for* a clinic from their
patients.

For now we don't persist marketing leads in Postgres. Each submission is
emailed to the founder via the existing handoff/email path and logged
structured for later analytics. Adding a ``MarketingLead`` model + alembic
migration is a follow-up if/when we need a CRM-like view.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from fastapi import APIRouter, HTTPException

from pantra.config import settings
from pantra.handoff.email import send_resend_raw
from pantra.logging import log

router = APIRouter()

# Where the founder receives marketing leads. Reuses the existing
# ``handoff_email_to`` env so the founder doesn't have to maintain a
# second address; if you eventually want a separate sales inbox, add
# ``leads_email_to`` to settings and switch here.
LEAD_NOTIFY_EMAIL = settings.handoff_email_to


class TrialRequest(BaseModel):
    """Public trial-form payload from /einzelpraxis."""

    contact_name: str = Field(min_length=1, max_length=120)
    clinic_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=64)
    consent_dsgvo: bool
    source: str = Field(default="einzelpraxis", max_length=64)
    languages_interested: list[str] | None = None


class DemoRequest(BaseModel):
    """Public demo-form payload — same shape, different intent."""

    contact_name: str = Field(min_length=1, max_length=120)
    clinic_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=64)
    preferred_time: str | None = Field(default=None, max_length=64)
    consent_dsgvo: bool
    source: str = Field(default="einzelpraxis", max_length=64)


def _ensure_consent(consent: bool) -> None:
    # DSGVO requires explicit opt-in. Without it we won't process the lead
    # at all — the form-side checkbox is `required` so this is defence in
    # depth against a misbehaving client.
    if not consent:
        raise HTTPException(
            status_code=400,
            detail="DSGVO-Einwilligung ist erforderlich.",
        )


async def _notify_founder(*, kind: str, payload: dict[str, str | bool | list | None]) -> None:
    """Email the founder with the new lead.

    ``send_email`` is a no-op when no email provider is configured — the
    structured log below still captures everything.
    """
    if not LEAD_NOTIFY_EMAIL:
        log.warning("leads.notify_skipped_no_recipient", kind=kind)
        return

    body_lines = [
        f"Neuer Pantra Lead ({kind})",
        "",
        f"Praxis: {payload.get('clinic_name')}",
        f"Kontakt: {payload.get('contact_name')}",
        f"Email: {payload.get('email')}",
        f"Telefon: {payload.get('phone') or '(keine)'}",
        f"Quelle: {payload.get('source')}",
    ]
    if payload.get("preferred_time"):
        body_lines.append(f"Bevorzugte Zeit: {payload['preferred_time']}")
    if payload.get("languages_interested"):
        body_lines.append(
            f"Sprachen-Interesse: {', '.join(payload['languages_interested'] or [])}"
        )
    body_lines += [
        "",
        f"DSGVO-Einwilligung: {'ja' if payload.get('consent_dsgvo') else 'nein'}",
    ]

    await send_resend_raw(
        to=LEAD_NOTIFY_EMAIL,
        subject=f"Pantra Lead — {payload.get('clinic_name')} ({kind})",
        text="\n".join(body_lines),
    )


@router.post("/api/leads/trial", status_code=201)
async def submit_trial(request: TrialRequest) -> dict[str, str]:
    _ensure_consent(request.consent_dsgvo)
    payload = request.model_dump()
    log.info(
        "leads.trial_submitted",
        clinic=request.clinic_name,
        email=request.email,
        source=request.source,
    )
    await _notify_founder(kind="trial", payload=payload)
    return {"status": "ok"}


@router.post("/api/leads/demo", status_code=201)
async def submit_demo(request: DemoRequest) -> dict[str, str]:
    _ensure_consent(request.consent_dsgvo)
    payload = request.model_dump()
    log.info(
        "leads.demo_submitted",
        clinic=request.clinic_name,
        email=request.email,
        source=request.source,
    )
    await _notify_founder(kind="demo", payload=payload)
    return {"status": "ok"}
