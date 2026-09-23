"""Targeted search: check each company in the list via its own ATS (live
data, exact job links), falling back to a scoped search link when a
company has no known ats_type or its scrape fails."""

import seen_store
import store
from bulk_search import build_company_link
from config import SCRAPE_LOG
from filters import filter_jobs
from scrapers import ashby, custom, greenhouse, lever, workday

ATS_SCRAPERS = {
    "greenhouse": greenhouse.fetch_jobs,
    "lever": lever.fetch_jobs,
    "ashby": ashby.fetch_jobs,
    "workday": workday.fetch_jobs,
    "custom": custom.fetch_jobs,
}


def _log(company_name: str, message: str) -> None:
    from datetime import datetime

    timestamp = datetime.now().isoformat(timespec="seconds")
    with open(SCRAPE_LOG, "a") as f:
        f.write(f"{timestamp}\t{company_name}\t{message}\n")


def _fetch(career_url: str, ats_type: str):
    scraper = ATS_SCRAPERS.get(ats_type)
    if scraper is None:
        return [], "SKIPPED", f"No scraper for ats_type '{ats_type}'"
    try:
        return scraper(career_url)
    except Exception as exc:  # noqa: BLE001 - one company's failure never stops the run
        return [], "FAILED", f"{type(exc).__name__}: {exc}"


def run(title: str = "", location: str = "", recency_days: int | None = None) -> list[dict]:
    """Returns one row per active company:
    {"company", "status", "matched_jobs": [...], "search_link", "note"}
    """
    companies = store.load_companies()
    seen = seen_store.load_seen()

    rows = []
    for company in companies:
        if not company.get("active", True):
            continue

        name = company["name"]
        career_url = company.get("career_url", "")
        ats_type = company.get("ats_type", "unknown")
        search_link = build_company_link(name, title, location, recency="all")

        if ats_type == "unknown" or not career_url:
            rows.append(
                {
                    "company": name,
                    "status": "NO_ATS_SET",
                    "matched_jobs": [],
                    "search_link": search_link,
                    "note": "No career_url/ats_type set -- use the search link",
                }
            )
            continue

        jobs, status, error = _fetch(career_url, ats_type)
        if status in ("FAILED", "PARTIAL"):
            _log(name, f"{status} - {error}")

        matched = filter_jobs(jobs, title, location, recency_days, seen, seen_store)

        rows.append(
            {
                "company": name,
                "status": status,
                "matched_jobs": matched,
                "search_link": search_link,
                "note": error,
            }
        )

    seen_store.save_seen(seen)
    return rows
