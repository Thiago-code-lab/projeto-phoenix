from __future__ import annotations

from datetime import date, timedelta

from dateutil.relativedelta import relativedelta


def start_of_week(reference: date) -> date:
    return reference - timedelta(days=reference.weekday())


def end_of_week(reference: date) -> date:
    return start_of_week(reference) + timedelta(days=6)


def add_months(reference: date, months: int) -> date:
    return reference + relativedelta(months=months)


def calculate_streak(days: list[date]) -> int:
    ordered = sorted(set(days), reverse=True)
    streak = 0
    current = date.today()
    for day in ordered:
        if day == current or day == current - timedelta(days=1):
            streak += 1
            current = day - timedelta(days=1)
        else:
            break
    return streak
