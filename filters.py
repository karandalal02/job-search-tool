"""Title / recency / location filtering shared by bulk and targeted search."""

from datetime import date, datetime


def match_title(title: str, title_filter: str) -> bool:
    """Case-insensitive substring match. Seniority is just part of the title
    you search for (e.g. "Senior Product Manager"), no separate filter."""
    if not title_filter:
        return True
    if not title:
        return False
    return title_filter.strip().lower() in title.lower()


def match_location(location: str | None, location_filter: str) -> bool:
    """Case-insensitive substring match. If the job has no location data
    (common for custom-scraped pages), we can't rule it out, so it passes --
    better a false positive you dismiss than a real posting silently dropped."""
    if not location_filter:
        return True
    if not location:
        return True
    return location_filter.strip().lower() in location.lower()


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def match_recency(posted_at: str | None, recency_days: int | None, fallback_first_seen: str) -> bool:
    """True if the posting is within recency_days. Uses posted_at when the
    ATS provides it, otherwise falls back to when this tool first saw the
    job (see seen_store.py)."""
    if recency_days is None:
        return True

    effective = _parse_date(posted_at) or _parse_date(fallback_first_seen)
    if effective is None:
        return True

    age_days = (date.today() - effective).days
    return age_days <= recency_days


def filter_jobs(jobs: list[dict], title_filter: str, location_filter: str, recency_days, seen: dict, seen_store) -> list[dict]:
    """Apply title match first (defines the relevant set), then record each
    matching job's first-seen date, then apply location/recency."""
    matched = []
    for job in jobs:
        if not match_title(job.get("job_title", ""), title_filter):
            continue

        first_seen = seen_store.mark_seen(seen, job["job_url"])

        if not match_location(job.get("location"), location_filter):
            continue
        if not match_recency(job.get("posted_at"), recency_days, first_seen):
            continue

        matched.append(job)

    return matched
