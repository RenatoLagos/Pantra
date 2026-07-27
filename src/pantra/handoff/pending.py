from __future__ import annotations

import uuid
from dataclasses import dataclass

from pantra.models import HandoffTask


@dataclass(frozen=True, slots=True)
class PendingHandoffNotification:
    """A durable handoff that may be published only after transaction commit."""

    task: HandoffTask
    business_id: uuid.UUID
    conversation_id: uuid.UUID
    is_demo: bool
