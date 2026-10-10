#!/usr/bin/env python3
"""Interactive CLI and Demo Runner for MyProfile v2.0."""

import sys
from pathlib import Path
from typing import Callable

from myprofile.models import SEPARATOR, EntrepreneurProfile
from myprofile.storage import (
    IntegrityError,
    export_card_txt,
    load_profile_json,
    save_profile_json,
)
from myprofile.validators import (
    sanitize_digits,
    sanitize_phone,
    validate_age,
    validate_bank_account,
    validate_bik,
    validate_correspondent_account,
    validate_email,
    validate_inn,
    validate_ogrnip,
)

DEFAULT_JSON_PATH = Path("profile_data.json")
DEFAULT_TXT_PATH = Path("business_card.txt")


def prompt_validated(prompt_text: str, validator: Callable[[str], object]):
    """Repeatedly prompt user until validator succeeds without raising ValueError."""
    while True:
        raw = input(prompt_text)
        try:
            return validator(raw)
        except ValueError as exc:
            print(f"[!] Ошибка валидации: {exc}")


def run_demo() -> int:
    """Run automated non-interactive demonstration of MyProfile v2.0 features."""
    profile = EntrepreneurProfile()
    profile.personal.name = "Алексей Жарков"
    profile.personal.age = validate_age("27")
    profile.personal.phone = sanitize_phone("+375 (29) 554-80-55")
    profile.personal.email = validate_email("lyosha.zharkov.98@mail.ru")
    profile.personal.postal_code = sanitize_digits("220000")
    profile.personal.address = "г. Минск, пр-т Независимости, д. 1"
    profile.personal.additional_information = "Специалист по ИБ (Blue Team / Pentest / DevSecOps)"

    profile.requisites.ogrnip = validate_ogrnip("323774600123456")
    profile.requisites.inn = validate_inn("770123456789")
    profile.requisites.bank_account = validate_bank_account("40802810000000000001")
    profile.requisites.bank_name = "ПАО Сбербанк"
    profile.requisites.bik = validate_bik("044525225")
    profile.requisites.correspondent_account = validate_correspondent_account(
        "30101810400000000225"
    )

    print("=== [DEMO] Полная карточка предпринимателя ===")
    print(profile.format_full_card(mask_pii=False))
    print("\n=== [DEMO] Карточка с маскированием ПДн и счетов (--mask-pii) ===")
    print(profile.format_full_card(mask_pii=True))
    return 0


def run_interactive() -> int:
    """Run interactive console menu."""
    profile = EntrepreneurProfile()
    print("Приложение MyProfile для предпринимателей (v2.0 Secure OOP Edition)")
    print("Сохраняй информацию о себе, проверяй целостность данных и экспортируй визитку")

    while True:
        print(SEPARATOR)
        print("ГЛАВНОЕ МЕНЮ")
        print("1 - Ввести или обновить информацию")
        print("2 - Вывести информацию")
        print("3 - Сохранить / загрузить профиль (JSON + SHA-256)")
        print("4 - Экспортировать карточку в TXT")
        print("0 - Завершить работу")

        raw_opt = input("Введите номер пункта меню: ").strip()
        if raw_opt == "0":
            break

        if raw_opt == "1":
            while True:
                print(SEPARATOR)
                print("ВВЕСТИ ИЛИ ОБНОВИТЬ ИНФОРМАЦИЮ")
                print("1 - Личная информация")
                print("2 - Информация о предпринимателе")
                print("0 - Назад")

                sub = input("Введите номер пункта меню: ").strip()
                if sub == "0":
                    break
                if sub == "1":
                    profile.personal.name = input("Введите имя: ").strip()
                    profile.personal.age = int(
                        prompt_validated("Введите возраст: ", validate_age)
                    )
                    profile.personal.phone = sanitize_phone(
                        input("Введите номер телефона (+7ХХХХХХХХХХ): ")
                    )
                    profile.personal.email = str(
                        prompt_validated("Введите адрес электронной почты: ", validate_email)
                    )
                    profile.personal.postal_code = sanitize_digits(
                        input("Введите почтовый индекс: ")
                    )
                    profile.personal.address = input(
                        "Введите почтовый адрес (без индекса): "
                    ).strip()
                    profile.personal.additional_information = input(
                        "Введите дополнительную информацию:\n"
                    ).strip()
                elif sub == "2":
                    profile.requisites.ogrnip = str(
                        prompt_validated("Введите ОГРНИП (15 цифр): ", validate_ogrnip)
                    )
                    profile.requisites.inn = str(
                        prompt_validated("Введите ИНН ИП (12 цифр): ", validate_inn)
                    )
                    profile.requisites.bank_account = str(
                        prompt_validated(
                            "Введите расчётный счёт (20 цифр): ", validate_bank_account
                        )
                    )
                    profile.requisites.bank_name = input("Введите название банка: ").strip()
                    profile.requisites.bik = str(
                        prompt_validated("Введите БИК (9 цифр): ", validate_bik)
                    )
                    profile.requisites.correspondent_account = str(
                        prompt_validated(
                            "Введите корреспондентский счёт (20 цифр): ",
                            validate_correspondent_account,
                        )
                    )
                else:
                    print("Введите корректный пункт меню")

        elif raw_opt == "2":
            while True:
                print(SEPARATOR)
                print("ВЫВЕСТИ ИНФОРМАЦИЮ")
                print("1 - Личная информация")
                print("2 - Вся информация (полная)")
                print("3 - Вся информация (с маскированием ПДн / счетов)")
                print("0 - Назад")

                sub = input("Введите номер пункта меню: ").strip()
                if sub == "0":
                    break
                if sub == "1":
                    print(profile.personal.format_card(mask_pii=False))
                elif sub == "2":
                    print(profile.format_full_card(mask_pii=False))
                elif sub == "3":
                    print(profile.format_full_card(mask_pii=True))
                else:
                    print("Введите корректный пункт меню")

        elif raw_opt == "3":
            print(SEPARATOR)
            print("1 - Сохранить профиль в JSON (с SHA-256 контрольной суммой)")
            print("2 - Загрузить профиль из JSON (с проверкой целостности)")
            sub = input("Выберите действие: ").strip()
            if sub == "1":
                digest = save_profile_json(profile, DEFAULT_JSON_PATH)
                print(f"[+] Профиль сохранён в {DEFAULT_JSON_PATH} (SHA-256: {digest[:16]}...)")
            elif sub == "2":
                if not DEFAULT_JSON_PATH.exists():
                    print(f"[!] Файл {DEFAULT_JSON_PATH} не найден.")
                else:
                    try:
                        profile = load_profile_json(DEFAULT_JSON_PATH, verify_integrity=True)
                        print("[+] Профиль успешно загружен, целостность SHA-256 подтверждена.")
                    except IntegrityError as exc:
                        print(f"[!] КРИТИЧЕСКАЯ ОШИБКА БЕЗОПАСНОСТИ: {exc}")

        elif raw_opt == "4":
            mask_choice = input("Маскировать реквизиты и ПДн при экспорте? (y/n): ").strip().lower()
            export_card_txt(profile, DEFAULT_TXT_PATH, mask_pii=(mask_choice == "y"))
            print(f"[+] Визитка экспортирована в {DEFAULT_TXT_PATH}")
        else:
            print("Введите корректный пункт меню")

    return 0


def main() -> int:
    if "--demo" in sys.argv:
        return run_demo()
    return run_interactive()


if __name__ == "__main__":
    sys.exit(main())
