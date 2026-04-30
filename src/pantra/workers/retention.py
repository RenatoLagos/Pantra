from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from pantra.config import settings
from pantra.db import session_scope
from pantra.logging import log
from pantra.models import AIRun
from pantra.workers.celery_app import celery_app


@celery_app.task(name="pantra.workers.retention.purge_prompt_logs")
def purge_prompt_logs() -> int:
    return asyncio.run(_purge_prompt_logs())


async def _purge_prompt_logs() -> int:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=settings.log_retention_days)
    async with session_scope() as session:
        result = await session.execute(
            delete(AIRun).where(AIRun.created_at < cutoff)
        )
    deleted = result.rowcount or 0
    log.info("retention.purged_prompt_logs", deleted=deleted, cutoff=cutoff.isoformat())
    return deleted
