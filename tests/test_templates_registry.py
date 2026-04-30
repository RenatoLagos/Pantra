from __future__ import annotations

import pytest

from pantra.channels.whatsapp import templates


def test_registry_has_required_templates() -> None:
    for name in ("reminder_24h", "reminder_2h", "booking_confirmation", "reengagement"):
        assert name in templates.REGISTRY


def test_unknown_template_raises() -> None:
    with pytest.raises(ValueError):
        templates.get("does-not-exist")


def test_draft_templates_are_not_approved() -> None:
    # MVP defaults are draft until Meta approves them.
    assert not templates.is_approved("reminder_24h")
