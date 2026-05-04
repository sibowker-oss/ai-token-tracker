#!/usr/bin/env python3
"""
cohort_metrics.py — Phase 1 cohort health snapshot (wq-081).

Reads sources-registry.json, filters to a Phase-1 cohort by tag (default
"wq-081"), and emits a markdown snapshot for data/phase1.log.md per the
brief §4b/c spec.

The metric set is intentionally split into TWO coverage axes:

    entity_coverage         — sources whose claims attach to one or more
                              of the currently rendered entities (entities
                              with site-data.json:entityDirectory[*]
                              .qualifies_for_detail_page = true).

    denominator_coverage    — sources that feed Capital Sankey, market
                              denominators, or sector-aggregate panels
                              without targeting a specific entity (macro,
                              grid, energy).

This split was added per the wq-081 handoff additional ask: macro APIs
(FRED / World Bank / ABS / RBA) must NOT dilute the entity_coverage stat,
because they are not entity-targeted.

Usage:
    python3 scripts/cohort_metrics.py                  # Phase 1.1 default
    python3 scripts/cohort_metrics.py --tag wq-081     # explicit tag
    python3 scripts/cohort_metrics.py --tag wq-081 --write
        # appends a snapshot block to data/phase1.log.md

Output (stdout): markdown summary including activation rate, claim count,
source-by-source table, routing decisions, and the entity- vs
denominator-coverage split.

Append-only per GUIDELINES §5.4 — never edits past phase1.log.md entries.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "sources-registry.json")
SITE_DATA_PATH = os.path.join(BASE_DIR, "site-data.json")
PHASE1_LOG_PATH = os.path.join(BASE_DIR, "data", "phase1.log.md")

# Sources whose primary output is macro / grid / sector denominators —
# these route their claims to vault-inbox or telemetry-feed but do NOT
# correspond to a specific Ledger entity. Listed by extraction_method
# so adding a new macro adapter doesn't require a method-name parsing
# rule. NOTE: keep in sync with the "routing decisions" block in the
# Week-1 summary.
DENOMINATOR_METHODS = {
    "fred_api",         # US macro
    "worldbank_api",    # global macro
    "abs_api",          # AU macro
    "rba_api",          # AU monetary
    "eia_api",          # US energy aggregates
    "iso_queue_ercot",  # US TX grid queue
    "iso_queue_pjm",    # US PJM grid queue
    "iso_queue_caiso",  # US CAISO grid queue
    "neso_tec",         # UK grid
    "aemo_nem",         # AU grid
    "epoch_frontier",   # DC attribution dataset (denominator + entity hybrid)
    "patentsview_search",  # patent counts (denominator-ish)
    "google_patents_bq",
    "epo_ops",
    "dol_lca_xlsx",     # H-1B aggregate hiring
}


def load_registry():
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def load_rendered_entities():
    """Return the set of entity slugs whose detail page renders."""
    if not os.path.exists(SITE_DATA_PATH):
        return set()
    with open(SITE_DATA_PATH) as f:
        sd = json.load(f)
    directory = sd.get("entityDirectory", [])
    return {
        e.get("slug", "")
        for e in directory
        if e.get("qualifies_for_detail_page")
    }


def filter_cohort(sources, tag):
    """Sources tagged with the cohort tag."""
    return [s for s in sources if tag in (s.get("tags") or [])]


def classify_coverage(source, rendered_slugs):
    """Return 'entity' or 'denominator'.

    Heuristic: if extraction_method is in DENOMINATOR_METHODS, it's
    denominator coverage by design. Otherwise check whether any tag
    matches a rendered entity slug (loose entity link)."""
    if source.get("extraction_method") in DENOMINATOR_METHODS:
        return "denominator"
    tags = source.get("tags") or []
    for t in tags:
        if t in rendered_slugs:
            return "entity"
    # Default: entity coverage (most non-macro sources target entities)
    return "entity"


def status_bucket(s):
    st = s.get("status", "")
    if st == "active":
        return "active"
    if st in ("pending_first_extraction", "pending_credentials"):
        return "pending"
    if st in ("error", "stale"):
        return "error"
    return st or "unknown"


def render_summary(cohort, rendered_slugs, tag):
    n = len(cohort)
    if n == 0:
        return f"# Cohort `{tag}` — no sources tagged.\n"

    by_status = {}
    by_routing = {}
    by_coverage = {"entity": [], "denominator": []}
    by_tier = {1: [], 2: [], 3: []}
    total_claims_first = sum(s.get("last_claims_count") or 0 for s in cohort)

    for s in cohort:
        by_status.setdefault(status_bucket(s), []).append(s)
        by_routing.setdefault(s.get("routing", "vault-inbox"), []).append(s)
        cov = classify_coverage(s, rendered_slugs)
        by_coverage[cov].append(s)
        tier = s.get("tier", 1)
        by_tier.setdefault(tier, []).append(s)

    activation_rate = (
        len(by_status.get("active", [])) / n if n else 0.0
    )

    out = []
    out.append(f"## Cohort `{tag}` snapshot — {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    out.append("")
    out.append(f"- Cohort size: **{n}**")
    out.append(f"- Activation rate: **{activation_rate:.0%}** ({len(by_status.get('active', []))}/{n} active)")
    out.append(f"- Pending: **{len(by_status.get('pending', []))}**, error: **{len(by_status.get('error', []))}**")
    out.append(f"- Total claims on first run (`last_claims_count` sum): **{total_claims_first}**")
    out.append("")
    out.append("### Coverage split")
    out.append("")
    out.append("| Coverage axis | Count | Notes |")
    out.append("|---|---:|---|")
    out.append(f"| **entity_coverage** | {len(by_coverage['entity'])} | Sources whose claims attach to rendered entities (entityDirectory.qualifies = true) |")
    out.append(f"| **denominator_coverage** | {len(by_coverage['denominator'])} | Macro / grid / sector — not entity-targeted |")
    out.append("")

    out.append("### Routing decisions")
    out.append("")
    out.append("| Routing | Count |")
    out.append("|---|---:|")
    for routing, items in sorted(by_routing.items()):
        out.append(f"| `{routing}` | {len(items)} |")
    out.append("")

    out.append("### Sources in cohort")
    out.append("")
    out.append("| id | title | tier | method | type | routing | coverage | status | first-run claims |")
    out.append("|---|---|---:|---|---|---|---|---|---:|")
    for s in cohort:
        cov = classify_coverage(s, rendered_slugs)
        out.append(
            f"| `{s['id']}` | {s.get('title', '')[:50]} | "
            f"{s.get('tier', 1)} | `{s.get('extraction_method', '')}` | "
            f"`{s.get('type', '')}` | `{s.get('routing', '')}` | "
            f"{cov} | `{s.get('status', '')}` | "
            f"{s.get('last_claims_count') or 0} |"
        )
    out.append("")

    # Activation gate evaluation per brief §5a
    out.append("### Phase 1 → Phase 2 gate (brief §5a)")
    out.append("")
    out.append(f"- Activation rate ≥ 80%? **{'YES' if activation_rate >= 0.8 else 'NO'}** (current: {activation_rate:.0%})")
    out.append(f"- Stale rate ≤ 20%? **{'YES' if (len(by_status.get('error', [])) / n <= 0.2) else 'NO'}** (current: {(len(by_status.get('error', [])) / n):.0%})")
    out.append("- Other gate criteria (4-week observation, named gaps, review-queue throughput) require post-Week-1 data and are not evaluated here.")
    out.append("")

    return "\n".join(out)


def append_to_phase1_log(snapshot):
    """Append (never edit) a snapshot block to data/phase1.log.md."""
    header = "# Phase 1 cohort log\n\nAppend-only per GUIDELINES §5.4. Each snapshot is one block.\n\n---\n\n"
    if not os.path.exists(PHASE1_LOG_PATH):
        os.makedirs(os.path.dirname(PHASE1_LOG_PATH), exist_ok=True)
        with open(PHASE1_LOG_PATH, "w") as f:
            f.write(header)
    with open(PHASE1_LOG_PATH, "a") as f:
        f.write(snapshot)
        f.write("\n\n---\n\n")


def main():
    ap = argparse.ArgumentParser(description="Phase 1 cohort metrics snapshot.")
    ap.add_argument("--tag", default="wq-081", help="Cohort tag in registry.tags (default: wq-081)")
    ap.add_argument("--write", action="store_true", help="Append snapshot to data/phase1.log.md")
    args = ap.parse_args()

    registry = load_registry()
    rendered_slugs = load_rendered_entities()
    cohort = filter_cohort(registry["sources"], args.tag)

    snapshot = render_summary(cohort, rendered_slugs, args.tag)
    print(snapshot)

    if args.write:
        append_to_phase1_log(snapshot)
        print(f"\n[appended to {os.path.relpath(PHASE1_LOG_PATH, BASE_DIR)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
