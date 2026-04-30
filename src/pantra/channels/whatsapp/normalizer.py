from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class InboundMessage:
    """Channel-agnostic shape consumed by services/conversation.py.

    `text` is the textual content of the message. For audio messages it
    starts as None — services/conversation transcribes via Whisper before
    classification. `audio_media_id` lets the service layer fetch the audio
    from Meta on demand. `raw` retains the full payload for debugging.
    """
    channel: str
    channel_account_id: str           # Meta phone_number_id receiving the msg
    external_message_id: str
    external_user_id: str             # customer's WhatsApp wa_id
    user_display_name: str | None
    text: str | None
    raw: dict
    received_at: datetime
    audio_media_id: str | None = None  # WhatsApp media id for audio messages


def parse_inbound(payload: dict) -> Iterable[InboundMessage]:
    """Walk a Meta webhook payload and yield one InboundMessage per supported msg.

    Supported types: 'text', 'audio'. Other media types currently skipped —
    the service layer can flag them for human handoff later.
    """
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id", "")
            contacts = {c["wa_id"]: c for c in value.get("contacts", [])}

            for msg in value.get("messages", []):
                msg_type = msg.get("type")
                wa_id = msg.get("from", "")
                contact = contacts.get(wa_id, {})
                received_at = (
                    datetime.fromtimestamp(int(msg["timestamp"]), tz=timezone.utc)
                    if "timestamp" in msg
                    else datetime.now(tz=timezone.utc)
                )

                if msg_type == "text":
                    yield InboundMessage(
                        channel="whatsapp",
                        channel_account_id=phone_number_id,
                        external_message_id=msg.get("id", ""),
                        external_user_id=wa_id,
                        user_display_name=(contact.get("profile") or {}).get("name"),
                        text=(msg.get("text") or {}).get("body"),
                        raw=msg,
                        received_at=received_at,
                    )
                elif msg_type == "audio":
                    yield InboundMessage(
                        channel="whatsapp",
                        channel_account_id=phone_number_id,
                        external_message_id=msg.get("id", ""),
                        external_user_id=wa_id,
                        user_display_name=(contact.get("profile") or {}).get("name"),
                        text=None,  # filled in by services after Whisper
                        raw=msg,
                        received_at=received_at,
                        audio_media_id=(msg.get("audio") or {}).get("id"),
                    )
                # Other media types (image, document, location) are ignored
                # for MVP. The service layer can flag them for handoff later.
