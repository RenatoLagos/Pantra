from __future__ import annotations

import os
import re

# Ensure tests run with a deterministic, non-secret env regardless of
# whatever .env the developer has lying around. MUST run before importing
# anything from `pantra` (config reads the environment at import time).
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://pantra:pantra@localhost:5432/pantra_test"
)
os.environ.setdefault(
    "DATABASE_URL_SYNC", "postgresql+psycopg2://pantra:pantra@localhost:5432/pantra_test"
)
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("PII_REDACTION_ENABLED", "true")

from datetime import date, time

import pytest
import pytest_asyncio
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from pantra.models import (
    Base,
    Booking,
    BookingStatus,
    Business,
    BusinessDomain,
    ChannelType,
    Customer,
)

# ─── Database fixtures ──────────────────────────────────────────────────
# These require a reachable Postgres (the CI workflow starts one; locally,
# point DATABASE_URL at a throwaway `pantra_test` DB). The schema is built
# from the models once per session; each test runs inside a transaction that
# is rolled back, so tests are isolated without recreating tables every time.


def _assert_safe_test_database_url(raw_url: str) -> None:
    """Reject destructive fixture DDL unless the database is clearly test-only.

    Inspect only the parsed database name: credentials, hosts and query-string
    parameters containing the word ``test`` must not make a production database
    look safe. Requiring ``test`` as a name token accepts the documented default
    (``pantra_test``) while rejecting ambiguous names such as ``contest``.
    """
    try:
        database = make_url(raw_url).database or ""
    except Exception as exc:
        raise RuntimeError("Refusing test DDL: DATABASE_URL is invalid") from exc

    tokens = {token for token in re.split(r"[^a-z0-9]+", database.lower()) if token}
    if "test" not in tokens:
        raise RuntimeError(
            "Refusing test DDL: DATABASE_URL must name a dedicated test database "
            f"(got {database!r})"
        )


@pytest.fixture
def database_url_guard():
    return _assert_safe_test_database_url


@pytest_asyncio.fixture(scope="session")
async def engine():
    database_url = os.environ["DATABASE_URL"]
    _assert_safe_test_database_url(database_url)
    eng = create_async_engine(database_url, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    conn = await engine.connect()
    trans = await conn.begin()
    maker = async_sessionmaker(bind=conn, expire_on_commit=False)
    sess = maker()
    try:
        yield sess
    finally:
        await sess.close()
        await trans.rollback()
        await conn.close()


@pytest_asyncio.fixture
async def sample_booking(session) -> Booking:
    """A minimal confirmed WhatsApp booking (business → customer → booking)."""
    business = Business(
        name="Test Clinic",
        domain=BusinessDomain.dental,
        timezone="Europe/Berlin",
        default_language="de",
        supported_languages=["de", "en"],
        slug="test-clinic",
    )
    session.add(business)
    await session.flush()

    customer = Customer(
        business_id=business.id,
        channel_type=ChannelType.whatsapp,
        external_user_id="4915100000000",
        name="Anna",
    )
    session.add(customer)
    await session.flush()

    booking = Booking(
        business_id=business.id,
        customer_id=customer.id,
        date=date(2026, 7, 9),
        time=time(10, 0),
        status=BookingStatus.confirmed,
    )
    session.add(booking)
    await session.flush()
    return booking
