# Job Search Tool

Two ways to search, available as both a CLI and a web UI:

1. **Bulk search** -- filter-driven. Generates pre-built Google `site:`
   search links across ATS platforms (Greenhouse, Lever, Ashby, Workday,
   etc.), scoped by job title, location, and recency. You open the links
   yourself and look at results, same idea as briansjobsearch.com.

2. **Targeted search** -- company-list driven. You maintain a list of
   companies you actually care about. For each one on Greenhouse, Lever,
   or Ashby, the tool calls that platform's public JSON API directly and
   returns exact, live job links -- no clicking required. Workday gets a
   best-effort attempt at its internal API. Custom career pages get a
   heuristic scrape. Whenever a company can't be resolved automatically
   (unknown ATS, failed scrape), you still get a scoped search link as a
   fallback so nothing is a dead end.

Data (company list + recency tracking) lives in a database via SQLAlchemy
-- Postgres in production (`DATABASE_URL`), local SQLite by default.

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Optionally copy `.env.example` to `.env` to set `DATABASE_URL` /
`WEB_UI_PASSWORD` / `FLASK_SECRET_KEY` locally. With no `.env`, it uses a
local SQLite file (`data/app.db`) and no login gate.

## Web UI

```bash
python3 app.py
```

Opens at `http://localhost:5050` -- Companies / Bulk Search / Targeted
Search pages.

## CLI

**Add a company to the targeted list:**

```bash
python3 cli.py add-company --name Acme --url https://boards.greenhouse.io/acme --ats greenhouse
```

`--ats` is one of `greenhouse`, `lever`, `ashby`, `workday`, `custom`, or
`unknown` (default). If you don't know a company's ATS yet, add it with
just a name -- it'll still show up in targeted search results with a
fallback search link.

**View the company list** (also how you check for duplicates before adding):

```bash
python3 cli.py list-companies
```

**Bulk search:**

```bash
python3 cli.py bulk --title "Product Manager" --recency day --location remote
```

**Targeted search** (live results across your company list):

```bash
python3 cli.py targeted --title "Product Manager" --location remote --recency-days 3
```

## How filters work

- **Title** -- case-insensitive substring match against the job title.
  Seniority is just part of what you type (e.g. `"Senior Product Manager"`),
  there's no separate seniority filter.
- **Location** -- case-insensitive substring match against the posting's
  location field. If a posting has no location data (common for
  custom-scraped pages), it's included rather than silently dropped.
- **Recency** -- for platforms that expose a real posted/updated date
  (Greenhouse, Lever, Ashby), filters against that. For platforms that
  don't (Workday, custom pages), falls back to "days since this tool
  first saw the posting" (tracked in the `seen_jobs` table).

## Deploying (Render + Neon)

1. **Database** -- create a free Postgres instance at
   [neon.tech](https://neon.tech), copy its connection string.
2. **Web service** -- create a new Web Service on
   [render.com](https://render.com) pointing at this repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Environment variables:
     - `DATABASE_URL` -- the Neon connection string
     - `WEB_UI_PASSWORD` -- a password of your choice (required for a
       public deployment -- without it, anyone with the URL can add
       companies or trigger outbound scrape requests)
     - `FLASK_SECRET_KEY` -- a random string, e.g. generate with
       `python3 -c "import secrets; print(secrets.token_hex(32))"`

## Files

- `db.py` / `models.py` -- SQLAlchemy engine + Company/SeenJob models
- `store.py` -- company list CRUD
- `seen_store.py` -- first-seen tracker for recency fallback
- `filters.py` -- title/location/recency matching
- `bulk_search.py` -- Google `site:` link generator (bulk mode + per-company fallback links)
- `targeted_search.py` -- orchestrates live scraping across the company list
- `scrapers/` -- one module per ATS type
- `cli.py` -- command-line entry point
- `app.py` / `templates/` -- Flask web UI
