"""Bulk search: pre-built Google `site:` search links across ATS platforms,
the same trick briansjobsearch.com uses. You open these in a browser and
look at the results yourself -- no scraping, no API key.
"""

from urllib.parse import quote_plus

# name -> (site query fragment, extra exclusion terms)
ATS_PLATFORMS = {
    "Greenhouse": ("site:greenhouse.io OR site:job-boards.greenhouse.io", ""),
    "Lever": ("site:lever.co", "-jobgether"),
    "Ashby": ("site:jobs.ashbyhq.com", ""),
    "Workday": ("site:myworkdayjobs.com", ""),
    "Workable": ("site:workable.com", ""),
    "BreezyHR": ("site:breezy.hr", ""),
    "iCIMS": ("site:icims.com", ""),
    "Jobvite": ("site:jobvite.com", ""),
    "SmartRecruiters": ("site:smartrecruiters.com", ""),
    "Recruitee": ("site:recruitee.com", ""),
    "JazzHR": ("site:jazz.co", ""),
    "Teamtailor": ("site:teamtailor.com", ""),
    "Personio": ("site:personio.de OR site:personio.com", ""),
    "Jobs Subdomain": ("site:jobs.*", ""),
    "Careers Pages": ("(site:careers.* OR site:*/careers/* OR site:*/career/*)", ""),
    "LinkedIn": ("site:linkedin.com/jobs", ""),
}

# recency label -> Google's tbs date-range param
RECENCY_TBS = {
    "hour": "qdr:h",
    "day": "qdr:d",
    "week": "qdr:w",
    "month": "qdr:m",
    "all": None,
}


def _build_url(title: str, location: str, site_fragment: str, exclusions: str, recency: str) -> str:
    terms = [f'"{title}"'] if title else []
    terms.append(site_fragment)
    if location:
        terms.append(location)
    if exclusions:
        terms.append(exclusions)

    query = " ".join(terms)
    url = f"https://www.google.com/search?q={quote_plus(query)}"

    tbs = RECENCY_TBS.get((recency or "all").lower())
    if tbs:
        url += f"&tbs={tbs}"

    return url


def build_links(title: str, location: str = "", recency: str = "all") -> list[dict]:
    """Returns a list of {"platform", "url"} dicts, one per ATS platform."""
    if recency.lower() not in RECENCY_TBS:
        raise ValueError(f"recency must be one of: {', '.join(RECENCY_TBS)}")

    return [
        {"platform": platform, "url": _build_url(title, location, site_fragment, exclusions, recency)}
        for platform, (site_fragment, exclusions) in ATS_PLATFORMS.items()
    ]


def build_company_link(company_name: str, title: str, location: str = "", recency: str = "all") -> str:
    """A single search link scoped to one company -- used as the fallback
    'check yourself' link in targeted search when live scraping fails or
    a company has no known ats_type."""
    terms = [f'"{title}"'] if title else []
    terms.append(f'"{company_name}"')
    terms.append("jobs")
    if location:
        terms.append(location)

    query = " ".join(terms)
    url = f"https://www.google.com/search?q={quote_plus(query)}"

    tbs = RECENCY_TBS.get((recency or "all").lower())
    if tbs:
        url += f"&tbs={tbs}"

    return url
