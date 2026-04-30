from __future__ import annotations

import json

from pantra.llm.classifier import _parse


def test_parses_plain_json() -> None:
    raw = json.dumps({
        "language": "de",
        "intent": "booking_request",
        "urgency": "normal",
        "needs_human": False,
        "business_domain": "dental",
        "extracted": {"date": "2026-05-03", "time": "19:30", "party_size": 4},
    })
    out = _parse(raw)
    assert out.language == "de"
    assert out.intent == "booking_request"
    assert out.extracted.party_size == 4


def test_parses_fenced_json() -> None:
    raw = """```json
{
  "language": "en",
  "intent": "faq",
  "urgency": "low",
  "needs_human": false
}
```"""
    out = _parse(raw)
    assert out.intent == "faq"


def test_falls_back_safely_on_garbage() -> None:
    out = _parse("¯\\_(ツ)_/¯")
    # Degraded fallback flips needs_human so a human reviews.
    assert out.needs_human is True
