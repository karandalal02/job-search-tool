"""Generic requests + BeautifulSoup scraper for custom career pages.

Looks for anchor tags whose href or surrounding context suggests a job
posting link, using the link text as the job title. This is a heuristic
and will not work for every site (especially JS-rendered pages) -- that's
expected; the caller should fall back to the generated search link when
this comes back FAILED or PARTIAL.
"""

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT_SECONDS

JOB_LINK_PATTERN = re.compile(r"(job|career|position|posting|vacanc|opening|detail)", re.I)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobSearchTool/1.0)"}


def fetch_jobs(career_page_url: str) -> tuple[list[dict], str, str]:
    """Scrape a custom career page for job links.

    Returns (jobs, status, error_message) where status is OK/PARTIAL/FAILED.
    No location/posted_at data is available from this heuristic scrape.
    """
    response = requests.get(career_page_url, timeout=REQUEST_TIMEOUT_SECONDS, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    seen_urls = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        title = link.get_text(strip=True)

        if not title or len(title) < 4:
            continue
        if not JOB_LINK_PATTERN.search(href):
            continue

        full_url = urljoin(career_page_url, href)
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)
        jobs.append({"job_title": title, "job_url": full_url, "location": None, "posted_at": None})

    if not jobs:
        return [], "FAILED", "No job listings found on page (page may require JavaScript to render)"

    if len(jobs) < 3:
        return (
            jobs,
            "PARTIAL",
            f"Only found {len(jobs)} job listing(s) on page; results may be incomplete "
            "(page may use JavaScript rendering or pagination)",
        )

    return jobs, "OK", ""
