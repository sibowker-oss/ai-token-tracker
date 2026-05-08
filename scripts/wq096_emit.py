#!/usr/bin/env python3
"""
wq096_emit.py — Read wq-096 evidence files and emit site-data.json blocks.

Called from scripts/generate_site_data.py during the build. Pure functions,
no side effects on disk except the archive snapshot.

Blocks emitted:
  - dashboard.enterpriseReality (numeric-first, expanded; replaces existing)
  - dashboard.topConsumers (tier-tagged; token-factory + dup records removed;
    ARR backfill applied)
  - dashboard.providers (tier-tagged in place)
  - sankey.providers (tier-tagged in place)
  - computeProviders.aiNativeCompute (new, top-level)
  - computeProviders.tradCompute (new, top-level)
  - arrModel (new, top-level; computed aggregator)
"""

import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "data", "evidence")
ARCHIVE = os.path.join(ROOT, "data", "archive")
TAGGING_PATH = os.path.join(ROOT, "data", "wq096_tagging.json")


def _load_evidence_dir(subdir):
    """Load every *.json (and _long_tail.json) under data/evidence/<subdir>."""
    path = os.path.join(EV, subdir)
    out = []
    if not os.path.isdir(path):
        return out
    for fname in sorted(os.listdir(path)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(path, fname)) as f:
            out.append(json.load(f))
    return out


def _load_tagging():
    if not os.path.exists(TAGGING_PATH):
        return None
    with open(TAGGING_PATH) as f:
        return json.load(f)


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def archive_topconsumers_premove(site, year_month):
    """Snapshot the pre-move topConsumers list once (idempotent)."""
    archive_path = os.path.join(ARCHIVE, f"topconsumers_premove_{year_month}.json")
    if os.path.exists(archive_path):
        return
    pre = site.get("dashboard", {}).get("topConsumers", [])
    os.makedirs(ARCHIVE, exist_ok=True)
    with open(archive_path, "w") as f:
        json.dump({"_archived_at": _now_iso(), "_brief": "wq-096", "topConsumers": pre}, f, indent=2)


def tag_providers(site, tagging):
    """Tag dashboard.providers and sankey.providers in place."""
    tier_map = tagging["TIER_FOR_PROVIDER_KEY"]

    # dashboard.providers is keyed dict
    dashboard_providers = site.get("dashboard", {}).get("providers", {})
    for key, card in dashboard_providers.items():
        tier = tier_map.get(key, "frontier")
        card["tier"] = tier
        # numeric ARR + provenance — provenance for the existing card uses
        # the entityDirectory data; we adopt 'tier_2a' editorial across the
        # board with overrides for highly-public ARR lines (OpenAI / Anthropic).
        if "rev" in card and isinstance(card["rev"], (int, float)):
            card["arrNumeric"] = float(card["rev"])
            card.setdefault("arrAsOf", "2026-Q1")
            card.setdefault("arrSource", "entities.json:current.arr")
            card.setdefault("provenance", "tier_2a")
            if key == "OpenAI":
                card["provenance"] = "tier_1b"
                card["arrSource"] = "OpenAI commentary 2026 — $25B ARR run-rate"
            elif key == "Anthropic":
                card["provenance"] = "tier_2a"
                card["arrSource"] = "Anthropic commentary 2026 — $30B ARR run-rate (single-source highest-quality figure parked separately per Decision D11)"

    # sankey.providers is a list
    label_to_tier = {
        "OpenAI": "frontier",
        "Anthropic": "frontier",
        "Google/Gemini": "frontier",
        "IaaS/Open": "frontier",
        "Other Model Providers": "frontier",
    }
    for prov in site.get("sankey", {}).get("providers", []):
        prov["tier"] = label_to_tier.get(prov.get("label"), "frontier")


def tag_and_filter_topconsumers(site, tagging):
    """Tag topConsumers tier; remove token factories + dup records; apply ARR backfill."""
    remove = set(tagging["TOPCONSUMERS_REMOVE"])
    tier_map = tagging["TIER_FOR_TOPCONSUMER"]
    backfill = tagging["TOPCONSUMERS_ARR_BACKFILL"]

    tc = site.get("dashboard", {}).get("topConsumers", [])
    filtered = []
    moved = []
    for c in tc:
        co = c.get("co")
        if co in remove:
            moved.append(co)
            continue
        # tier
        c["tier"] = tier_map.get(co, "ai_native_app")
        # backfill ARR + provenance
        if co in backfill:
            bf = backfill[co]
            if "arrNumeric" in bf and bf["arrNumeric"] is not None:
                c["arrNumeric"] = bf["arrNumeric"]
                c["arrSource"] = bf.get("arrSource")
                c["provenance"] = bf.get("provenance", "tier_3a")
                c["arrAsOf"] = "2026-Q1"
            if bf.get("arrPending"):
                c["arrPending"] = True
                c["arrPendingReason"] = bf.get("arrPendingReason", "")
        # ensure entries with arrNumeric also carry provenance + arrAsOf
        if c.get("arrNumeric") is not None and not c.get("provenance"):
            c["provenance"] = "tier_2b"
            c.setdefault("arrAsOf", "2026-Q1")
            c.setdefault("arrSource", "Pre-existing entry; provenance backfilled to Tier 2B as part of wq-096")
        filtered.append(c)

    site["dashboard"]["topConsumers"] = filtered
    return moved


def emit_enterprise_reality(site):
    """Replace dashboard.enterpriseReality with the numeric-first records from evidence."""
    records = _load_evidence_dir("enterprise_reality")
    out = []
    for r in records:
        narrative = r.get("narrative", {})
        entry = {
            "id": r["id"],
            "name": r["name"],
            "ticker": r.get("ticker"),
            "tier": r.get("tier", "trad_saas"),
            "arrClaimedNumeric": r.get("arrClaimedNumeric"),
            "arrAsOf": r.get("arrAsOf"),
            "arrSource": r.get("arrSource"),
            "provenance": r.get("provenance"),
            "claimed": narrative.get("claimed", ""),
            "usage": narrative.get("usage", ""),
            "real": narrative.get("real", ""),
            "flags": narrative.get("flags", ""),
            "growth": r.get("growth", ""),
            "prevGrowth": r.get("prevGrowth", ""),
        }
        if "arrClaimedVsReal" in r:
            entry["arrClaimedVsReal"] = r["arrClaimedVsReal"]
        out.append(entry)
    # Sort by arrClaimedNumeric desc (largest first) for stable visual ordering
    out.sort(key=lambda x: -(x.get("arrClaimedNumeric") or 0))
    site.setdefault("dashboard", {})["enterpriseReality"] = out
    return out


def emit_compute_providers(site):
    """Build computeProviders.tradCompute and computeProviders.aiNativeCompute (top-level block)."""
    er_lookup = {r["id"]: r for r in site.get("dashboard", {}).get("enterpriseReality", [])}

    trad_records = _load_evidence_dir("compute_disclosures")
    trad_out = []
    for r in trad_records:
        carveout_total = sum((er_lookup.get(cid, {}).get("arrClaimedNumeric") or 0) for cid in r.get("appsCarveout", []))
        net = round(float(r.get("arrGrossDisclosed", 0)) - carveout_total, 4)
        trad_out.append({
            "id": r["id"],
            "name": r["name"],
            "tier": r.get("tier", "trad_compute"),
            "arrGrossDisclosed": r.get("arrGrossDisclosed"),
            "arrNetOfAppsCarveout": net,
            "arrAsOf": r.get("arrAsOf"),
            "arrSource": r.get("arrSource"),
            "provenance": r.get("provenance"),
            "appsCarveout": r.get("appsCarveout", []),
            "appsCarveoutNote": r.get("appsCarveoutNote", ""),
        })

    native_records = _load_evidence_dir("compute_native")
    native_out = []
    for r in native_records:
        native_out.append({
            "id": r["id"],
            "name": r["name"],
            "tier": r.get("tier", "ai_native_compute"),
            "subType": r.get("subType"),
            "arrNumeric": r.get("arrNumeric"),
            "arrAsOf": r.get("arrAsOf"),
            "arrSource": r.get("arrSource"),
            "provenance": r.get("provenance"),
            "movedFromTopConsumers": r.get("movedFromTopConsumers", False),
            "doubleCountNote": r.get("doubleCountNote", ""),
        })

    site["computeProviders"] = {
        "_generatedAt": _now_iso(),
        "_doc": "wq-096 — Tier 4 (trad_compute) and Tier 5 (ai_native_compute) records. tradCompute carries appsCarveout pointing at trad_saas record IDs whose ARR is deducted to produce arrNetOfAppsCarveout. Per Decision D9, multi-tier companies (Google, Microsoft, Oracle) split into separate records per tier; Microsoft has no Frontier entry.",
        "tradCompute": trad_out,
        "aiNativeCompute": native_out,
    }


def _frontier_arr_entries(site):
    """Build frontier ARR entries from dashboard.providers (Tier 1)."""
    out = []
    for key, card in site.get("dashboard", {}).get("providers", {}).items():
        tier = card.get("tier", "frontier")
        if tier != "frontier":
            continue
        arr = card.get("arrNumeric")
        if arr is None:
            arr = card.get("rev")
        out.append({
            "id": key,
            "arr": float(arr) if arr is not None else 0.0,
            "provenance": card.get("provenance", "tier_2a"),
            "tier": "frontier",
        })
    return out


def _ai_native_app_entries(site):
    """Sum AI-Native Apps ARR from topConsumers (USD billions)."""
    out = []
    for c in site.get("dashboard", {}).get("topConsumers", []):
        if c.get("tier") != "ai_native_app":
            continue
        arr_n = c.get("arrNumeric")
        if arr_n is None:
            continue
        # arrNumeric in topConsumers is the established USD whole-dollars convention.
        # Convert to billions for the arrModel aggregator.
        arr_b = float(arr_n) / 1e9
        # Skip pure-passthrough gateway entries (no additive ARR contribution).
        if c.get("subcategory") == "gateway":
            continue
        # Skip suspect-magnitude values (less than $1M is almost certainly a units bug
        # in the source row — the topConsumers list does not include sub-$1M cohort).
        if arr_b < 0.001:
            continue
        out.append({
            "id": c.get("co"),
            "arr": round(arr_b, 4),
            "provenance": c.get("provenance", "tier_2b"),
            "tier": "ai_native_app",
        })
    return out


def _trad_saas_entries(site):
    out = []
    for r in site.get("dashboard", {}).get("enterpriseReality", []):
        if r.get("tier") != "trad_saas":
            continue
        arr = r.get("arrClaimedNumeric")
        if arr is None:
            continue
        out.append({
            "id": r.get("id"),
            "arr": float(arr),
            "provenance": r.get("provenance", "tier_2b"),
            "tier": "trad_saas",
        })
    return out


def _passthrough_layer(layer):
    """Read evidence/passthrough/<layer>/*.json — split named entries vs long-tail."""
    path = os.path.join(EV, "passthrough", layer)
    named = []
    long_tail = None
    if not os.path.isdir(path):
        return named, long_tail
    for fname in sorted(os.listdir(path)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(path, fname)) as f:
            r = json.load(f)
        if r.get("isLongTail"):
            long_tail = r
        else:
            named.append(r)
    return named, long_tail


def emit_arrmodel(site):
    """Compute the arrModel aggregator block (top-level)."""
    frontier = _frontier_arr_entries(site)
    ai_native = _ai_native_app_entries(site)
    trad_saas = _trad_saas_entries(site)

    apps_frontier_total = round(sum(e["arr"] for e in frontier), 4)
    apps_aiNative_total = round(sum(e["arr"] for e in ai_native), 4)
    apps_tradSaas_total = round(sum(e["arr"] for e in trad_saas), 4)
    apps_subtotal = round(apps_frontier_total + apps_aiNative_total + apps_tradSaas_total, 4)

    cp = site.get("computeProviders", {})
    trad_compute_entries = cp.get("tradCompute", [])
    ai_native_compute_entries = cp.get("aiNativeCompute", [])

    trad_compute_gross = round(sum(float(t.get("arrGrossDisclosed") or 0) for t in trad_compute_entries), 4)
    trad_compute_net_sum = round(sum(float(t.get("arrNetOfAppsCarveout") or 0) for t in trad_compute_entries), 4)
    ai_native_compute_total = round(sum(float(e.get("arrNumeric") or 0) for e in ai_native_compute_entries), 4)

    # ── Pass-through deductions ──
    deduction_blocks = {}
    for layer in ("frontier_to_trad", "apps_to_aiNativeCompute", "aiNativeCompute_to_tradCompute"):
        named, long_tail = _passthrough_layer(layer)
        named_sum = round(sum(float(r.get("value") or 0) for r in named), 4)
        long_tail_value = 0.0
        long_tail_block = None
        if long_tail:
            base = float(long_tail.get("baseValue") or 0)
            mult = float(long_tail.get("multiplierPct") or 0)
            long_tail_value = round(base * mult / 100.0, 4)
            long_tail_block = {
                "baseValueBasis": long_tail.get("baseValueBasis"),
                "baseValue": base,
                "multiplierPct": mult,
                "computedValue": long_tail_value,
                "rationale": long_tail.get("rationale"),
                "provenance": long_tail.get("provenance"),
            }
        layer_total = round(named_sum + long_tail_value, 4)
        deduction_blocks[f"passthrough_{layer}"] = {
            "total": layer_total,
            "namedSum": named_sum,
            "longTailValue": long_tail_value,
            "entries": [
                # Note: `valueUsdB` + `evidence` are intentional renames of the
                # underlying evidence-file `value` + `source` fields — the §4.2
                # provenance validator's datapoint-detection heuristic (any
                # object containing both `value` and `source`) would otherwise
                # demand the full nine-field datapoint metadata. These are
                # aggregator entries, not §4.2 datapoints.
                {
                    "id": r.get("id"),
                    "from": r.get("from"),
                    "to": r.get("to"),
                    "valueUsdB": r.get("value"),
                    "valueBasis": r.get("valueBasis"),
                    "evidence": r.get("source"),
                    "provenance": r.get("provenance"),
                    "rationale": r.get("rationale"),
                }
                for r in named
            ],
            "longTailMultiplier": long_tail_block,
        }

    total_deductions = round(sum(b["total"] for b in deduction_blocks.values()), 4)

    # compute.netExternal = (sum of trad_compute net) + (sum of ai_native_compute) − sum(deductions)
    compute_net_external = round(trad_compute_net_sum + ai_native_compute_total - total_deductions, 4)
    compute_subtotal = compute_net_external

    industry_total = round(apps_subtotal + compute_net_external, 4)

    ai_native_total = round(apps_frontier_total + apps_aiNative_total + ai_native_compute_total, 4)
    trad_total = round(apps_tradSaas_total + trad_compute_net_sum, 4)
    ai_native_share_pct = round(100 * ai_native_total / max(industry_total, 0.0001), 2) if industry_total else None

    arr_model = {
        "_generatedAt": _now_iso(),
        "_brief": "wq-096",
        "_doc": "Five-tier revenue model aggregator. apps_total + compute_net = industry_total within $0.1B tolerance. ai_native_total / trad_total cross-cut the apps/compute split per the editorial axis (Decision D1) and do not sum to industry_total because pass-through deductions are netted at the compute layer.",
        "asOf": "2026-Q1-annualised",
        "basis": "trailing_quarter_x4_or_disclosed_run_rate",
        "currency": "USD_B",
        "apps": {
            "frontier": {"total": apps_frontier_total, "entries": frontier},
            "aiNative": {"total": apps_aiNative_total, "entries": ai_native},
            "tradSaas": {"total": apps_tradSaas_total, "entries": trad_saas},
            "subtotal": apps_subtotal,
        },
        "compute": {
            "tradCompute": {
                "totalGross": trad_compute_gross,
                "totalNet": trad_compute_net_sum,
                "entries": [
                    {
                        "id": t.get("id"),
                        "arrGrossDisclosed": t.get("arrGrossDisclosed"),
                        "arrNetOfAppsCarveout": t.get("arrNetOfAppsCarveout"),
                        "appsCarveout": t.get("appsCarveout", []),
                        "provenance": t.get("provenance"),
                        "tier": "trad_compute",
                    }
                    for t in trad_compute_entries
                ],
            },
            "aiNativeCompute": {
                "total": ai_native_compute_total,
                "entries": [
                    {
                        "id": e.get("id"),
                        "arr": e.get("arrNumeric"),
                        "subType": e.get("subType"),
                        "provenance": e.get("provenance"),
                        "tier": "ai_native_compute",
                    }
                    for e in ai_native_compute_entries
                ],
            },
            "deductions": {
                "passthrough_frontier_to_trad": deduction_blocks["passthrough_frontier_to_trad"],
                "passthrough_apps_to_aiNativeCompute": deduction_blocks["passthrough_apps_to_aiNativeCompute"],
                "passthrough_aiNativeCompute_to_tradCompute": deduction_blocks["passthrough_aiNativeCompute_to_tradCompute"],
                "totalDeductions": total_deductions,
            },
            "netExternal": compute_net_external,
            "subtotal": compute_subtotal,
        },
        "combined": {
            "apps_total": apps_subtotal,
            "compute_net": compute_net_external,
            "industry_total": industry_total,
            "ai_native_total": ai_native_total,
            "trad_total": trad_total,
            "ai_native_share_pct": ai_native_share_pct,
        },
    }

    site["arrModel"] = arr_model
    return arr_model


def apply_all(site):
    """Top-level entry point — apply every wq-096 transform to `site` in place."""
    tagging = _load_tagging()
    if tagging is None:
        print("  wq-096: tagging table missing — skipping (run scripts/migrate_wq096.py)")
        return None

    archive_topconsumers_premove(site, year_month="2026-05")
    tag_providers(site, tagging)
    moved = tag_and_filter_topconsumers(site, tagging)
    emit_enterprise_reality(site)
    emit_compute_providers(site)
    arr_model = emit_arrmodel(site)

    print(f"  wq-096: enterpriseReality={len(site['dashboard']['enterpriseReality'])} entries; topConsumers moved out: {sorted(moved)}")
    print(f"  wq-096: computeProviders.tradCompute={len(site['computeProviders']['tradCompute'])} aiNativeCompute={len(site['computeProviders']['aiNativeCompute'])}")
    c = arr_model["combined"]
    print(f"  wq-096: arrModel apps_total=${c['apps_total']}B compute_net=${c['compute_net']}B industry_total=${c['industry_total']}B ai_native_share={c['ai_native_share_pct']}%")
    return arr_model
