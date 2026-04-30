from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

import aiofiles

from pantra.config import settings


@dataclass(frozen=True, slots=True)
class AudioRef:
    filename: str
    path: Path
    public_url: str


async def save_audio(content: bytes, *, suffix: str = "mp3") -> AudioRef:
    """Persist audio to the configured storage and return path + public URL.

    MVP uses local filesystem at AUDIO_STORAGE_PATH, served via FastAPI
    StaticFiles at /static/audio. Phase 2 will swap to S3/R2 by replacing
    the body of this function.
    """
    filename = f"{uuid.uuid4().hex}.{suffix}"
    storage_dir = Path(settings.audio_storage_path)
    storage_dir.mkdir(parents=True, exist_ok=True)
    path = storage_dir / filename

    async with aiofiles.open(path, "wb") as f:
        await f.write(content)

    base = settings.audio_public_url_base.rstrip("/") if settings.audio_public_url_base else "/static/audio"
    public_url = f"{base}/{filename}"
    return AudioRef(filename=filename, path=path, public_url=public_url)


async def load_audio(filename: str) -> bytes:
    path = Path(settings.audio_storage_path) / filename
    async with aiofiles.open(path, "rb") as f:
        return await f.read()
