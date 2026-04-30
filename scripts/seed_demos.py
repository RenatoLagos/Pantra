"""Seed the demo dental clinic business.

Usage:
    python -m scripts.seed_demos

Idempotent: re-running updates the existing row.
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from pantra.db import session_scope
from pantra.models import Business, BusinessDomain

DEMOS: list[dict] = [
    {
        "slug": "demo-dental",
        "name": "Zahnarztpraxis Berlin Mitte",
        "domain": BusinessDomain.dental,
        "default_language": "de",
        "supported_languages": ["de", "en"],
        "config": {
            "tone": "professional_calm",
            "emoji_policy": "none",
            "tts_mode": "mirror",
            "opening_hours": "Mo-Fr 8:00-19:00, Sa 9:00-13:00",
            "knowledge": [
                "Adresse: Friedrichstraße 100, 10117 Berlin.",
                "Telefon: +49 30 1234 5678.",
                "Notfälle werden am gleichen Tag eingeplant — bitte rufen Sie direkt an.",
                "Wir behandeln gesetzlich und privat versicherte Patienten.",
                "Sprachen im Team: Deutsch und Englisch.",
            ],
            # Always-relevant: injected verbatim into the system prompt in the
            # patient's language. Structured fields are also kept for future
            # tooling (refunds, automated reminders).
            "cancellation_policy": {
                "free_until_hours_before": 24,
                "late_cancel_fee_pct": 50,
                "no_show_fee_eur": 50,
                "exceptions": ["medical_emergency"],
                "human_text": {
                    "de": (
                        "Termine können bis 24 Stunden vorher kostenlos abgesagt werden. "
                        "Bei späterer Absage berechnen wir 50 % des Behandlungspreises. "
                        "Bei unentschuldigtem Nichterscheinen erheben wir eine Pauschale von 50 €. "
                        "Im Krankheitsfall mit ärztlichem Attest entfällt die Gebühr."
                    ),
                    "en": (
                        "Appointments can be cancelled free of charge up to 24 hours in advance. "
                        "Cancellations after that incur a fee of 50% of the treatment price. "
                        "No-shows are charged a flat €50 fee. "
                        "Cancellations due to medical emergency (with doctor's note) are exempt."
                    ),
                },
            },
        },
    },
]


async def seed() -> None:
    async with session_scope() as session:
        for spec in DEMOS:
            existing = (
                await session.execute(select(Business).where(Business.slug == spec["slug"]))
            ).scalar_one_or_none()

            if existing:
                existing.name = spec["name"]
                existing.domain = spec["domain"]
                existing.default_language = spec["default_language"]
                existing.supported_languages = spec["supported_languages"]
                existing.config = spec["config"]
                existing.is_demo = True
                action = "updated"
            else:
                session.add(
                    Business(
                        slug=spec["slug"],
                        name=spec["name"],
                        domain=spec["domain"],
                        default_language=spec["default_language"],
                        supported_languages=spec["supported_languages"],
                        config=spec["config"],
                        is_demo=True,
                    )
                )
                action = "created"
            print(f"  [{action}] {spec['slug']} — {spec['name']}")


if __name__ == "__main__":
    asyncio.run(seed())
