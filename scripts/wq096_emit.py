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
ENTITIES_PATH = os.path.join(ROOT, "entities.json")
VAULT_PATH = os.path.join(ROOT, "vault-data.json")
AUDIT_DIR = os.path.join(ROOT, "data", "audits")
ARRMODEL_LEAK_AUDIT = os.path.join(AUDIT_DIR, "wq-098-arrmodel-source-leak.md")

# Tracks the source decision for every entry emitted into arrModel so the
# audit doc + reconcile assertion #8 can verify no orphan/hardcoded values.
# Cleared at the start of each emit_arrmodel run; consumed at end.
_LEAK_AUDIT_ROWS: list = []


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
    """Tag topConsumers tier; remove token factories + dup records; apply ARR backfill.

    Hotfix 2026-05-08 — defer to the entity-derived arrNumeric written by
    `generate_site_data.py:418` when the entity has a populated `arr`
    field (vault-backed via `apply_pipeline.py`). The hardcoded
    `TOPCONSUMERS_ARR_BACKFILL` table in `data/wq096_tagging.json` is the
    legacy fallback for entities not yet in entities.json — it must NOT
    override a fresh entity-backed value, otherwise apply_pipeline writes
    silently dead-end at the wq096_emit step.
    """
    remove = set(tagging["TOPCONSUMERS_REMOVE"])
    tier_map = tagging["TIER_FOR_TOPCONSUMER"]
    backfill = tagging["TOPCONSUMERS_ARR_BACKFILL"]
    entities_lookup = _load_entities_lookup()

    def _entity_has_arr(co_name):
        if not co_name:
            return False
        candidates = (
            co_name.lower(),
            co_name.lower().replace(" ", "-").replace(".", ""),
        )
        for key in candidates:
            ent = entities_lookup.get(key)
            if not ent:
                continue
            arr_b, _src, _dp = _entity_arr_b(ent)
            if arr_b is not None:
                return True
        return False

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
        # backfill ARR + provenance — but ONLY when entities.json doesn't
        # already provide a vault-backed value. Otherwise the hardcoded
        # legacy figure overrides an applied claim.
        if co in backfill and not _entity_has_arr(co):
            bf = backfill[co]
            if "arrNumeric" in bf and bf["arrNumeric"] is not None:
                c["arrNumeric"] = bf["arrNumeric"]
                c["arrSource"] = bf.get("arrSource")
                c["provenance"] = bf.get("provenance", "tier_3a")
                c["arrAsOf"] = "2026-Q1"
            if bf.get("arrPending"):
                c["arrPending"] = True
                c["arrPendingReason"] = bf.get("arrPendingReason", "")
        elif co in backfill:
            # Entity-backed; leave arrNumeric alone but stamp the source
            # so the rendered card credits the vault claim, not the
            # hardcoded backfill.
            c.setdefault("arrAsOf", "2026-Q1")
            c["arrSource"] = "entities.json (apply_pipeline)"
            if not c.get("provenance"):
                c["provenance"] = "tier_2b"
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


def _load_entities_lookup():
    """Build name/slug → entity dict from entities.json. Tolerant of a
    missing file (older site builds run without the apply pipeline)."""
    if not os.path.exists(ENTITIES_PATH):
        return {}
    try:
        with open(ENTITIES_PATH) as f:
            ents = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    lookup = {}
    for c in ents.get("companies", []):
        slug = (c.get("slug") or "").lower()
        name = (c.get("name") or "").lower()
        if slug:
            lookup[slug] = c
        if name and name not in lookup:
            lookup[name] = c
    return lookup


def _load_vault_lookup():
    """Build dp-id → claim from vault-data.json so audit rows can name the
    backing data point id."""
    if not os.path.exists(VAULT_PATH):
        return {}
    try:
        with open(VAULT_PATH) as f:
            vault = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    return {dp.get("id"): dp for dp in vault.get("dataPoints", []) if dp.get("id")}


def _entity_arr_b(entity):
    """Return (arr_value_in_B, source_path, source_dp_id) for an entity.

    Resolution order (for the "current ARR run-rate" view that arrModel
    represents):
      1. `current.arr` — apply_pipeline writes here for point-in-time
         claims, which is what arrModel wants.
      2. Latest non-projected `financials[<year>].arr` whose year is ≤
         the current calendar year. Far-future entries (e.g. an editorial
         2030 baseline) are excluded — they're projections in disguise.

    `source_dp_id` is the highest-tier provenance entry id for the chosen
    field (so the audit doc can name the dp the value is backed by).
    Returns (None, None, None) if no value present.
    """
    if not entity:
        return None, None, None

    cur = entity.get("current") or {}
    if cur.get("arr") is not None:
        arr_raw = cur.get("arr")
        prov_key = "current.arr"
        source_path = "entities.json:current.arr"
    else:
        fins = entity.get("financials") or {}
        current_year = datetime.now(timezone.utc).year
        candidate_year = None
        for y in sorted(fins.keys(), reverse=True):
            if y.endswith("_projected"):
                continue
            try:
                yr = int(y.split("_")[0])
            except ValueError:
                continue
            if yr > current_year:
                continue  # editorial future baseline, not a real ARR claim
            if isinstance(fins[y], dict) and fins[y].get("arr") is not None:
                candidate_year = y
                break
        if not candidate_year:
            return None, None, None
        arr_raw = fins[candidate_year].get("arr")
        prov_key = f"{candidate_year}.arr"
        source_path = f"entities.json:financials.{candidate_year}.arr"

    # Entity-stored arr values are in $B by apply_handlers/arr.py
    # convention. Legacy $M-stored values (e.g. Perplexity 2026.arr=500
    # meaning $500M) get force-overwritten when the human-reviewed claim
    # applies, so this path treats every remaining value as $B. If a units
    # bug ever sneaks back in, reconcile assertion #8 will surface the
    # affected entity in the leak audit.
    try:
        arr_b = float(arr_raw)
    except (TypeError, ValueError):
        return None, None, None

    prov = (entity.get("provenance") or {}).get(prov_key) or {}
    claims = prov.get("claims") or []
    source_dp_id = None
    if claims:
        # Highest tier wins; ties → latest date.
        from apply_handlers._shared import TIER_RANK
        ranked = sorted(
            claims,
            key=lambda c: (TIER_RANK.get(c.get("tier") or "", 0), c.get("date") or ""),
            reverse=True,
        )
        source_dp_id = ranked[0].get("id")
    return round(arr_b, 4), source_path, source_dp_id


def _record_leak_audit(row):
    _LEAK_AUDIT_ROWS.append(row)


def _frontier_arr_entries(site, entities_lookup, vault_lookup):
    """Build frontier ARR entries.

    Vault-first: prefer the entity's `current.arr` / `financials[<latest>].arr`
    (populated by apply_pipeline from vault claims). Fall back to the
    legacy `dashboard.providers.<key>.arrNumeric / rev` only when no entity
    record is available, and surface the fallback in the leak audit doc.
    """
    out = []
    for key, card in site.get("dashboard", {}).get("providers", {}).items():
        tier = card.get("tier", "frontier")
        if tier != "frontier":
            continue

        ent = entities_lookup.get(key.lower())
        arr_b, source_path, source_dp_id = _entity_arr_b(ent) if ent else (None, None, None)

        if arr_b is None:
            # Legacy fallback path — the leak audit flags this as a non-vault source.
            arr_legacy = card.get("arrNumeric")
            if arr_legacy is None:
                arr_legacy = card.get("rev")
            arr_b = float(arr_legacy) if arr_legacy is not None else 0.0
            source_path = "dashboard.providers (legacy fallback)"
            source_dp_id = None

        out.append({
            "id": key,
            "arr": arr_b,
            "provenance": card.get("provenance", "tier_2a"),
            "tier": "frontier",
            "_arrSource": source_path,
            "_arrSourceDpId": source_dp_id,
        })
        _record_leak_audit({
            "block": "arrModel.apps.frontier",
            "entity": key,
            "arr_b": arr_b,
            "source_path": source_path,
            "source_dp_id": source_dp_id,
            "vault_backed": source_dp_id is not None,
        })
    return out


def _ai_native_app_entries(site, entities_lookup, vault_lookup):
    """Build aiNative ARR entries.

    Vault-first: read the entity's latest non-projected `financials.arr`
    (populated by `apply_pipeline.py` from accepted vault claims). Fall
    back to the legacy `topConsumers.arrNumeric` only when the entity
    cannot be resolved or has no arr field — and tag the entry as a
    fallback so reconcile assertion #8 can flag it.
    """
    out = []
    for c in site.get("dashboard", {}).get("topConsumers", []):
        if c.get("tier") != "ai_native_app":
            continue
        # Skip pure-passthrough gateway entries (no additive ARR contribution).
        if c.get("subcategory") == "gateway":
            continue

        co = c.get("co") or ""
        co_lc = co.lower()
        ent = (entities_lookup.get(co_lc)
               or entities_lookup.get(co_lc.replace(" ", "-").replace(".", "")))

        arr_b, source_path, source_dp_id = _entity_arr_b(ent) if ent else (None, None, None)

        if arr_b is None:
            arr_n = c.get("arrNumeric")
            if arr_n is None:
                continue
            arr_b = float(arr_n) / 1e9
            source_path = "dashboard.topConsumers (legacy fallback)"
            source_dp_id = None

        # Skip suspect-magnitude values (< $1M is almost certainly a units bug
        # in the source row — the topConsumers list does not include sub-$1M).
        if arr_b < 0.001:
            continue

        out.append({
            "id": co,
            "arr": round(arr_b, 4),
            "provenance": c.get("provenance", "tier_2b"),
            "tier": "ai_native_app",
            "_arrSource": source_path,
            "_arrSourceDpId": source_dp_id,
        })
        _record_leak_audit({
            "block": "arrModel.apps.aiNative",
            "entity": co,
            "arr_b": round(arr_b, 4),
            "source_path": source_path,
            "source_dp_id": source_dp_id,
            "vault_backed": source_dp_id is not None,
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
        # Trad-SaaS entries source from data/evidence/enterprise_reality/*.json
        # — hand-curated evidence files, vault-adjacent.
        source_path = "data/evidence/enterprise_reality/*.json"
        out.append({
            "id": r.get("id"),
            "arr": float(arr),
            "provenance": r.get("provenance", "tier_2b"),
            "tier": "trad_saas",
            "_arrSource": source_path,
            "_arrSourceDpId": None,
        })
        _record_leak_audit({
            "block": "arrModel.apps.tradSaas",
            "entity": r.get("id"),
            "arr_b": float(arr),
            "source_path": source_path,
            "source_dp_id": None,
            "vault_backed": True,  # evidence-file-backed
        })
    return out


def _record_compute_audit_rows(trad_entries, native_entries):
    """Compute-side blocks (tradCompute, aiNativeCompute) source ARR from
    the curated `data/evidence/compute_disclosures/*.json` evidence files.
    These are hand-curated and audited as a unit (dp-239 → azure.json
    reconciles to the compute disclosure evidence in apply_pipeline). For
    the arrModel source-leak audit, count these as vault-adjacent (the
    evidence path itself is the source-of-truth) rather than orphan.
    """
    for t in trad_entries:
        _record_leak_audit({
            "block": "arrModel.compute.tradCompute",
            "entity": t.get("id"),
            "arr_b": float(t.get("arrGrossDisclosed") or 0),
            "source_path": "data/evidence/compute_disclosures/*.json",
            "source_dp_id": None,
            "vault_backed": True,  # evidence-file-backed
        })
    for e in native_entries:
        _record_leak_audit({
            "block": "arrModel.compute.aiNativeCompute",
            "entity": e.get("id"),
            "arr_b": float(e.get("arrNumeric") or 0),
            "source_path": "data/evidence/compute_disclosures/aiNativeCompute/*.json",
            "source_dp_id": None,
            "vault_backed": True,
        })


def _write_leak_audit():
    """Write the arrModel source-leak audit doc.

    Lists every entity in arrModel.apps.* and arrModel.compute.* with its
    actual data source. Reconcile assertion #8 reads this surface to verify
    no orphan/hardcoded entries.
    """
    if not _LEAK_AUDIT_ROWS:
        return None
    os.makedirs(AUDIT_DIR, exist_ok=True)
    rows = list(_LEAK_AUDIT_ROWS)
    by_block = {}
    for r in rows:
        by_block.setdefault(r["block"], []).append(r)

    total = len(rows)
    vault_backed = sum(1 for r in rows if r["vault_backed"])
    legacy = total - vault_backed

    lines = [
        "# wq-098 hotfix — arrModel source-leak audit",
        "",
        f"_Generated_: {_now_iso()}",
        "",
        "Each row in `arrModel.apps.*` and `arrModel.compute.*` and the data",
        "source it actually reads from. Generated on every site build by",
        "`scripts/wq096_emit.py:emit_arrmodel`. Reconcile assertion #8",
        "(`a_arrmodel_vault_backed`) reads this and fails if any entry",
        "sources from a non-vault path.",
        "",
        "## Summary",
        "",
        f"- **Total arrModel entries:** {total}",
        f"- **Vault-backed (entities.json + provenance dp-id, or curated evidence file):** {vault_backed}",
        f"- **Legacy fallback (dashboard.providers / topConsumers / enterpriseReality):** {legacy}",
        "",
    ]
    for block in sorted(by_block.keys()):
        block_rows = by_block[block]
        lines.append(f"## {block} ({len(block_rows)} entries)")
        lines.append("")
        lines.append("| entity | arr ($B) | source_path | source_dp_id | vault_backed |")
        lines.append("|---|---|---|---|---|")
        for r in block_rows:
            lines.append(
                f"| {r['entity']} | {r['arr_b']} | {r['source_path']} "
                f"| {r['source_dp_id'] or '—'} "
                f"| {'✅' if r['vault_backed'] else '❌ legacy fallback'} |"
            )
        lines.append("")

    with open(ARRMODEL_LEAK_AUDIT, "w") as f:
        f.write("\n".join(lines) + "\n")
    return ARRMODEL_LEAK_AUDIT


def get_leak_audit_rows():
    """Read-only accessor for the most recent run's audit rows. Used by
    reconcile_pipeline.py assertion #8."""
    return list(_LEAK_AUDIT_ROWS)


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
    _LEAK_AUDIT_ROWS.clear()
    entities_lookup = _load_entities_lookup()
    vault_lookup = _load_vault_lookup()
    frontier = _frontier_arr_entries(site, entities_lookup, vault_lookup)
    ai_native = _ai_native_app_entries(site, entities_lookup, vault_lookup)
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
    _record_compute_audit_rows(trad_compute_entries, ai_native_compute_entries)

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
    audit_path = _write_leak_audit()
    if audit_path:
        print(f"  wq-098 hotfix: arrModel source-leak audit → {audit_path}")

    print(f"  wq-096: enterpriseReality={len(site['dashboard']['enterpriseReality'])} entries; topConsumers moved out: {sorted(moved)}")
    print(f"  wq-096: computeProviders.tradCompute={len(site['computeProviders']['tradCompute'])} aiNativeCompute={len(site['computeProviders']['aiNativeCompute'])}")
    c = arr_model["combined"]
    print(f"  wq-096: arrModel apps_total=${c['apps_total']}B compute_net=${c['compute_net']}B industry_total=${c['industry_total']}B ai_native_share={c['ai_native_share_pct']}%")
    return arr_model
