from __future__ import annotations


def validate_required(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} e obrigatorio")


def validate_positive_number(value: float, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} deve ser positivo")
