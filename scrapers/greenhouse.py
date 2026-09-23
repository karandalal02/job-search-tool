"""Greenhouse public job board JSON API."""

from urllib.parse import urlparse

import requests

from config import REQUEST_TIMEOUT_SECONDS


def _extract_board_token(career_page_url: str) -> str:
    path = urlparse(career_page_url).path
    return path.strip("/").split("/")[-1]


def fetch_jobs(career_page_url: str) -> tuple[list[dict], str, str]:
    """Fetch all open jobs from a Greenhouse board.

    Returns (jobs, status, error_message) where jobs is a list of
    {"job_title", "job_url", "location", "posted_at"} dicts and status
    is OK/PARTIAL/FAILED.
    """
    token = _extract_board_token(career_page_url)
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"

    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    jobs = [
        {
            "job_title": job["title"],
            "job_url": job["absolute_url"],
            "location": (job.get("location") or {}).get("name"),
            "posted_at": job.get("updated_at"),
        }
        for job in data.get("jobs", [])
    ]

    if not jobs:
        return jobs, "PARTIAL", "Greenhouse API returned zero jobs"

    return jobs, "OK", ""
