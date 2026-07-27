from __future__ import annotations

import io
from pathlib import Path

from openai import AsyncOpenAI

from pantra.config import settings


class TranscriptionError(Exception):
    pass


async def transcribe(
    audio: bytes | str | Path,
    *,
    language: str | None = None,
    filename_hint: str = "audio.ogg",
) -> str:
    """Transcribe audio to text using OpenAI Whisper.

    `audio` can be raw bytes (e.g. fetched from WhatsApp media or recorded
    in the browser) OR a filesystem path. `language` is an ISO 639-1 hint
    that improves accuracy and latency when known.
    """
    if not settings.openai_api_key:
        raise TranscriptionError("OPENAI_API_KEY is not configured")

    # Explicit timeout + bounded retries. The SDK retries connection errors,
    # timeouts, 429 and 5xx with backoff — scoped to transient failures, unlike
    # the previous blanket Exception retry that also burned latency on bad audio
    # or auth errors before re-raising.
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.stt_timeout_seconds,
        max_retries=settings.stt_max_retries,
    )

    if isinstance(audio, (str, Path)):
        with open(audio, "rb") as f:
            audio_bytes = f.read()
        filename_hint = Path(audio).name
    else:
        audio_bytes = audio

    # The OpenAI SDK accepts a (filename, bytes) tuple.
    file_tuple = (filename_hint, io.BytesIO(audio_bytes))

    if language is None:
        result = await client.audio.transcriptions.create(
            model="whisper-1",
            file=file_tuple,
            response_format="text",
        )
    else:
        result = await client.audio.transcriptions.create(
            model="whisper-1",
            file=file_tuple,
            language=language,
            response_format="text",
        )
    # When response_format="text", result is a plain string.
    return result.strip() if isinstance(result, str) else getattr(result, "text", "").strip()
