# Contributing to MyProfile

Thanks for your interest in contributing! MyProfile is a standard-library-only
console application, and we aim to keep it dependency-free at runtime.

## Ground Rules

- **No runtime dependencies.** The app must run on a clean Python 3.9+ install.
- **Secure by default.** All user input goes through validators; sensitive fields
  (phone, email, INN, bank accounts) must support masking. Never log or print
  unmasked PII unless the user explicitly requests it.
- **Preserve leading zeros.** Banking identifiers (BIK, accounts) are strings,
  never integers.

## Development Setup

```bash
git clone https://github.com/Voobrazhenie21-lab/code-python-project.git
cd code-python-project

uv sync --extra dev
uv run pytest -v

# or: pip install -e ".[dev]" && pytest -v
```

## Pull Request Checklist

- [ ] `pytest -v` passes locally.
- [ ] New validators/features have test coverage in `tests/`.
- [ ] README updated if user-facing behavior changed.
- [ ] No real personal data, secrets, or credentials in commits (use the demo
      data style already present in `main.py --demo`).
- [ ] Commit messages follow conventional style (`feat:`, `fix:`, `docs:`, `ci:`).

## Ideas for Future Contributions

- Export to PDF/HTML business card.
- Configurable masking policy (what to mask, how many characters to reveal).
- Localization (i18n) support.
