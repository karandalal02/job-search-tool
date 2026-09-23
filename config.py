"""Shared configuration: file paths and request settings."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

COMPANIES_FILE = DATA_DIR / "companies.json"
SEEN_JOBS_FILE = DATA_DIR / "seen_jobs.json"
SCRAPE_LOG = DATA_DIR / "scrape_log.txt"

REQUEST_TIMEOUT_SECONDS = 10

ATS_TYPES = ("greenhouse", "lever", "ashby", "workday", "custom", "unknown")
