"""Input sanitization, validation, and PII masking functions for MyProfile v2.0."""

import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def sanitize_phone(raw_phone: str) -> str:
    """Keep only digits and leading/embedded '+' sign."""
    return "".join(ch for ch in raw_phone if ch == "+" or ("0" <= ch <= "9"))


def sanitize_digits(raw_value: str) -> str:
    """Strip all non-numeric characters while preserving leading zeros."""
    return "".join(ch for ch in str(raw_value) if "0" <= ch <= "9")


def format_years_label(age: int) -> str:
    """Return proper Russian declension ('год', 'года', 'лет') for age."""
    if 11 <= age % 100 <= 19:
        return "лет"
    if age % 10 == 1:
        return "год"
    if 2 <= age % 10 <= 4:
        return "года"
    return "лет"


def validate_age(raw_age: str) -> int:
    """Validate age is a non-negative integer within realistic bounds (0..120)."""
    cleaned = raw_age.strip()
    if not cleaned.lstrip("-").isdigit():
        raise ValueError("Возраст должен быть целым числом.")
    val = int(cleaned)
    if val < 0:
        raise ValueError("Возраст не может быть отрицательным.")
    if val > 120:
        raise ValueError("Указан некорректный возраст (максимум 120 лет).")
    return val


def validate_email(raw_email: str) -> str:
    """Validate email format."""
    cleaned = raw_email.strip()
    if not cleaned or not EMAIL_RE.match(cleaned):
        raise ValueError("Некорректный формат электронной почты (пример: user@example.com).")
    return cleaned


def validate_exact_digits(raw_value: str, expected_len: int, field_name: str) -> str:
    """Validate that a banking/tax identifier contains exact number of digits (preserving leading zeros)."""
    digits = sanitize_digits(raw_value)
    if len(digits) != expected_len:
        raise ValueError(f"{field_name} должен содержать ровно {expected_len} цифр.")
    return digits


def validate_ogrnip(raw_value: str) -> str:
    return validate_exact_digits(raw_value, 15, "ОГРНИП")


def validate_inn(raw_value: str) -> str:
    return validate_exact_digits(raw_value, 12, "ИНН ИП")


def validate_bank_account(raw_value: str) -> str:
    return validate_exact_digits(raw_value, 20, "Расчётный счёт (Р/с)")


def validate_bik(raw_value: str) -> str:
    return validate_exact_digits(raw_value, 9, "БИК")


def validate_correspondent_account(raw_value: str) -> str:
    return validate_exact_digits(raw_value, 20, "Корреспондентский счёт (К/с)")


def mask_sensitive(value: str, visible_start: int = 4, visible_end: int = 4) -> str:
    """Mask sensitive PII/financial strings for safe logging or public export."""
    if not value or len(value) <= visible_start + visible_end:
        return "*" * len(value) if value else ""
    masked_len = len(value) - visible_start - visible_end
    return f"{value[:visible_start]}{'*' * masked_len}{value[-visible_end:]}"
