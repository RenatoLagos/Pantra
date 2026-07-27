from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path

from pantra.config import settings
from pantra.logging import log
from pantra.workers.celery_app import celery_app


@celery_app.task(name="pantra.workers.audio_retention.purge_old_audio")
def purge_old_audio() -> int:
    """Delete audio files older than AUDIO_RETENTION_HOURS.

    Audio is sensitive PII (voice biometrics). Default retention: 24h.
    """
    cutoff = time.time() - timedelta(hours=settings.audio_retention_hours).total_seconds()
    deleted = 0
    # Sweep both the public TTS output tree and the private inbound-recordings
    # tree (raw patient voice lives outside audio_storage_path — see config).
    roots = [Path(settings.audio_storage_path), Path(settings.audio_inbound_path)]

    for storage in roots:
        if not storage.exists():
            continue
        for path in storage.rglob("*"):
            if path.is_file() and path.stat().st_mtime < cutoff:
                try:
                    path.unlink()
                    deleted += 1
                except OSError as e:
                    log.warning("audio_retention.unlink_failed", path=str(path), error=str(e))

    log.info("audio_retention.purged", deleted=deleted)
    return deleted
