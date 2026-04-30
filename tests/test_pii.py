from __future__ import annotations

from pantra.privacy import pii


def test_redacts_email() -> None:
    assert "[REDACTED_EMAIL]" in pii.redact("ping me at renato@example.com please")


def test_redacts_phone_de() -> None:
    out = pii.redact("Ruf mich an: +49 30 12345678")
    assert "[REDACTED_PHONE]" in out
    assert "12345678" not in out


def test_redacts_iban() -> None:
    assert "[REDACTED_IBAN]" in pii.redact("Account: DE89370400440532013000")


def test_redacts_credit_card() -> None:
    assert "[REDACTED_CARD]" in pii.redact("card 4111 1111 1111 1111 expires soon")


def test_keeps_short_numbers() -> None:
    # Reservations like "table for 4 at 20:15" must not be over-redacted.
    out = pii.redact("table for 4 at 20:15")
    assert "4" in out
    assert "20:15" in out


def test_redacts_combined() -> None:
    out = pii.redact("call +49 151 12345678 or write to a@b.de")
    assert "[REDACTED_PHONE]" in out
    assert "[REDACTED_EMAIL]" in out
