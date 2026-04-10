#!/usr/bin/env python3
"""
Generate feed-data.json from review decisions and newsletter briefs.

Reads:
  - data-updates/archive/review-decisions-*.json (and data-updates/)

Outputs:
  - feed-data.json
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DECISIONS_DIRS = [
    ROOT / "data-updates" / "archive",
    ROOT / "data-updates",
]
OUTPUT = ROOT / "feed-data.json"

# Map claim metrics/tags to feed categories
CATEGORY_MAP = {
    "revenue": "revenue",
    "arr": "revenue",
    "actual-collected": "revenue",
    "funding": "funding",
    "capital": "funding",
    "VC": "funding",
    "launch": "launch",
    "adoption": "adoption",
    "users": "adoption",
    "subscribers": "adoption",
    "inference": "inference",
    "market-share": "inference",
    "coding": "inference",
    "pricing": "pricing",
    "shelfware": "shelfware",
    "partnership": "partnership",
}

TAG_CLASSES = {
    "revenue": "tag-revenue",
    "funding": "tag-funding",
    "launch": "tag-launch",
    "adoption": "tag-launch",
    "inference": "tag-pricing",
    "pricing": "tag-pricing",
    "shelfware": "tag-shelfware",
    "partnership": "tag-partnership",
}


def categorize_claim(claim):
    """Determine feed category from claim's metric and tags."""
    metric = claim.get("metric", "")
    tags = claim.get("tags", [])

    # Check metric first
    if metric in CATEGORY_MAP:
        return CATEGORY_MAP[metric]

    # Then check tags
    for tag in tags:
        if tag in CATEGORY_MAP:
            return CATEGORY_MAP[tag]

    return "launch"  # default


def make_title(claim_text, entity):
    """Generate a short title from claim text."""
    title = claim_text
    # Truncate at ~80 chars on word boundary
    if len(title) > 80:
        title = title[:77].rsplit(" ", 1)[0] + "..."
    return title


def load_decisions(days_back=30):
    """Load accepted claims from review decision files."""
    claims = []
    seen_ids = set()

    for d in DECISIONS_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("review-decisions-*.json"), reverse=True):
            try:
                data = json.loads(f.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            submitted = data.get("submitted_at", "")
            for item in data.get("accepted", []):
                cid = item.get("id", "")
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)

                category = categorize_claim(item)
                date_str = item.get("reviewed_at", submitted)[:10]

                claims.append({
                    "category": category,
                    "tagClass": TAG_CLASSES.get(category, "tag-launch"),
                    "date": date_str,
                    "entity": item.get("entity", ""),
                    "title": make_title(item.get("claim", ""), item.get("entity", "")),
                    "claim": item.get("claim", ""),
                    "value": item.get("value_display", ""),
                    "source": item.get("sourceAuthor", ""),
                    "sourceUrl": item.get("sourceUrl", ""),
                    "impact": item.get("impact"),
                    "majorChange": item.get("major_change", False),
                })

    # Sort by date descending
    claims.sort(key=lambda c: c["date"], reverse=True)
    return claims


def generate():
    claims = load_decisions()

    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=now.weekday())

    feed = {
        "generatedAt": now.isoformat(timespec="seconds") + "Z",
        "weekOf": week_start.strftime("%Y-%m-%d"),
        "dashboardChanges": claims,
    }

    OUTPUT.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n")
    print(f"Generated {OUTPUT}")
    print(f"  {len(claims)} dashboard changes from review decisions")


if __name__ == "__main__":
    generate()
