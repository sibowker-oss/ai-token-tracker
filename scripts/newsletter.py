#!/usr/bin/env python3
"""
APAC AI Intel — Newsletter Formatter

Generates a formatted newsletter from the company database.
Outputs: Markdown, HTML, or plain text.

Usage:
    python scripts/newsletter.py                          # Full newsletter (markdown)
    python scripts/newsletter.py --format html            # HTML output
    python scripts/newsletter.py --format text            # Plain text
    python scripts/newsletter.py --new-only               # Only companies added since last newsletter
    python scripts/newsletter.py --output newsletter.md   # Write to file
"""

import json
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "companies.json"
OUTPUT_DIR = Path(__file__).parent.parent / "newsletters"


def load_db():
    with open(DB_PATH) as f:
        return json.load(f)


def format_contacts(contacts):
    if not contacts:
        return "No contacts identified"
    lines = []
    for c in contacts:
        name = c.get("name", "Unknown")
        title = c.get("title", "")
        if name == "Unknown":
            continue
        lines.append(f"  - **{name}** — {title}")
    return "\n".join(lines) if lines else "No named contacts"


def format_providers(providers):
    if not providers:
        return "Unknown"
    return ", ".join(providers)


def generate_markdown(db, new_only=False, since_date=None):
    companies = db["companies"]

    if new_only and since_date:
        companies = [
            c for c in companies
            if c.get("last_researched", "") >= since_date
        ]

    today = date.today()
    issue_num = (today - date(2026, 3, 26)).days // 7 + 1

    lines = []
    lines.append(f"# APAC AI Intelligence Brief")
    lines.append(f"**Issue #{issue_num} — {today.strftime('%B %d, %Y')}**")
    lines.append(f"")
    lines.append(f"*Tracking who's building on AI APIs across Asia-Pacific.*")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Summary stats
    lines.append(f"## This Week at a Glance")
    lines.append(f"- **{len(companies)} companies** tracked")

    volume_high = [c for c in companies if "High" in c.get("estimated_volume_tier", "")]
    lines.append(f"- **{len(volume_high)} high-volume** token buyers identified")

    providers = set()
    for c in companies:
        for p in c.get("primary_providers", []):
            providers.add(p)
    lines.append(f"- **{len(providers)} AI providers** in the supply chain")
    lines.append(f"")

    # Provider heatmap
    lines.append(f"## Provider Demand Map")
    lines.append(f"*Which providers are APAC companies buying from?*")
    lines.append(f"")
    provider_counts = {}
    for c in companies:
        for p in c.get("primary_providers", []):
            provider_counts[p] = provider_counts.get(p, 0) + 1
    for provider, count in sorted(provider_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count + "░" * (len(companies) - count)
        lines.append(f"| {provider:<12} | {bar} | {count}/{len(companies)} companies |")
    lines.append(f"")

    # Company profiles — sorted by volume tier
    tier_order = {"Very High": 0, "High": 1, "Medium": 2, "Low": 3, "Unknown": 4}

    def tier_sort(c):
        tier_text = c.get("estimated_volume_tier", "Unknown")
        for key in tier_order:
            if key in tier_text:
                return tier_order[key]
        return 5

    companies_sorted = sorted(companies, key=tier_sort)

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Company Profiles")
    lines.append(f"")

    for company in companies_sorted:
        lines.append(f"### {company['company_name']}")
        lines.append(f"**{company.get('hq_country', 'Unknown')}** | {company.get('product_category', 'Unknown')}")
        lines.append(f"")
        lines.append(f"> {company.get('product', 'TBD')}")
        lines.append(f"")
        lines.append(f"**Volume:** {company.get('estimated_volume_tier', 'Unknown')}")
        lines.append(f"")
        lines.append(f"**Providers:** {format_providers(company.get('primary_providers', []))}")
        lines.append(f"")
        lines.append(f"**Models:** {', '.join(company.get('models_used', [])[:5])}")
        if len(company.get("models_used", [])) > 5:
            lines.append(f" + {len(company['models_used']) - 5} more")
        lines.append(f"")

        if company.get("funding"):
            lines.append(f"**Funding:** {company['funding']}")
        if company.get("revenue_estimate"):
            lines.append(f"**Revenue:** {company['revenue_estimate']}")
        if company.get("employee_count"):
            lines.append(f"**Team:** ~{company['employee_count']} employees")
        lines.append(f"")

        lines.append(f"**Key Contacts:**")
        lines.append(format_contacts(company.get("key_contacts", [])))
        lines.append(f"")

        if company.get("notes"):
            lines.append(f"**Intel:** {company['notes'][:300]}")
            lines.append(f"")

        lines.append(f"---")
        lines.append(f"")

    # Footer
    lines.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} by APAC AI Intelligence Pipeline*")
    lines.append(f"*Data freshness: companies last enriched {db['meta'].get('last_updated', 'unknown')}*")

    return "\n".join(lines)


def markdown_to_html(md_content):
    """Convert markdown newsletter to basic HTML with inline styles."""
    html_lines = []
    html_lines.append("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; max-width: 720px; margin: 0 auto; padding: 24px; color: #1a1a2e; background: #fafafa; line-height: 1.6; }
  h1 { color: #0f3460; border-bottom: 3px solid #e94560; padding-bottom: 12px; }
  h2 { color: #16213e; margin-top: 32px; }
  h3 { color: #0f3460; margin-top: 24px; }
  blockquote { border-left: 4px solid #e94560; margin: 12px 0; padding: 8px 16px; background: #f0f0f5; }
  table { border-collapse: collapse; width: 100%; margin: 8px 0; }
  td, th { padding: 4px 8px; text-align: left; font-family: monospace; font-size: 14px; }
  hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
  strong { color: #16213e; }
  code { background: #eee; padding: 2px 6px; border-radius: 3px; font-size: 14px; }
  .footer { color: #888; font-size: 13px; margin-top: 40px; }
</style>
</head>
<body>
""")

    in_table = False
    for line in md_content.split("\n"):
        # Headers
        if line.startswith("### "):
            html_lines.append(f"<h3>{process_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{process_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{process_inline(line[2:])}</h1>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{process_inline(line[2:])}</blockquote>")
        elif line.startswith("| "):
            if not in_table:
                html_lines.append("<table>")
                in_table = True
            cells = [c.strip() for c in line.split("|")[1:-1]]
            html_lines.append("<tr>" + "".join(f"<td>{process_inline(c)}</td>" for c in cells) + "</tr>")
        elif line.startswith("- "):
            html_lines.append(f"<li>{process_inline(line[2:])}</li>")
        elif line.startswith("---"):
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append("<hr>")
        elif line.startswith("*") and line.endswith("*"):
            html_lines.append(f"<p class='footer'><em>{line.strip('*')}</em></p>")
        elif line.strip():
            if in_table:
                html_lines.append("</table>")
                in_table = False
            html_lines.append(f"<p>{process_inline(line)}</p>")

    if in_table:
        html_lines.append("</table>")

    html_lines.append("</body></html>")
    return "\n".join(html_lines)


def process_inline(text):
    """Process inline markdown: bold, italic, links."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = __import__("re").sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = __import__("re").sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def markdown_to_text(md_content):
    """Strip markdown to plain text."""
    import re
    text = md_content
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s*", "  ", text, flags=re.MULTILINE)
    text = re.sub(r"^---$", "-" * 60, text, flags=re.MULTILINE)
    return text


def main():
    parser = argparse.ArgumentParser(description="APAC AI Intel Newsletter Generator")
    parser.add_argument("--format", choices=["markdown", "html", "text"], default="markdown")
    parser.add_argument("--new-only", action="store_true", help="Only include recently added companies")
    parser.add_argument("--since", help="Include companies researched since date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    db = load_db()

    since_date = args.since
    if args.new_only and not since_date:
        since_date = (date.today() - timedelta(days=7)).isoformat()

    md = generate_markdown(db, new_only=args.new_only, since_date=since_date)

    if args.format == "html":
        content = markdown_to_html(md)
        ext = ".html"
    elif args.format == "text":
        content = markdown_to_text(md)
        ext = ".txt"
    else:
        content = md
        ext = ".md"

    if args.output:
        out_path = Path(args.output)
    else:
        OUTPUT_DIR.mkdir(exist_ok=True)
        out_path = OUTPUT_DIR / f"brief-{date.today().isoformat()}{ext}"

    out_path.write_text(content)
    print(f"[OK] Newsletter written to {out_path}")
    print(f"     Format: {args.format}")
    print(f"     Companies: {len(db['companies'])}")


if __name__ == "__main__":
    main()
