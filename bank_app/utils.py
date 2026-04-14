from __future__ import annotations

from .exceptions import ValidationError


def normalize_account_number(raw_value: object) -> str:
    value = str(raw_value).strip()
    if not value:
        raise ValidationError("Account number is required.")
    if not value.isdigit():
        raise ValidationError("Account number must contain only digits.")
    if len(value) < 6:
        raise ValidationError("Account number must be at least 6 digits.")
    return value


def parse_amount(raw_value: object, field_name: str = "Amount") -> float:
    try:
        amount = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc

    if amount <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")
    return round(amount, 2)
