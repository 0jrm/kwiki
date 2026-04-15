from datetime import datetime, timezone
from math import exp, isclose

from decay import RATE_CONSTANTS, decayed_confidence


def test_slow_rate_path():
    now = datetime(2026, 4, 15, tzinfo=timezone.utc)
    last = datetime(2026, 4, 5, tzinfo=timezone.utc)
    expected = 0.8 * exp(-RATE_CONSTANTS["slow"] * 10)
    actual = decayed_confidence(0.8, last, "slow", now=now)
    assert isclose(actual, expected, rel_tol=1e-9)


def test_medium_rate_path():
    now = "2026-04-15T00:00:00Z"
    last = "2026-04-05T00:00:00Z"
    expected = 0.8 * exp(-RATE_CONSTANTS["medium"] * 10)
    actual = decayed_confidence(0.8, last, "medium", now=now)
    assert isclose(actual, expected, rel_tol=1e-9)


def test_fast_rate_path():
    now = "2026-04-15T00:00:00Z"
    last = "2026-04-05T00:00:00Z"
    expected = 0.8 * exp(-RATE_CONSTANTS["fast"] * 10)
    actual = decayed_confidence(0.8, last, "fast", now=now)
    assert isclose(actual, expected, rel_tol=1e-9)


def test_compatibility_normalization_low_and_high():
    now = "2026-04-15T00:00:00Z"
    last = "2026-04-05T00:00:00Z"
    low_rate = decayed_confidence(0.7, last, "low", now=now)
    slow_rate = decayed_confidence(0.7, last, "slow", now=now)
    high_rate = decayed_confidence(0.7, last, "high", now=now)
    fast_rate = decayed_confidence(0.7, last, "fast", now=now)
    assert isclose(low_rate, slow_rate, rel_tol=1e-12)
    assert isclose(high_rate, fast_rate, rel_tol=1e-12)


def test_today_no_decay():
    now = "2026-04-15T00:00:00Z"
    actual = decayed_confidence(0.63, now, "medium", now=now)
    assert isclose(actual, 0.63, rel_tol=1e-12)


def test_very_old_date_near_zero():
    now = "2026-04-15T00:00:00Z"
    last = "2000-01-01T00:00:00Z"
    actual = decayed_confidence(1.0, last, "fast", now=now)
    assert actual < 0.00001


def test_deterministic_now_injection_and_guards():
    now = "2026-04-15T00:00:00Z"
    # future last_confirmed clamps day delta to 0; confidence clamps to 1.0
    actual = decayed_confidence(2.5, "2026-05-01T00:00:00Z", "unknown", now=now)
    assert isclose(actual, 1.0, rel_tol=1e-12)
