"""JSON-backed storage for the company list."""

import json

from config import ATS_TYPES, COMPANIES_FILE


def load_companies() -> list[dict]:
    if not COMPANIES_FILE.exists():
        return []
    with open(COMPANIES_FILE) as f:
        return json.load(f)


def save_companies(companies: list[dict]) -> None:
    with open(COMPANIES_FILE, "w") as f:
        json.dump(companies, f, indent=2)
        f.write("\n")


def _normalize(name: str) -> str:
    return " ".join(name.strip().lower().split())


def find_company(companies: list[dict], name: str) -> dict | None:
    target = _normalize(name)
    for company in companies:
        if _normalize(company["name"]) == target:
            return company
    return None


def add_company(name: str, career_url: str = "", ats_type: str = "unknown", active: bool = True) -> tuple[bool, str]:
    """Add a company to the list. Returns (success, message)."""
    ats_type = (ats_type or "unknown").strip().lower()
    if ats_type not in ATS_TYPES:
        return False, f"Unknown ats_type '{ats_type}'. Must be one of: {', '.join(ATS_TYPES)}"

    companies = load_companies()
    if find_company(companies, name):
        return False, f"'{name}' is already in the list (skipped duplicate)"

    companies.append(
        {
            "name": name.strip(),
            "career_url": career_url.strip(),
            "ats_type": ats_type,
            "active": active,
        }
    )
    save_companies(companies)
    return True, f"Added '{name.strip()}'"


def list_companies() -> list[dict]:
    return load_companies()
