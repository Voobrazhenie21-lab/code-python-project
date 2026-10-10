"""Secure JSON persistence with SHA-256 integrity verification and TXT export."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from .models import EntrepreneurProfile


class IntegrityError(Exception):
    """Raised when the stored JSON profile fails SHA-256 integrity verification."""


def compute_payload_sha256(profile_dict: Dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash over canonical JSON payload."""
    canonical = json.dumps(profile_dict, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def save_profile_json(profile: EntrepreneurProfile, file_path: Path) -> str:
    """Save profile to JSON file along with SHA-256 integrity digest."""
    payload = profile.to_dict()
    digest = compute_payload_sha256(payload)
    envelope = {
        "schema_version": "2.0",
        "sha256_checksum": digest,
        "profile": payload,
    }
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
    return digest


def load_profile_json(file_path: Path, verify_integrity: bool = True) -> EntrepreneurProfile:
    """Load profile from JSON file and verify SHA-256 checksum."""
    raw = json.loads(file_path.read_text(encoding="utf-8"))
    payload = raw.get("profile", raw)
    stored_hash = raw.get("sha256_checksum")

    if verify_integrity and stored_hash:
        actual_hash = compute_payload_sha256(payload)
        if actual_hash != stored_hash:
            raise IntegrityError(
                f"Нарушена целостность файла профиля! Ожидался SHA-256 {stored_hash[:12]}..., "
                f"получен {actual_hash[:12]}..."
            )

    return EntrepreneurProfile.from_dict(payload)


def export_card_txt(profile: EntrepreneurProfile, file_path: Path, mask_pii: bool = False) -> None:
    """Export formatted entrepreneur business card to a UTF-8 TXT file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    content = profile.format_full_card(mask_pii=mask_pii) + "\n"
    file_path.write_text(content, encoding="utf-8")
