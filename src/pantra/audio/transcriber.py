from __future__ import annotations

import io
from pathlib import Path

from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pantra.config import settings


class TranscriptionError(Exception):
    pass


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=0.5, max=4),
    reraise=True,
)
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

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    if isinstance(audio, (str, Path)):
        with open(audio, "rb") as f:
            audio_bytes = f.read()
        filename_hint = Path(audio).name
    else:
        audio_bytes = audio

    # The OpenAI SDK accepts a (filename, bytes) tuple.
    file_tuple = (filename_hint, io.BytesIO(audio_bytes))

    result = await client.audio.transcriptions.create(
        model="whisper-1",
        file=file_tuple,
        language=language,
        response_format="text",
    )
    # When response_format="text", result is a plain string.
    return result.strip() if isinstance(result, str) else getattr(result, "text", "").strip()
