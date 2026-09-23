"""JSON-backed tracker of when we first saw each job URL.

Used as a recency fallback for postings whose ATS doesn't expose a real
posted date (Workday, custom career pages): "first time this tool saw it"
stands in for "posted date" so the recency filter still means something.
"""

import json
from datetime import date

from config import SEEN_JOBS_FILE


def load_seen() -> dict:
    if not SEEN_JOBS_FILE.exists():
        return {}
    with open(SEEN_JOBS_FILE) as f:
        return json.load(f)


def save_seen(seen: dict) -> None:
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(seen, f, indent=2)
        f.write("\n")


def mark_seen(seen: dict, job_url: str) -> str:
    """Record job_url as seen today if new; return its first-seen date (ISO)."""
    if job_url not in seen:
        seen[job_url] = date.today().isoformat()
    return seen[job_url]
