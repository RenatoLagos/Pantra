"""Populate the demo dental clinic with practitioners, services, schedules
and ~one year of partially-booked agenda.

Idempotent: re-running wipes the previous practitioner/service/booking
catalog for `demo-dental` and re-creates it deterministically. Customer rows
that were created by real demo prospects are left alone — only the
synthetic "filler" customers are reset.

Usage:
    python -m scripts.seed_dental_clinic
"""
from __future__ import annotations

import asyncio
import random
import uuid
from datetime import date, datetime, time, timedelta

from sqlalchemy import delete, select

from pantra.db import session_scope
from pantra.models import (
    Booking,
    BookingStatus,
    Business,
    ChannelType,
    Customer,
    Practitioner,
    PractitionerSchedule,
    Service,
)

RNG = random.Random(42)
TODAY = date.today()
HORIZON_DAYS = 365
SLOT_STEP_MIN = 30
TARGET_OCCUPANCY = 0.32   # ~32% of working slots filled
SYNTHETIC_USER_PREFIX = "synthetic:dental:"


# ─── Practitioners ──────────────────────────────────────────────────────
PRACTITIONERS: list[dict] = [
    {
        "code": "anna",
        "title": "Dra.",
        "name": "Anna Schmidt",
        "specialties": ["general", "checkup", "cleaning"],
        "languages": ["de", "en"],  # MVP: DE + EN only
        "bio": "Especialista en odontología preventiva. 12 años de experiencia.",
        "schedule": {
            0: [(time(8, 0), time(13, 0))],   # Mon morning
            1: [(time(8, 0), time(13, 0))],   # Tue morning
            2: [(time(8, 0), time(13, 0))],   # Wed morning
            3: [(time(8, 0), time(13, 0))],   # Thu morning
            4: [(time(8, 0), time(13, 0))],   # Fri morning
        },
    },
    {
        "code": "markus",
        "title": "Dr.",
        "name": "Markus Weber",
        "specialties": ["general", "filling", "endodontics", "checkup"],
        "languages": ["de", "en"],  # MVP: DE + EN only
        "bio": "Endodoncia y restauraciones. Atiende también urgencias.",
        "schedule": {
            0: [(time(14, 0), time(19, 0))],
            1: [(time(14, 0), time(19, 0))],
            2: [(time(14, 0), time(19, 0))],
            3: [(time(14, 0), time(19, 0))],
            4: [(time(14, 0), time(19, 0))],
            5: [(time(9, 0), time(13, 0))],   # Sat morning
        },
    },
    {
        "code": "elena",
        "title": "Dr.",
        "name": "Sebastian Krause",
        "specialties": ["implantology", "implant", "general"],
        "languages": ["de", "en"],  # MVP: DE + EN only
        "bio": "Implantologe mit 9 Jahren Erfahrung. Patienten auf Deutsch und Englisch.",
        "schedule": {
            0: [(time(8, 0), time(13, 0)), (time(14, 0), time(18, 0))],
            1: [(time(8, 0), time(13, 0)), (time(14, 0), time(18, 0))],
            2: [(time(8, 0), time(13, 0)), (time(14, 0), time(18, 0))],
            3: [(time(8, 0), time(13, 0))],
            4: [(time(8, 0), time(13, 0))],
        },
    },
    {
        "code": "sarah",
        "title": "Dr.",
        "name": "Sarah Klein",
        "specialties": ["general", "cleaning", "bleaching", "checkup"],
        "languages": ["de", "en"],
        "bio": "Ästhetische Zahnmedizin und Bleaching. Patienten auf Deutsch und Englisch.",
        "schedule": {
            1: [(time(10, 0), time(18, 0))],
            2: [(time(10, 0), time(18, 0))],
            3: [(time(10, 0), time(18, 0))],
            4: [(time(10, 0), time(18, 0))],
            5: [(time(9, 0), time(13, 0))],
        },
    },
]


# ─── Services ───────────────────────────────────────────────────────────
SERVICES: list[dict] = [
    {
        "code": "checkup",
        "name": "Kontrolluntersuchung",
        "name_translations": {"es": "Revisión general", "en": "Check-up", "tr": "Kontrol muayenesi"},
        "description": "Revisión general, panorámica si hace falta.",
        "duration_minutes": 30,
        "price_cents": 5000,
        "required_specialties": ["checkup", "general"],
    },
    {
        "code": "cleaning",
        "name": "Professionelle Zahnreinigung",
        "name_translations": {"es": "Limpieza dental", "en": "Teeth cleaning", "tr": "Diş temizliği"},
        "description": "Limpieza profesional con ultrasonido y pulido.",
        "duration_minutes": 45,
        "price_cents": 9000,
        "required_specialties": ["cleaning", "general"],
    },
    {
        "code": "filling",
        "name": "Füllung",
        "name_translations": {"es": "Empaste", "en": "Filling", "tr": "Dolgu"},
        "description": "Empaste de composite por diente.",
        "duration_minutes": 60,
        "price_cents": 12000,
        "required_specialties": ["filling", "general"],
    },
    {
        "code": "implant",
        "name": "Implantatberatung",
        "name_translations": {"es": "Consulta de implante", "en": "Implant consultation", "tr": "İmplant danışmanlığı"},
        "description": "Primera consulta para evaluar implante. Incluye TC si necesario.",
        "duration_minutes": 60,
        "price_cents": 15000,
        "required_specialties": ["implant", "implantology"],
    },
    {
        "code": "bleaching",
        "name": "Bleaching",
        "name_translations": {"es": "Blanqueamiento", "en": "Whitening", "tr": "Beyazlatma"},
        "description": "Blanqueamiento profesional en consultorio.",
        "duration_minutes": 90,
        "price_cents": 35000,
        "required_specialties": ["bleaching", "general"],
    },
    {
        "code": "root_canal",
        "name": "Wurzelbehandlung",
        "name_translations": {"es": "Endodoncia", "en": "Root canal", "tr": "Kanal tedavisi"},
        "description": "Tratamiento de conducto. Requiere normalmente 2 sesiones.",
        "duration_minutes": 60,
        "price_cents": 24000,
        "required_specialties": ["endodontics", "general"],
    },
]


# ─── Synthetic patients (for the filler bookings) ───────────────────────
SYNTHETIC_PATIENTS: list[str] = [
    "Anna Müller", "Klaus Schmidt", "Sophie Bauer", "Michael Weber",
    "Elif Demir", "Mehmet Yılmaz", "Ayşe Kaya", "Hasan Çelik",
    "María Rodríguez", "Carlos García", "Lucía Fernández", "Pablo López",
    "John Smith", "Emma Wilson", "Liam Brown", "Olivia Davis",
    "Lena Hoffmann", "Tobias Fischer", "Julia Schneider", "Felix Wagner",
    "Aylin Şahin", "Burak Özdemir", "Zeynep Yıldız",
    "Pierre Martin", "Camille Dubois", "Lin Chen", "Wei Zhang",
    "Priya Patel", "Arjun Singh", "Noor Ahmed",
    "Sara Becker", "Niklas Hartmann", "Hannah Koch",
]


async def seed() -> None:
    async with session_scope() as session:
        biz = (
            await session.execute(select(Business).where(Business.slug == "demo-dental"))
        ).scalar_one_or_none()
        if not biz:
            raise SystemExit("demo-dental business not found — run scripts/seed_demos.py first")

        # ─ Wipe previous synthetic data ───────────────────────────────
        await session.execute(
            delete(Booking).where(
                Booking.business_id == biz.id,
                Booking.customer_id.in_(
                    select(Customer.id).where(
                        Customer.business_id == biz.id,
                        Customer.external_user_id.like(f"{SYNTHETIC_USER_PREFIX}%"),
                    )
                ),
            )
        )
        await session.execute(
            delete(Customer).where(
                Customer.business_id == biz.id,
                Customer.external_user_id.like(f"{SYNTHETIC_USER_PREFIX}%"),
            )
        )
        # Wipe the catalog and rebuild — keeps practitioner_id stable across
        # runs by making it deterministic from a slug+code seed.
        await session.execute(
            delete(PractitionerSchedule).where(
                PractitionerSchedule.practitioner_id.in_(
                    select(Practitioner.id).where(Practitioner.business_id == biz.id)
                )
            )
        )
        await session.execute(delete(Practitioner).where(Practitioner.business_id == biz.id))
        await session.execute(delete(Service).where(Service.business_id == biz.id))

        # ─ Create services ────────────────────────────────────────────
        services_by_code: dict[str, Service] = {}
        for spec in SERVICES:
            svc = Service(
                business_id=biz.id,
                code=spec["code"],
                name=spec["name"],
                name_translations=spec["name_translations"],
                description=spec["description"],
                duration_minutes=spec["duration_minutes"],
                price_cents=spec["price_cents"],
                required_specialties=spec["required_specialties"],
                is_active=True,
                is_demo=biz.is_demo,
            )
            session.add(svc)
            services_by_code[spec["code"]] = svc
        await session.flush()

        # ─ Create practitioners + schedules ──────────────────────────
        practitioners: list[Practitioner] = []
        for spec in PRACTITIONERS:
            p = Practitioner(
                business_id=biz.id,
                title=spec["title"],
                name=spec["name"],
                specialties=spec["specialties"],
                languages=spec["languages"],
                bio=spec["bio"],
                is_active=True,
                is_demo=biz.is_demo,
            )
            session.add(p)
            await session.flush()
            for dow, ranges in spec["schedule"].items():
                for start, end in ranges:
                    session.add(
                        PractitionerSchedule(
                            practitioner_id=p.id,
                            day_of_week=dow,
                            start_time=start,
                            end_time=end,
                        )
                    )
            practitioners.append(p)
        await session.flush()

        # ─ Create synthetic patients ─────────────────────────────────
        synth_customers: list[Customer] = []
        for i, name in enumerate(SYNTHETIC_PATIENTS):
            c = Customer(
                business_id=biz.id,
                channel_type=ChannelType.web,
                external_user_id=f"{SYNTHETIC_USER_PREFIX}{i:02d}",
                name=name,
                preferred_language=RNG.choice(["de", "en", "es", "tr"]),
                is_demo=biz.is_demo,
            )
            session.add(c)
            synth_customers.append(c)
        await session.flush()

        # ─ Generate bookings spanning the next year ──────────────────
        services = list(services_by_code.values())
        bookings_added = 0

        # Preload schedules ONCE keyed by (practitioner_id, day_of_week).
        all_schedules = (
            await session.execute(
                select(PractitionerSchedule).where(
                    PractitionerSchedule.practitioner_id.in_([p.id for p in practitioners])
                )
            )
        ).scalars().all()
        sched_by_p_dow: dict[tuple[uuid.UUID, int], list[PractitionerSchedule]] = {}
        for s in all_schedules:
            sched_by_p_dow.setdefault((s.practitioner_id, s.day_of_week), []).append(s)

        for offset in range(HORIZON_DAYS):
            d = TODAY + timedelta(days=offset)
            dow = d.weekday()

            for p in practitioners:
                schedules = sched_by_p_dow.get((p.id, dow), [])

                for sched in schedules:
                    cursor = datetime.combine(d, sched.start_time)
                    sched_end = datetime.combine(d, sched.end_time)
                    while cursor < sched_end:
                        if RNG.random() < TARGET_OCCUPANCY:
                            # Pick a service compatible with this practitioner.
                            picks = [
                                s for s in services
                                if not s.required_specialties
                                or set(s.required_specialties).intersection(p.specialties)
                            ]
                            svc = RNG.choice(picks) if picks else RNG.choice(services)
                            slot_dur = timedelta(minutes=svc.duration_minutes)
                            if cursor + slot_dur > sched_end:
                                cursor += timedelta(minutes=SLOT_STEP_MIN)
                                continue

                            customer = RNG.choice(synth_customers)
                            booking = Booking(
                                business_id=biz.id,
                                customer_id=customer.id,
                                practitioner_id=p.id,
                                service_id=svc.id,
                                date=d,
                                time=cursor.time(),
                                duration_minutes=svc.duration_minutes,
                                status=BookingStatus.confirmed,
                                is_demo=biz.is_demo,
                            )
                            session.add(booking)
                            bookings_added += 1
                            cursor += slot_dur
                        else:
                            cursor += timedelta(minutes=SLOT_STEP_MIN)

            if offset % 30 == 0:
                await session.flush()  # keep memory bounded

        await session.flush()

        print(f"  [seeded] practitioners={len(practitioners)}")
        print(f"  [seeded] services={len(services)}")
        print(f"  [seeded] synthetic_patients={len(synth_customers)}")
        print(f"  [seeded] bookings={bookings_added} (≈{TARGET_OCCUPANCY*100:.0f}% slot occupancy)")
        print(f"  [seeded] horizon={HORIZON_DAYS} days starting {TODAY.isoformat()}")


if __name__ == "__main__":
    asyncio.run(seed())
