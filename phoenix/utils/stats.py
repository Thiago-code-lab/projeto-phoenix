from __future__ import annotations

from statistics import mean


def average(values: list[float]) -> float:
    return mean(values) if values else 0.0


def trend(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return values[-1] - values[0]


def completion_rate(completed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return completed / total
