"""Ashby public job board JSON API.

Not one of the "big three" ATS platforms by market share, but like
Greenhouse and Lever it exposes a clean, reliable public JSON API, so it
gets the same "no scraping needed" treatment. Use ats_type=ashby for
companies whose career page is hosted at jobs.ashbyhq.com/<org>.
"""

from urllib.parse import urlparse

import requests

from config import REQUEST_TIMEOUT_SECONDS


def _extract_board_token(career_page_url: str) -> str:
    path = urlparse(career_page_url).path
    return path.strip("/").split("/")[-1]


def fetch_jobs(career_page_url: str) -> tuple[list[dict], str, str]:
    """Fetch all listed jobs from an Ashby job board.

    Returns (jobs, status, error_message).
    """
    token = _extract_board_token(career_page_url)
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"

    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    jobs = [
        {
            "job_title": job["title"],
            "job_url": job["jobUrl"],
            "location": job.get("location"),
            "posted_at": job.get("publishedAt"),
        }
        for job in data.get("jobs", [])
        if job.get("isListed", True)
    ]

    if not jobs:
        return jobs, "PARTIAL", "Ashby API returned zero listed jobs"

    return jobs, "OK", ""
