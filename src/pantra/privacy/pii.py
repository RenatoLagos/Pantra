from __future__ import annotations

import re

# Patterns are intentionally conservative — false positives are fine
# (we're redacting), false negatives are NOT (we'd leak PII to logs).

_EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# E.164-ish + common DE / international formats. Catches +49 30 1234567,
# 030/12345678, 0151-12345678, +1 (415) 555-1212, etc.
_PHONE = re.compile(r"""
    (?<![\w])                         # not preceded by word char
    (?:\+?\d{1,3}[\s\-/.]?)?          # optional country code
    (?:\(?\d{2,4}\)?[\s\-/.]?)        # area / city
    \d{2,4}[\s\-/.]?\d{2,5}           # subscriber
    (?![\w])                          # not followed by word char
""", re.VERBOSE)

# IBAN: 2 country letters + 2 check digits + up to 30 alnum chars
_IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")

# DE Personalausweis (10 digits) and similar long ID strings.
_LONG_ID = re.compile(r"\b\d{9,12}\b")

# Credit card-ish (13-19 digits with optional separators). The negative
# lookbehind prevents it from eating international phones that start with
# `+CC` (e.g. +49 151 12345678) — those should fall through to _PHONE.
_CREDIT_CARD = re.compile(r"(?<!\+)\b(?:\d[ -]?){13,19}\b")

_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (_EMAIL, "[REDACTED_EMAIL]"),
    (_IBAN, "[REDACTED_IBAN]"),
    (_CREDIT_CARD, "[REDACTED_CARD]"),
    (_PHONE, "[REDACTED_PHONE]"),
    (_LONG_ID, "[REDACTED_ID]"),
)


def redact(text: str) -> str:
    """Replace PII matches with stable placeholder tokens.

    Order matters: longer / more specific patterns run first so they win
    over the looser phone / id patterns.
    """
    out = text
    for pattern, replacement in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out
