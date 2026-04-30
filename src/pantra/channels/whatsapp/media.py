from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pantra.config import settings


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, max=4),
    reraise=True,
)
async def download_media(media_id: str, *, access_token: str | None = None) -> bytes:
    """Two-step Meta media fetch:
        1) GET /<media_id> → JSON with a short-lived signed `url`
        2) GET <url> → raw bytes (still requires the bearer token)
    """
    token = access_token or settings.whatsapp_access_token
    if not token:
        raise RuntimeError("whatsapp_access_token is not configured")

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=15) as client:
        meta_resp = await client.get(
            f"{settings.whatsapp_api_base}/{media_id}",
            headers=headers,
        )
        meta_resp.raise_for_status()
        signed_url = meta_resp.json().get("url")
        if not signed_url:
            raise RuntimeError(f"no url returned for media {media_id}")

        bin_resp = await client.get(signed_url, headers=headers)
        bin_resp.raise_for_status()
        return bin_resp.content
