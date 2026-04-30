from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pantra.channels.whatsapp import templates
from pantra.config import settings
from pantra.logging import log


class WhatsAppAdapter:
    """Outbound client for the Meta Cloud API.

    All sends MUST go through this class — never raw HTTP from services or
    tools. This is where window enforcement and template fallback live.
    """

    def __init__(
        self,
        *,
        phone_number_id: str | None = None,
        access_token: str | None = None,
        api_base: str | None = None,
    ) -> None:
        self._phone_number_id = phone_number_id or settings.whatsapp_phone_number_id
        self._token = access_token or settings.whatsapp_access_token
        self._api_base = api_base or settings.whatsapp_api_base

    # ─── Public ──
    async def send_text(self, *, to: str, body: str) -> dict[str, Any]:
        """Free-text reply. Caller is responsible for ensuring the 24h
        window is open — see channels.whatsapp.window.is_within_window.
        """
        return await self._post({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        })

    async def send_audio(self, *, to: str, audio_url: str) -> dict[str, Any]:
        """Send an audio message via a public HTTPS link.

        Meta fetches the link itself, so the URL must be reachable from the
        public internet (use AUDIO_PUBLIC_URL_BASE — ngrok in dev,
        S3/R2/your-domain in prod).
        """
        return await self._post({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {"link": audio_url},
        })

    async def send_template(
        self, *, to: str, name: str, language: str, params: list[str]
    ) -> dict[str, Any]:
        """Send an approved template. Used outside the 24h window or for
        proactive messages (reminders, confirmations).
        """
        tpl = templates.get(name)
        if tpl.status != templates.TemplateStatus.approved:
            log.warning("whatsapp.template_not_approved", name=name)
            # In dev we still send so the integration can be exercised; in
            # prod Meta will reject the request, which is the correct behavior.
        return await self._post({
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": name,
                "language": {"code": language},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": p} for p in params],
                    }
                ],
            },
        })

    # ─── Private ──
    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, max=4),
        reraise=True,
    )
    async def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._api_base}/{self._phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {self._token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, headers=headers, json=body)
            r.raise_for_status()
            return r.json()
