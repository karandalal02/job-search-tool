"""Company list storage, backed by the database (see db.py / models.py)."""

from config import ATS_TYPES
from db import SessionLocal
from models import Company


def _normalize(name: str) -> str:
    return " ".join(name.strip().lower().split())


def add_company(name: str, career_url: str = "", ats_type: str = "unknown", active: bool = True) -> tuple[bool, str]:
    """Add a company to the list. Returns (success, message)."""
    ats_type = (ats_type or "unknown").strip().lower()
    if ats_type not in ATS_TYPES:
        return False, f"Unknown ats_type '{ats_type}'. Must be one of: {', '.join(ATS_TYPES)}"

    with SessionLocal() as session:
        existing = session.query(Company).all()
        if any(_normalize(c.name) == _normalize(name) for c in existing):
            return False, f"'{name}' is already in the list (skipped duplicate)"

        session.add(Company(name=name.strip(), career_url=career_url.strip(), ats_type=ats_type, active=active))
        session.commit()
        return True, f"Added '{name.strip()}'"


def list_companies() -> list[dict]:
    with SessionLocal() as session:
        companies = session.query(Company).order_by(Company.name).all()
        return [
            {"id": c.id, "name": c.name, "career_url": c.career_url, "ats_type": c.ats_type, "active": c.active}
            for c in companies
        ]


def load_companies() -> list[dict]:
    return list_companies()


def delete_company(company_id: int) -> bool:
    with SessionLocal() as session:
        company = session.get(Company, company_id)
        if not company:
            return False
        session.delete(company)
        session.commit()
        return True


def set_active(company_id: int, active: bool) -> bool:
    with SessionLocal() as session:
        company = session.get(Company, company_id)
        if not company:
            return False
        company.active = active
        session.commit()
        return True
