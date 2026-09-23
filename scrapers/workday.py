"""Best-effort scraper for Workday-hosted career sites.

Workday career sites are React apps backed by a "CXS" JSON API at
https://{tenant}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs
but the {site} name varies per company and isn't reliably derivable from
the public career page URL. This module makes a best-effort guess and
falls back to FAILED -- Workday is high-risk by nature; when it fails,
the caller should fall back to the generated search link instead.
"""

import re
from urllib.parse import urlparse

import requests

from config import REQUEST_TIMEOUT_SECONDS

LOCALE_PATTERN = re.compile(r"^[a-z]{2}-[A-Z]{2}$")


def _candidate_sites(tenant: str, path_segments: list[str]) -> list[str]:
    candidates = [seg for seg in path_segments if seg and not LOCALE_PATTERN.match(seg)]
    for fallback in ("External", "Careers", "External_Career_Site", tenant.capitalize()):
        if fallback not in candidates:
            candidates.append(fallback)
    return candidates


def fetch_jobs(career_page_url: str, search_text: str = "") -> tuple[list[dict], str, str]:
    """Attempt to fetch jobs from a Workday CXS API.

    Returns (jobs, status, error_message). Often returns FAILED unless the
    {site} guess happens to be correct -- expected and handled upstream.
    """
    parsed = urlparse(career_page_url)
    host = parsed.netloc
    tenant = host.split(".")[0]
    path_segments = [p for p in parsed.path.strip("/").split("/") if p]

    tried = []
    for site in _candidate_sites(tenant, path_segments):
        api_url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
        tried.append(api_url)
        try:
            response = requests.post(
                api_url,
                json={"limit": 20, "offset": 0, "searchText": search_text},
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException:
            continue

        if response.status_code != 200:
            continue

        try:
            data = response.json()
        except ValueError:
            continue

        postings = data.get("jobPostings")
        if postings is None:
            continue

        prefix = f"https://{host}/{'/'.join(path_segments[:1]) or 'en-US'}/{site}"
        jobs = [
            {
                "job_title": posting.get("title", ""),
                "job_url": prefix + posting.get("externalPath", ""),
                "location": posting.get("locationsText"),
                "posted_at": None,
            }
            for posting in postings
        ]

        if not jobs:
            return jobs, "PARTIAL", f"Workday API at {api_url} returned zero postings"
        return jobs, "OK", ""

    return (
        [],
        "FAILED",
        f"Could not locate Workday job search API for tenant '{tenant}' "
        f"(tried: {', '.join(tried)}); use the search link instead",
    )
