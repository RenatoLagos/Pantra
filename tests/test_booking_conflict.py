"""Pure unit tests for booking slot-overlap detection.

`_has_conflict` is the safety-critical core of double-booking prevention. It's a
pure function over booking-like objects, so it needs no DB — SimpleNamespace
stand-ins are enough.
"""
from __future__ import annotations

from datetime import date, datetime, time
from types import SimpleNamespace

from pantra.tools.booking import _has_conflict

DAY = date(2026, 7, 9)


def _booking(hour: int, minute: int, duration: int):
    return SimpleNamespace(date=DAY, time=time(hour, minute), duration_minutes=duration)


def test_adjacent_slots_do_not_conflict():
    existing = [_booking(10, 0, 30)]  # 10:00-10:30
    start, end = datetime.combine(DAY, time(10, 30)), datetime.combine(DAY, time(11, 0))
    assert _has_conflict(existing, start, end) is False


def test_slot_ending_at_existing_start_does_not_conflict():
    existing = [_booking(10, 0, 30)]  # 10:00-10:30
    start, end = datetime.combine(DAY, time(9, 30)), datetime.combine(DAY, time(10, 0))
    assert _has_conflict(existing, start, end) is False


def test_overlapping_slots_conflict():
    existing = [_booking(10, 0, 60)]  # 10:00-11:00
    start, end = datetime.combine(DAY, time(10, 30)), datetime.combine(DAY, time(11, 0))
    assert _has_conflict(existing, start, end) is True


def test_existing_slot_enclosing_new_conflicts():
    existing = [_booking(10, 0, 120)]  # 10:00-12:00
    start, end = datetime.combine(DAY, time(10, 30)), datetime.combine(DAY, time(11, 0))
    assert _has_conflict(existing, start, end) is True


def test_slot_starting_before_existing_but_overlapping_conflicts():
    existing = [_booking(10, 0, 60)]  # 10:00-11:00
    start, end = datetime.combine(DAY, time(9, 30)), datetime.combine(DAY, time(10, 30))
    assert _has_conflict(existing, start, end) is True


def test_slot_enclosing_existing_conflicts():
    existing = [_booking(10, 0, 30)]  # 10:00-10:30
    start, end = datetime.combine(DAY, time(9, 30)), datetime.combine(DAY, time(11, 0))
    assert _has_conflict(existing, start, end) is True


def test_exact_same_slot_conflicts():
    existing = [_booking(9, 0, 30)]  # 09:00-09:30
    start, end = datetime.combine(DAY, time(9, 0)), datetime.combine(DAY, time(9, 30))
    assert _has_conflict(existing, start, end) is True


def test_slot_before_existing_does_not_conflict():
    existing = [_booking(14, 0, 30)]  # afternoon
    start, end = datetime.combine(DAY, time(10, 0)), datetime.combine(DAY, time(10, 30))
    assert _has_conflict(existing, start, end) is False


def test_no_conflict_against_empty_calendar():
    start, end = datetime.combine(DAY, time(10, 0)), datetime.combine(DAY, time(10, 30))
    assert _has_conflict([], start, end) is False


def test_conflict_detected_among_many():
    existing = [_booking(8, 0, 30), _booking(9, 0, 30), _booking(10, 0, 60)]
    start, end = datetime.combine(DAY, time(10, 30)), datetime.combine(DAY, time(11, 0))
    assert _has_conflict(existing, start, end) is True
