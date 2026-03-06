from __future__ import annotations

from datetime import date, datetime


def format_currency(value: float, currency: str = "BRL") -> str:
    symbol = "R$" if currency == "BRL" else currency
    return f"{symbol} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date(value: date | datetime | None) -> str:
    if value is None:
        return ""
    return value.strftime("%d/%m/%Y")


def truncate_text(text: str, limit: int = 80) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."
