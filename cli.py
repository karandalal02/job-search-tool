"""Command-line entry point.

    python3 cli.py add-company --name Acme --url https://boards.greenhouse.io/acme --ats greenhouse
    python3 cli.py list-companies
    python3 cli.py bulk --title "Product Manager" --recency day --location remote
    python3 cli.py targeted --title "Product Manager" --recency-days 1 --location remote
"""

import argparse

import bulk_search
import store
import targeted_search
from db import init_db


def cmd_add_company(args):
    ok, message = store.add_company(args.name, args.url or "", args.ats, active=not args.inactive)
    print(message)


def cmd_list_companies(args):
    companies = store.list_companies()
    if not companies:
        print("No companies yet. Add one with: python3 cli.py add-company --name ...")
        return

    for c in companies:
        state = "active" if c.get("active", True) else "inactive"
        print(f"- {c['name']}  [{c.get('ats_type', 'unknown')}, {state}]  {c.get('career_url', '')}")


def cmd_bulk(args):
    links = bulk_search.build_links(args.title, args.location or "", args.recency)
    print(f"{'Platform':<20} Link")
    print("-" * 100)
    for row in links:
        print(f"{row['platform']:<20} {row['url']}")


def cmd_targeted(args):
    rows = targeted_search.run(args.title, args.location or "", args.recency_days)

    for row in rows:
        print(f"\n{row['company']}  [{row['status']}]")
        if row["matched_jobs"]:
            for job in row["matched_jobs"]:
                loc = f"  ({job['location']})" if job.get("location") else ""
                print(f"    {job['job_title']}{loc}\n    -> {job['job_url']}")
        else:
            print("    No results")
        print(f"    Search link: {row['search_link']}")


def main():
    parser = argparse.ArgumentParser(description="Job search tool: bulk (filter-driven) and targeted (company list) search.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add-company", help="Add a company to the targeted-search list")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--url", help="Career page / job board URL")
    p_add.add_argument("--ats", default="unknown", choices=["greenhouse", "lever", "ashby", "workday", "custom", "unknown"])
    p_add.add_argument("--inactive", action="store_true", help="Add as inactive (excluded from targeted search)")
    p_add.set_defaults(func=cmd_add_company)

    p_list = subparsers.add_parser("list-companies", help="View the company list")
    p_list.set_defaults(func=cmd_list_companies)

    p_bulk = subparsers.add_parser("bulk", help="Generate bulk Google site: search links")
    p_bulk.add_argument("--title", required=True)
    p_bulk.add_argument("--location", default="")
    p_bulk.add_argument("--recency", default="all", choices=["hour", "day", "week", "month", "all"])
    p_bulk.set_defaults(func=cmd_bulk)

    p_targeted = subparsers.add_parser("targeted", help="Search live postings across your company list")
    p_targeted.add_argument("--title", required=True)
    p_targeted.add_argument("--location", default="")
    p_targeted.add_argument("--recency-days", type=int, default=None, help="Only show postings within N days (omit for all)")
    p_targeted.set_defaults(func=cmd_targeted)

    args = parser.parse_args()
    init_db()
    args.func(args)


if __name__ == "__main__":
    main()
