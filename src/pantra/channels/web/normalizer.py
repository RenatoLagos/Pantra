from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from pantra.channels.whatsapp.normalizer import InboundMessage as _InboundMessage


@dataclass(slots=True)
class WebInbound:
    """Lightweight wrapper to construct an InboundMessage from a web POST."""
    business_slug: str
    session_id: str
    text: str | None
    audio_path: str | None
    inbound_kind: str  # 'text' | 'audio'


def to_inbound_message(web: WebInbound) -> _InboundMessage:
    """Adapt a web POST to the channel-agnostic InboundMessage shape used by
    services/conversation. Channel="web", channel_account_id=business_slug.
    """
    return _InboundMessage(
        channel="web",
        channel_account_id=web.business_slug,
        external_message_id=f"web:{web.session_id}:{datetime.utcnow().timestamp()}",
        external_user_id=web.session_id,
        user_display_name=None,
        text=web.text,
        raw={"kind": web.inbound_kind, "audio_path": web.audio_path} if web.audio_path else {"kind": web.inbound_kind},
        received_at=datetime.now(tz=timezone.utc),
    )
