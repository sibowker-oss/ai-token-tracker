#!/usr/bin/env python3
"""wq-102 Stage 1.5 — Dry-run preview of what Stage 2 will change.

Resolves every manifest entry's source_path against the live site-data.json /
entities.json, formats it the way Stage 2 will, and compares it to the
editorial fallback captured at Stage 1. Output groups entries by:

  - identical    : live value matches the literal currently on the page
  - rounding     : live differs by < 0.5 unit (display-only rounding noise)
  - small drift  : 0.5–4.99% relative change
  - notable drift: 5–24.99% relative change
  - large drift  : ≥ 25% relative change OR sign change OR unit mismatch
  - path missing : source_path nominated but the engine doesn't emit it
  - no path      : entry has no source_path (fixed editorial / unresolved)

Writes data/wq-102-supersession-preview.md.

NO HTML CHANGES; this is purely diagnostic.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "wq-102-supersession-preview.md"


def resolve_path(qualified_path: str, site_data: dict, entities: dict):
    """Return (value, exists). Path examples:
      site-data.cumulative.capex_total
      entities.market_aggregates._cumulative_2023_2025.capex_total
      site-data.capital_sankey.utilization.Inference (Paid)
    """
    if not qualified_path:
        return None, False
    if qualified_path.startswith("site-data."):
        blob, rest = site_data, qualified_path[len("site-data."):]
    elif qualified_path.startswith("entities."):
        blob, rest = entities, qualified_path[len("entities."):]
    else:
        return None, False
    obj = blob
    for p in rest.split("."):
        if isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return None, False
    return obj, True


def fmt(value, fmt_kind: str) -> str:
    """Render a numeric value using the manifest entry's format string.

    Mirrors what Stage 2 render_numbers.py will do (centralised formatter).
    """
    if value is None:
        return "—"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    if fmt_kind == "currency_b_compact":
        # ≥10 → whole billions; <10 → 1dp
        if abs(v) >= 10:
            return f"${int(round(v))}B"
        return f"${v:.1f}B"
    if fmt_kind == "currency_m_compact":
        return f"${int(round(v))}M"
    if fmt_kind == "currency_t_compact":
        return f"${v:.2f}T" if abs(v) < 10 else f"${int(round(v))}T"
    if fmt_kind == "currency_unit":
        if abs(v) < 10:
            return f"${v:.2f}"
        return f"${int(round(v))}"
    if fmt_kind == "tokens_compact":
        return f"~{int(round(v))}T"
    if fmt_kind == "percentage_1dp":
        if abs(v - round(v)) < 0.05:
            return f"{int(round(v))}%"
        return f"{v:.1f}%"
    if fmt_kind == "ratio_x_to_1":
        return f"{v:.1f}×" if abs(v - round(v)) > 0.05 else f"{int(round(v))}×"
    if fmt_kind == "count_compact":
        if abs(v) >= 1_000_000_000:
            return f"{v/1e9:.1f}B"
        if abs(v) >= 1_000_000:
            return f"{v/1e6:.1f}M"
        if abs(v) >= 1_000:
            return f"{v/1e3:.0f}K"
        return f"{v:.0f}"
    if fmt_kind == "power_unit":
        return f"{int(round(v))} GW"
    return str(value)


def relative_drift(editorial_v: float, live_v: float) -> float | None:
    if editorial_v is None or live_v is None:
        return None
    if editorial_v == 0:
        return None if live_v == 0 else float("inf")
    return abs(live_v - editorial_v) / abs(editorial_v) * 100.0


def classify_change(editorial_v, live_v) -> str:
    if live_v is None:
        return "path_missing"
    if editorial_v is None:
        return "no_path"
    if editorial_v == live_v:
        return "identical"
    drift = relative_drift(editorial_v, live_v)
    if drift is None:
        return "large_drift"
    if abs(live_v - editorial_v) < 0.5 and drift < 1.0:
        return "rounding"
    if drift < 5.0:
        return "small_drift"
    if drift < 25.0:
        return "notable_drift"
    return "large_drift"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "data" / "numbers-manifest.json"))
    ap.add_argument("--site-data", default=str(ROOT / "site-data.json"))
    ap.add_argument("--entities", default=str(ROOT / "entities.json"))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())
    site_data = json.loads(Path(args.site_data).read_text())
    entities = json.loads(Path(args.entities).read_text())

    rows = []
    for e in manifest["entries"]:
        editorial_raw = e["current_rendered_value"]
        editorial_v = e["editorial_fallback"]["value"]
        sp = e.get("source_path")
        live_v, exists = (None, False)
        if sp:
            live_v, exists = resolve_path(sp, site_data, entities)
        if not exists or sp is None:
            live_v = None
        live_rendered = fmt(live_v, e["format"]) if live_v is not None else None
        klass = classify_change(editorial_v, live_v)
        # No-source entries (fixed) are not really "changes" — bucket them separately
        if e["source_state"] == "fixed":
            klass = "fixed_editorial"
        elif sp is None:
            klass = "no_path"
        elif not exists:
            klass = "path_missing"
        drift_pct = relative_drift(editorial_v, live_v) if live_v is not None else None
        rows.append({
            **e,
            "live_value": live_v,
            "live_rendered": live_rendered,
            "drift_pct": drift_pct,
            "change_class": klass,
        })

    # Bucket order for the report
    BUCKETS = [
        ("large_drift", "Large drift (≥25% change or unit mismatch)"),
        ("notable_drift", "Notable drift (5–25% change)"),
        ("small_drift", "Small drift (0.5–5% change)"),
        ("rounding", "Rounding noise (sub-unit, <1%)"),
        ("identical", "Identical (no change)"),
        ("path_missing", "Path nominated but engine doesn't emit it (Stage 2 → editorial fallback)"),
        ("fixed_editorial", "Fixed editorial (literal preserved by design)"),
        ("no_path", "No source path (gap)"),
    ]
    by_bucket = defaultdict(list)
    for r in rows:
        by_bucket[r["change_class"]].append(r)

    lines = []
    lines.append("# wq-102 — Stage 2 supersession preview\n")
    lines.append("Generated by `scripts/preview_numbers_supersession.py`. Dry-run: shows what each anchored "
                 "number on the six priority pages will render to once Stage 2 ships, compared to the "
                 "literal currently in the HTML.\n")
    lines.append("**No HTML is modified by this script.** Stage 2 will install the binding contract.\n")

    # Headline counts
    lines.append("## Counts\n")
    lines.append("| Bucket | Entries |")
    lines.append("|---|---:|")
    for k, label in BUCKETS:
        lines.append(f"| {label} | {len(by_bucket[k])} |")
    lines.append(f"| **Total** | **{len(rows)}** |\n")

    # Summary of WILL CHANGE numbers (large+notable+small)
    flips = (
        by_bucket["large_drift"] + by_bucket["notable_drift"] + by_bucket["small_drift"]
    )
    lines.append(f"**{len(flips)} numbers will change visibly** when Stage 2 ships "
                 f"(large + notable + small drift, excluding sub-unit rounding).\n")

    # Per-bucket details
    for k, label in BUCKETS:
        items = by_bucket[k]
        if not items:
            continue
        lines.append(f"## {label}  ({len(items)})\n")
        lines.append("| Page | Anchor / Line | Editorial → Live | Drift | Source path |")
        lines.append("|---|---|---|---:|---|")
        for r in sorted(items, key=lambda x: (x["page"], x["_capture"]["line"])):
            anchor = r.get("anchor_dom_id") or f"L{r['_capture']['line']}"
            ed = r["current_rendered_value"]
            lv = r.get("live_rendered") or "—"
            arrow = "→" if ed != lv else "≡"
            drift = f"{r['drift_pct']:.1f}%" if r["drift_pct"] is not None else "—"
            sp = r.get("source_path") or "_(none)_"
            lines.append(
                f"| `{r['page']}` | `{anchor}` | `{ed}` {arrow} `{lv}` | {drift} | `{sp}` |"
            )
        lines.append("")

    # Footnotes
    lines.append("## Notes\n")
    lines.append("- **Editorial → Live** is the headline diff: HTML literal at scan time vs. what "
                 "Stage 2 will render after resolving the source path through the formatter.")
    lines.append("- Sub-unit / sub-1% changes are treated as rounding noise and won't be flagged in the changelog.")
    lines.append("- Entries in *Path nominated but engine doesn't emit it* mean the manifest points "
                 "at a stub the engine doesn't currently produce; Stage 2 will fall back to the literal "
                 "until the engine is extended (logged for follow-on briefs).")
    lines.append("- Entries in *Fixed editorial* are preserved verbatim — supersession is intentionally skipped.")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines))

    # Console summary
    print(f"Wrote {len(rows)} rows → {args.out}")
    for k, label in BUCKETS:
        print(f"  {label}: {len(by_bucket[k])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
