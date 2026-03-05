from __future__ import annotations

from datetime import date, datetime


def format_currency(value: float, currency: str = "R$") -> str:
    return f"{currency} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def greeting_by_hour(now: datetime | None = None) -> str:
    current = now or datetime.now()
    hour = current.hour
    if hour < 12:
        return "Bom dia"
    if hour < 18:
        return "Boa tarde"
    return "Boa noite"
