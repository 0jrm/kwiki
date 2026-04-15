"""Retention decay helpers for wiki lifecycle scoring."""

from __future__ import annotations

from datetime import datetime, timezone
from math import exp

RATE_CONSTANTS = {
    "slow": 0.0015,
    "medium": 0.005,
    "fast": 0.02,
}

RATE_ALIASES = {
    "low": "slow",
    "high": "fast",
}


def _normalize_rate(decay_rate: str | None) -> str:
    if not decay_rate:
        return "medium"
    normalized = decay_rate.strip().lower()
    normalized = RATE_ALIASES.get(normalized, normalized)
    if normalized not in RATE_CONSTANTS:
        return "medium"
    return normalized


def _parse_iso8601(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def decayed_confidence(
    base_confidence: float,
    last_confirmed: str | datetime,
    decay_rate: str,
    now: str | datetime | None = None,
) -> float:
    """Compute retention-decayed confidence with compatibility normalization."""
    base = min(1.0, max(0.0, float(base_confidence)))
    rate = _normalize_rate(decay_rate)
    last_dt = _parse_iso8601(last_confirmed)
    now_dt = _parse_iso8601(now) if now is not None else datetime.now(timezone.utc)
    delta_days = max(0.0, (now_dt - last_dt).total_seconds() / 86400.0)
    return base * exp(-RATE_CONSTANTS[rate] * delta_days)
