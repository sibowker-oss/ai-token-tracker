#!/usr/bin/env python3
"""
APAC AI Intel — Company Enrichment Pipeline

Scrapes and enriches company data from multiple sources:
- Crunchbase (via web scraping)
- GitHub (API)
- LinkedIn (metadata only)
- Company websites (meta tags, about pages)
- Tracxn (web scraping)

Usage:
    python scripts/enrich.py                    # Enrich all companies
    python scripts/enrich.py --company dify     # Enrich specific company
    python scripts/enrich.py --add "Company Name" --url "https://example.com"
"""

import json
import os
import re
import sys
import argparse
import urllib.request
import urllib.error
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from log_run import logged_run  # noqa: E402
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "companies.json"
COMPANIES_DIR = Path(__file__).parent.parent / "companies"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"User-Agent": "APAC-AI-Intel/1.0"}


def load_db():
    with open(DB_PATH) as f:
        return json.load(f)


def save_db(db):
    db["meta"]["last_updated"] = date.today().isoformat()
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"[OK] Database saved ({len(db['companies'])} companies)")


def fetch_url(url, headers=None):
    """Simple URL fetch with error handling."""
    req_headers = {**HEADERS, **(headers or {})}
    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"  [WARN] Failed to fetch {url}: {e}")
        return None


def enrich_from_github(company):
    """Pull GitHub org stats if we can find their org."""
    sources = company.get("sources", [])
    github_urls = [s for s in sources if "github.com" in s]

    if not github_urls:
        return {}

    for url in github_urls:
        match = re.search(r"github\.com/([^/]+)(?:/([^/]+))?", url)
        if not match:
            continue

        org_or_user = match.group(1)
        repo_name = match.group(2)

        api_headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            api_headers["Authorization"] = f"token {GITHUB_TOKEN}"

        enriched = {}

        # If it's a specific repo
        if repo_name:
            data = fetch_url(
                f"https://api.github.com/repos/{org_or_user}/{repo_name}",
                api_headers,
            )
            if data:
                repo = json.loads(data)
                enriched["github_stars"] = repo.get("stargazers_count")
                enriched["github_forks"] = repo.get("forks_count")
                enriched["github_language"] = repo.get("language")
                enriched["github_last_push"] = repo.get("pushed_at")
                print(f"  [GitHub] {org_or_user}/{repo_name}: {enriched['github_stars']} stars")

        # Org info
        data = fetch_url(
            f"https://api.github.com/orgs/{org_or_user}", api_headers
        )
        if data:
            org = json.loads(data)
            enriched["github_public_repos"] = org.get("public_repos")
            enriched["github_followers"] = org.get("followers")

        if enriched:
            return enriched

    return {}


def enrich_from_website(company):
    """Scrape basic metadata from company website."""
    sources = company.get("sources", [])
    websites = [
        s for s in sources if "github.com" not in s and "tracxn" not in s and "linkedin" not in s
    ]

    if not websites:
        return {}

    url = websites[0]
    html = fetch_url(url)
    if not html:
        return {}

    enriched = {}

    # Extract title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        enriched["website_title"] = title_match.group(1).strip()[:200]

    # Extract meta description
    desc_match = re.search(
        r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
        html,
        re.IGNORECASE,
    )
    if desc_match:
        enriched["website_description"] = desc_match.group(1).strip()[:500]

    # Look for pricing page link
    if re.search(r'href=["\'][^"\']*pric', html, re.IGNORECASE):
        enriched["has_pricing_page"] = True

    # Look for API/docs link
    if re.search(r'href=["\'][^"\']*(?:docs|api|developer)', html, re.IGNORECASE):
        enriched["has_api_docs"] = True

    if enriched:
        print(f"  [Web] Scraped metadata from {url}")

    return enriched


def enrich_company(company):
    """Run all enrichment sources for a single company."""
    print(f"\nEnriching: {company['company_name']}")

    github_data = enrich_from_github(company)
    web_data = enrich_from_website(company)

    # Merge enrichment data
    enrichment = {**github_data, **web_data}

    if enrichment:
        if "enrichment" not in company:
            company["enrichment"] = {}
        company["enrichment"].update(enrichment)
        company["enrichment"]["last_enriched"] = datetime.now().isoformat()
        company["last_researched"] = date.today().isoformat()
        print(f"  [OK] Added {len(enrichment)} enrichment fields")
    else:
        print(f"  [SKIP] No new data found")

    return company


def add_company_scaffold(name, url, db):
    """Add a new empty company entry to the database."""
    company_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    # Check for duplicates
    existing_ids = [c["id"] for c in db["companies"]]
    if company_id in existing_ids:
        print(f"[ERROR] Company '{company_id}' already exists")
        return db

    new_company = {
        "id": company_id,
        "company_name": name,
        "hq_country": "Unknown",
        "apac_presence": "Unknown",
        "product": "TBD",
        "product_category": "TBD",
        "models_used": [],
        "primary_providers": [],
        "estimated_volume_tier": "Unknown",
        "funding": None,
        "revenue_estimate": None,
        "employee_count": None,
        "key_contacts": [],
        "outreach_status": "Not started",
        "notes": "",
        "last_researched": date.today().isoformat(),
        "sources": [url] if url else [],
    }

    db["companies"].append(new_company)
    print(f"[OK] Added scaffold for '{name}' (id: {company_id})")

    # Create markdown profile
    md_path = COMPANIES_DIR / f"{company_id}.md"
    md_path.write_text(f"# {name}\n\n## Overview\n| Field | Value |\n|-------|-------|\n| HQ | Unknown |\n| Founded | Unknown |\n| Employees | Unknown |\n| Funding | Unknown |\n| Revenue | Unknown |\n\n## Product\nTBD\n\n## Token Buying Profile\n**Volume Tier: Unknown**\n\n## Key Contacts\nTBD\n\n## Outreach Status\nNot started\n\n## Intel Notes\n- Added {date.today().isoformat()}\n")
    print(f"[OK] Created {md_path}")

    return db


def generate_summary_stats(db):
    """Print summary statistics."""
    companies = db["companies"]
    print(f"\n{'='*60}")
    print(f"APAC AI Intel Database Summary")
    print(f"{'='*60}")
    print(f"Total companies: {len(companies)}")

    # By country
    countries = {}
    for c in companies:
        country = c.get("hq_country", "Unknown").split("(")[0].strip()
        countries[country] = countries.get(country, 0) + 1
    print(f"\nBy HQ Country:")
    for country, count in sorted(countries.items(), key=lambda x: -x[1]):
        print(f"  {country}: {count}")

    # By volume tier
    tiers = {}
    for c in companies:
        tier = c.get("estimated_volume_tier", "Unknown").split("—")[0].split("—")[0].strip()
        tiers[tier] = tiers.get(tier, 0) + 1
    print(f"\nBy Volume Tier:")
    for tier, count in sorted(tiers.items()):
        print(f"  {tier}: {count}")

    # By category
    cats = {}
    for c in companies:
        cat = c.get("product_category", "Unknown")
        cats[cat] = cats.get(cat, 0) + 1
    print(f"\nBy Category:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Provider coverage
    all_providers = set()
    for c in companies:
        for p in c.get("primary_providers", []):
            all_providers.add(p)
    print(f"\nProviders tracked: {', '.join(sorted(all_providers))}")

    # Outreach status
    statuses = {}
    for c in companies:
        status = c.get("outreach_status", "Unknown")
        statuses[status] = statuses.get(status, 0) + 1
    print(f"\nOutreach Status:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")


def main():
    with logged_run("enrich.py") as outputs:
        _main_impl(outputs)


def _main_impl(outputs):
    parser = argparse.ArgumentParser(description="APAC AI Intel Enrichment Pipeline")
    parser.add_argument("--company", help="Enrich a specific company by ID")
    parser.add_argument("--add", help="Add a new company (provide name)")
    parser.add_argument("--url", help="Website URL for new company")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--all", action="store_true", help="Enrich all companies")
    args = parser.parse_args()

    db = load_db()

    if args.stats:
        generate_summary_stats(db)
        return

    if args.add:
        db = add_company_scaffold(args.add, args.url, db)
        save_db(db)
        return

    if args.company:
        targets = [c for c in db["companies"] if c["id"] == args.company]
        if not targets:
            print(f"[ERROR] Company '{args.company}' not found")
            print(f"Available: {', '.join(c['id'] for c in db['companies'])}")
            sys.exit(1)
    elif args.all:
        targets = db["companies"]
    else:
        # Default: enrich all
        targets = db["companies"]

    for company in targets:
        enrich_company(company)

    save_db(db)
    generate_summary_stats(db)

    outputs["companies_enriched"] = len(targets)
    outputs["companies_total"] = len(db.get("companies", []))


if __name__ == "__main__":
    main()
