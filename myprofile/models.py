"""Object-Oriented Data Models for MyProfile v2.0."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict

from .validators import format_years_label, mask_sensitive

SEPARATOR = "------------------------------------------"


@dataclass
class PersonalInfo:
    """Stores personal and contact information of the entrepreneur."""

    name: str = ""
    age: int = 0
    phone: str = ""
    email: str = ""
    postal_code: str = ""
    address: str = ""
    additional_information: str = ""

    def format_card(self, mask_pii: bool = False) -> str:
        phone_out = mask_sensitive(self.phone, 4, 2) if mask_pii and self.phone else self.phone
        lines = [
            SEPARATOR,
            f"Имя:     {self.name}",
            f"Возраст: {self.age} {format_years_label(self.age)}",
            f"Телефон: {phone_out}",
            f"E-mail:  {self.email}",
            f"Индекс:  {self.postal_code}",
            f"Адрес:   {self.address}",
        ]
        if self.additional_information:
            lines.extend(["", "Дополнительная информация:", self.additional_information])
        return "\n".join(lines)


@dataclass
class EntrepreneurRequisites:
    """Stores tax and banking requisites (preserving leading zeros as strings)."""

    ogrnip: str = ""
    inn: str = ""
    bank_account: str = ""
    bank_name: str = ""
    bik: str = ""
    correspondent_account: str = ""

    def format_card(self, mask_pii: bool = False) -> str:
        rs_out = (
            mask_sensitive(self.bank_account, 5, 4)
            if mask_pii and self.bank_account
            else self.bank_account
        )
        inn_out = mask_sensitive(self.inn, 4, 2) if mask_pii and self.inn else self.inn
        lines = [
            "",
            "Информация о предпринимателе",
            f"ОГРНИП: {self.ogrnip}",
            f"ИНН:    {inn_out}",
            "Банковские реквизиты",
            f"Р/с:    {rs_out}",
            f"Банк:   {self.bank_name}",
            f"БИК:    {self.bik}",
            f"К/с:    {self.correspondent_account}",
        ]
        return "\n".join(lines)


@dataclass
class EntrepreneurProfile:
    """Aggregate root combining personal info and entrepreneur banking requisites."""

    personal: PersonalInfo = field(default_factory=PersonalInfo)
    requisites: EntrepreneurRequisites = field(default_factory=EntrepreneurRequisites)

    def format_full_card(self, mask_pii: bool = False) -> str:
        return f"{self.personal.format_card(mask_pii=mask_pii)}\n{self.requisites.format_card(mask_pii=mask_pii)}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntrepreneurProfile":
        personal_data = data.get("personal", {})
        req_data = data.get("requisites", {})
        return cls(
            personal=PersonalInfo(**personal_data),
            requisites=EntrepreneurRequisites(**req_data),
        )
