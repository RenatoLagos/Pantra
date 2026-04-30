from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pantra.config import settings


class SynthesisError(Exception):
    pass


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=0.5, max=4),
    reraise=True,
)
async def synthesize(
    text: str,
    *,
    voice_id: str | None = None,
    model_id: str | None = None,
) -> bytes:
    """Synthesize speech with ElevenLabs. Returns MP3 bytes.

    Voice and model are env-configurable. The default voice is multilingual
    so DE / EN / ES / TR work without picking a different voice per language.
    TR is in beta with the multilingual model — early demos may need to
    fall back to text_only for Turkish if quality is unacceptable.
    """
    if not settings.elevenlabs_api_key:
        raise SynthesisError("ELEVENLABS_API_KEY is not configured")

    voice = voice_id or settings.elevenlabs_voice_id
    model = model_id or settings.elevenlabs_model_id

    url = f"{settings.elevenlabs_api_base}/text-to-speech/{voice}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return r.content
