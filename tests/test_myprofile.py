"""Automated Pytest suite for MyProfile v2.0."""

from pathlib import Path
import pytest

from myprofile.models import EntrepreneurProfile
from myprofile.storage import IntegrityError, load_profile_json, save_profile_json
from myprofile.validators import (
    format_years_label,
    mask_sensitive,
    sanitize_phone,
    validate_age,
    validate_bank_account,
    validate_bik,
    validate_correspondent_account,
    validate_email,
    validate_inn,
    validate_ogrnip,
)


def test_age_validation_and_declension() -> None:
    assert validate_age("21") == 21
    assert format_years_label(21) == "год"
    assert format_years_label(24) == "года"
    assert format_years_label(14) == "лет"
    assert format_years_label(30) == "лет"

    with pytest.raises(ValueError):
        validate_age("-5")
    with pytest.raises(ValueError):
        validate_age("abc")


def test_preserves_leading_zeros_in_bik_and_requisites() -> None:
    # Critical bug in v1.0: int('044525225') dropped leading zero
    assert validate_bik("044525225") == "044525225"
    assert validate_ogrnip("323774600123456") == "323774600123456"
    assert validate_inn("770123456789") == "770123456789"
    assert validate_bank_account("40802810000000000001") == "40802810000000000001"
    assert validate_correspondent_account("30101810400000000225") == "30101810400000000225"


def test_phone_and_email_sanitization() -> None:
    assert sanitize_phone("+7 (999) 123-45-67") == "+79991234567"
    assert validate_email("ivan@example.com") == "ivan@example.com"
    with pytest.raises(ValueError):
        validate_email("not-an-email")


def test_json_persistence_and_sha256_integrity_check(tmp_path: Path) -> None:
    profile = EntrepreneurProfile()
    profile.personal.name = "Иван Иванов"
    profile.personal.age = 32
    profile.requisites.bik = "044525225"
    profile.requisites.bank_account = "40802810000000000001"

    json_file = tmp_path / "profile.json"
    digest = save_profile_json(profile, json_file)
    assert len(digest) == 64

    loaded = load_profile_json(json_file, verify_integrity=True)
    assert loaded.personal.name == "Иван Иванов"
    assert loaded.requisites.bik == "044525225"

    # Simulate unauthorized file tampering on disk (FIM violation)
    tampered = json_file.read_text(encoding="utf-8").replace("Иван Иванов", "Злоумышленник")
    json_file.write_text(tampered, encoding="utf-8")

    with pytest.raises(IntegrityError):
        load_profile_json(json_file, verify_integrity=True)


def test_pii_masking() -> None:
    masked = mask_sensitive("40802810000000000001", 5, 4)
    assert masked == "40802***********0001"
