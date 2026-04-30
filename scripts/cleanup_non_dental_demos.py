"""Drop the non-dental demo businesses from a previously seeded DB.

Pantra now focuses on dental clinics only. This script is a one-shot
cleanup so the alembic migration that drops `restaurant_tables` and
`bookings.table_id` doesn't run into orphan data.

Usage:
    python -m scripts.cleanup_non_dental_demos
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from pantra.db import session_scope
from pantra.models import Business

SLUGS_TO_DROP = ("demo-restaurant", "demo-realestate")


async def cleanup() -> None:
    async with session_scope() as session:
        for slug in SLUGS_TO_DROP:
            biz = (
                await session.execute(select(Business).where(Business.slug == slug))
            ).scalar_one_or_none()
            if biz:
                await session.delete(biz)  # cascades to channels, customers, conversations, bookings, ...
                print(f"  [deleted] {slug}")
            else:
                print(f"  [skip] {slug} not present")


if __name__ == "__main__":
    asyncio.run(cleanup())
