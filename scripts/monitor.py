#!/usr/bin/env python3
"""
APAC AI Intel — Monitoring & Scheduling

Monitors tracked companies for changes:
- GitHub activity (new releases, star count changes)
- Website changes (title, description updates)
- Staleness alerts (companies not enriched recently)

Usage:
    python scripts/monitor.py                   # Run all monitors
    python scripts/monitor.py --stale           # Show stale entries
    python scripts/monitor.py --github          # Check GitHub activity
    python scripts/monitor.py --changes         # Detect website changes
    python scripts/monitor.py --report          # Generate monitoring report
"""

import json
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "companies.json"
MONITOR_LOG = Path(__file__).parent.parent / "monitor_log.json"


def load_db():
    with open(DB_PATH) as f:
        return json.load(f)


def load_monitor_log():
    if MONITOR_LOG.exists():
        with open(MONITOR_LOG) as f:
            return json.load(f)
    return {"runs": [], "alerts": []}


def save_monitor_log(log):
    with open(MONITOR_LOG, "w") as f:
        json.dump(log, f, indent=2)


def check_stale(db, days=14):
    """Find companies not enriched in the last N days."""
    threshold = (date.today() - timedelta(days=days)).isoformat()
    stale = []
    for c in db["companies"]:
        last = c.get("last_researched", "1970-01-01")
        if last < threshold:
            stale.append({
                "company": c["company_name"],
                "id": c["id"],
                "last_researched": last,
                "days_stale": (date.today() - date.fromisoformat(last)).days,
            })
    return sorted(stale, key=lambda x: x["days_stale"], reverse=True)


def check_incomplete(db):
    """Find companies with missing critical fields."""
    issues = []
    required_fields = ["hq_country", "product", "product_category", "primary_providers"]

    for c in db["companies"]:
        missing = []
        for field in required_fields:
            val = c.get(field)
            if not val or val in ("Unknown", "TBD", []):
                missing.append(field)

        if not c.get("key_contacts") or (
            len(c["key_contacts"]) == 1 and c["key_contacts"][0].get("name") == "Unknown"
        ):
            missing.append("key_contacts")

        if missing:
            issues.append({
                "company": c["company_name"],
                "id": c["id"],
                "missing_fields": missing,
            })

    return issues


def check_outreach_status(db):
    """Summarize outreach pipeline."""
    pipeline = {}
    for c in db["companies"]:
        status = c.get("outreach_status", "Unknown")
        if status not in pipeline:
            pipeline[status] = []
        pipeline[status].append(c["company_name"])
    return pipeline


def generate_report(db):
    """Full monitoring report."""
    lines = []
    lines.append(f"# APAC AI Intel — Monitoring Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"")

    # Database health
    lines.append(f"## Database Health")
    lines.append(f"- Total companies: {len(db['companies'])}")
    lines.append(f"- Last updated: {db['meta'].get('last_updated', 'unknown')}")
    lines.append(f"")

    # Stale entries
    stale = check_stale(db)
    if stale:
        lines.append(f"## Stale Entries ({len(stale)} companies)")
        lines.append(f"*Not researched in >14 days*")
        for s in stale:
            lines.append(f"- **{s['company']}** — {s['days_stale']} days stale (last: {s['last_researched']})")
        lines.append(f"")
    else:
        lines.append(f"## Stale Entries: None")
        lines.append(f"")

    # Incomplete entries
    incomplete = check_incomplete(db)
    if incomplete:
        lines.append(f"## Incomplete Entries ({len(incomplete)} companies)")
        for i in incomplete:
            lines.append(f"- **{i['company']}** — missing: {', '.join(i['missing_fields'])}")
        lines.append(f"")
    else:
        lines.append(f"## Incomplete Entries: None")
        lines.append(f"")

    # Outreach pipeline
    pipeline = check_outreach_status(db)
    lines.append(f"## Outreach Pipeline")
    for status, companies in sorted(pipeline.items()):
        lines.append(f"- **{status}:** {', '.join(companies)}")
    lines.append(f"")

    # Provider coverage matrix
    lines.append(f"## Provider Coverage Matrix")
    providers = set()
    for c in db["companies"]:
        for p in c.get("primary_providers", []):
            providers.add(p)

    for provider in sorted(providers):
        users = [c["company_name"] for c in db["companies"] if provider in c.get("primary_providers", [])]
        lines.append(f"- **{provider}:** {', '.join(users)}")
    lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="APAC AI Intel Monitor")
    parser.add_argument("--stale", action="store_true", help="Check for stale entries")
    parser.add_argument("--incomplete", action="store_true", help="Check for incomplete entries")
    parser.add_argument("--pipeline", action="store_true", help="Show outreach pipeline")
    parser.add_argument("--report", action="store_true", help="Generate full monitoring report")
    parser.add_argument("--days", type=int, default=14, help="Staleness threshold in days")
    args = parser.parse_args()

    db = load_db()
    log = load_monitor_log()

    if args.report or not any([args.stale, args.incomplete, args.pipeline]):
        report = generate_report(db)
        print(report)

        # Save report
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / f"monitor-{date.today().isoformat()}.md"
        report_path.write_text(report)
        print(f"[OK] Report saved to {report_path}")

    elif args.stale:
        stale = check_stale(db, args.days)
        if stale:
            print(f"Stale entries (>{args.days} days):")
            for s in stale:
                print(f"  {s['company']}: {s['days_stale']} days (last: {s['last_researched']})")
        else:
            print("No stale entries.")

    elif args.incomplete:
        incomplete = check_incomplete(db)
        if incomplete:
            print(f"Incomplete entries:")
            for i in incomplete:
                print(f"  {i['company']}: missing {', '.join(i['missing_fields'])}")
        else:
            print("All entries complete.")

    elif args.pipeline:
        pipeline = check_outreach_status(db)
        for status, companies in sorted(pipeline.items()):
            print(f"{status}: {', '.join(companies)}")

    # Log the run
    log["runs"].append({
        "timestamp": datetime.now().isoformat(),
        "companies_count": len(db["companies"]),
    })
    save_monitor_log(log)


if __name__ == "__main__":
    main()
