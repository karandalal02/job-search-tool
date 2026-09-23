"""Tracks when we first saw each job URL, backed by the database.

Used as a recency fallback for postings whose ATS doesn't expose a real
posted date (Workday, custom career pages): "first time this tool saw it"
stands in for "posted date" so the recency filter still means something.
"""

from datetime import date

from db import SessionLocal
from models import SeenJob


def load_seen() -> dict:
    with SessionLocal() as session:
        rows = session.query(SeenJob).all()
        return {row.job_url: row.first_seen.isoformat() for row in rows}


def save_seen(seen: dict) -> None:
    with SessionLocal() as session:
        existing_urls = {row.job_url for row in session.query(SeenJob.job_url).all()}
        for job_url, first_seen_iso in seen.items():
            if job_url not in existing_urls:
                session.add(SeenJob(job_url=job_url, first_seen=date.fromisoformat(first_seen_iso)))
        session.commit()


def mark_seen(seen: dict, job_url: str) -> str:
    """Record job_url as seen today if new; return its first-seen date (ISO)."""
    if job_url not in seen:
        seen[job_url] = date.today().isoformat()
    return seen[job_url]
