from __future__ import annotations

import enum
from dataclasses import dataclass


class TemplateStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    paused = "paused"


@dataclass(frozen=True, slots=True)
class Template:
    """Meta-approved template definition.

    The actual content lives in WhatsApp Business Manager; this registry
    only tracks the name + parameter schema the app expects to fill in.
    """
    name: str
    languages: tuple[str, ...]
    parameters: tuple[str, ...]
    status: TemplateStatus
    purpose: str  # human-readable: 'reminder_24h', 'booking_confirmation', etc.


# MVP registry. Extend as templates are approved by Meta.
REGISTRY: dict[str, Template] = {
    "reminder_24h": Template(
        name="reminder_24h",
        languages=("de", "en", "es", "tr"),
        parameters=("customer_name", "service", "date", "time"),
        status=TemplateStatus.draft,
        purpose="appointment reminder, 24 hours before",
    ),
    "reminder_2h": Template(
        name="reminder_2h",
        languages=("de", "en", "es", "tr"),
        parameters=("customer_name", "date", "time"),
        status=TemplateStatus.draft,
        purpose="appointment reminder, 2 hours before",
    ),
    "booking_confirmation": Template(
        name="booking_confirmation",
        languages=("de", "en", "es", "tr"),
        parameters=("customer_name", "service", "date", "time"),
        status=TemplateStatus.draft,
        purpose="confirm a booking that was just created",
    ),
    "reengagement": Template(
        name="reengagement",
        languages=("de", "en", "es", "tr"),
        parameters=("customer_name",),
        status=TemplateStatus.draft,
        purpose="reopen the 24h window with a soft prompt",
    ),
}


def get(name: str) -> Template:
    try:
        return REGISTRY[name]
    except KeyError as e:
        raise ValueError(f"unknown template: {name!r}") from e


def is_approved(name: str) -> bool:
    return REGISTRY.get(name, None) is not None and REGISTRY[name].status == TemplateStatus.approved
