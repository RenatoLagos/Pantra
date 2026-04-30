from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from pantra.config import settings

celery_app = Celery(
    "pantra",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "pantra.workers.reminders",
        "pantra.workers.retention",
        "pantra.workers.audio_retention",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.timezone,
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "reminders.scan": {
        "task": "pantra.workers.reminders.scan_upcoming",
        # Every minute. The task itself is a quick query; only the
        # bookings inside the next 25h are considered.
        "schedule": crontab(minute="*"),
    },
    "retention.purge_prompt_logs": {
        "task": "pantra.workers.retention.purge_prompt_logs",
        # Daily at 03:30.
        "schedule": crontab(hour=3, minute=30),
    },
    "audio_retention.purge_old_audio": {
        "task": "pantra.workers.audio_retention.purge_old_audio",
        # Hourly — audio is sensitive PII, short retention window.
        "schedule": crontab(minute=0),
    },
}
