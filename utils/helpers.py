from __future__ import annotations

from datetime import date, timedelta


def last_n_days(days: int) -> list[date]:
    today = date.today()
    return [today - timedelta(days=offset) for offset in range(days - 1, -1, -1)]


def safe_float(value: str | float | int, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
