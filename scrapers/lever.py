"""Lever public job postings JSON API."""

from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from config import REQUEST_TIMEOUT_SECONDS


def _extract_company_token(career_page_url: str) -> str:
    path = urlparse(career_page_url).path
    return path.strip("/").split("/")[-1]


def _to_iso(epoch_ms) -> str | None:
    if not epoch_ms:
        return None
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).date().isoformat()


def fetch_jobs(career_page_url: str) -> tuple[list[dict], str, str]:
    """Fetch all open jobs from a Lever postings board.

    Returns (jobs, status, error_message).
    """
    token = _extract_company_token(career_page_url)
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"

    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    jobs = [
        {
            "job_title": posting["text"],
            "job_url": posting["hostedUrl"],
            "location": (posting.get("categories") or {}).get("location"),
            "posted_at": _to_iso(posting.get("createdAt")),
        }
        for posting in data
    ]

    if not jobs:
        return jobs, "PARTIAL", "Lever API returned zero jobs"

    return jobs, "OK", ""
