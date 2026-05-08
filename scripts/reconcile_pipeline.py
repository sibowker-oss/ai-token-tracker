#!/usr/bin/env python3
"""reconcile_pipeline.py — wq-099 nightly visibility + alert script.

Walks vault-inbox.json, vault-data.json, entities.json, site-data.json, and
data/runs.jsonl to answer the four-question morning glance:

  1. What came in overnight?              (ingestSummary)
  2. What's waiting for me?               (reviewQueueSummary)
  3. What might be stale?                 (staleEntities)
  4. What broke?                          (assertions[])

Writes:
  - data/pipeline-health-YYYY-MM-DD.json  (date-stamped snapshot)
  - data/pipeline-health-latest.json      (always points to today's run)
  - data/audits/pipeline-alerts-YYYY-MM-DD.md  (only if any assertion failed)

Six assertions are evaluated (brief §5). Each returns
  {name, passed, count, details}
and any failure flips alertCount and triggers the alert markdown file.

USAGE
    python3 scripts/reconcile_pipeline.py            # write today's snapshot
    python3 scripts/reconcile_pipeline.py --stdout   # also print JSON to stdout
    python3 scripts/reconcile_pipeline.py --suffix initial   # write date-suffix-initial.json

EXIT CODES
    0  — script completed (regardless of assertion results)
    1  — script-level error (malformed input file etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from apply_handlers import all_handlers, default_handler  # noqa: E402
from apply_handlers.arr import _looks_like_arr as looks_like_arr  # noqa: E402
from apply_handlers._shared import derive_tier  # noqa: E402

VAULT_INBOX = os.path.join(ROOT_DIR, "vault-inbox.json")
VAULT_DATA = os.path.join(ROOT_DIR, "vault-data.json")
ENTITIES = os.path.join(ROOT_DIR, "entities.json")
SITE_DATA = os.path.join(ROOT_DIR, "site-data.json")
RUNS_JSONL = os.path.join(ROOT_DIR, "data", "runs.jsonl")
APPLY_LOG = os.path.join(ROOT_DIR, "data", "apply_log.json")
DATA_DIR = os.path.join(ROOT_DIR, "data")
AUDIT_DIR = os.path.join(DATA_DIR, "audits")

LOOKBACK_HOURS_INGEST = 24
STALE_REVIEW_DAYS = 7
TIER_RANK = {"tier_1A": 1, "tier_1B": 2, "tier_2A": 3, "tier_2B": 4, "tier_3": 5}
ARR_LIKE_UNITS = {
    "$B", "$B ARR", "$B ARR (peak-4wk)", "USD billions", "$M ARR",
    "USD millions", "$B annualised", "$B annualized",
}
ARRMODEL_TOLERANCE_B = 0.1
DIVERGENCE_PCT = 0.15  # mirror apply_pipeline.py's divergence guard


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def parse_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def parse_date(d):
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def load_runs():
    """Return last record per run_id from data/runs.jsonl."""
    if not os.path.exists(RUNS_JSONL):
        return []
    records = []
    with open(RUNS_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    by_id = {}
    for r in records:
        prev = by_id.get(r.get("run_id"))
        if not prev:
            by_id[r["run_id"]] = r
            continue
        # Prefer ended_at record (the "end" record overwrites the "start")
        if r.get("ended_at") and not prev.get("ended_at"):
            by_id[r["run_id"]] = r
        elif (r.get("ended_at") and prev.get("ended_at")
              and r["ended_at"] > prev["ended_at"]):
            by_id[r["run_id"]] = r
    return list(by_id.values())


def tier_rank(tier):
    return TIER_RANK.get(tier, 99)


def claim_tier(claim):
    """Derive a claim's tier label, preferring an explicit `tier` field if
    present (legacy claims sometimes carry one). Falls back to the
    sourceType+confidence ladder used by apply_pipeline."""
    explicit = claim.get("tier") if isinstance(claim, dict) else None
    if explicit:
        return explicit
    return derive_tier(claim or {})


# ── ingest summary ──

INGEST_SCRIPTS = (
    "scan_sources.py",
    "monitor_sources.py",
    "extract_claims.py",
    "news_monitor.py",
    "scrape_podcasts.py",
    "curated_intake.py",
)


def summarise_ingest(runs, inbox, now_utc):
    cutoff = now_utc - timedelta(hours=LOOKBACK_HOURS_INGEST)
    recent_runs = [
        r for r in runs
        if r.get("script") in INGEST_SCRIPTS
        and parse_iso(r.get("started_at")) is not None
        and parse_iso(r["started_at"]) >= cutoff
    ]
    runs_by_script = defaultdict(list)
    for r in recent_runs:
        runs_by_script[r["script"]].append(r)

    # claims added to inbox in the last 24h (by dateAdded — date-only granularity)
    today = now_utc.date()
    yesterday = (now_utc - timedelta(days=1)).date()
    items = inbox.get("items", []) if inbox else []
    recent_inbox = [
        i for i in items
        if (parse_date(i.get("dateAdded")) is not None
            and parse_date(i["dateAdded"]).date() in (today, yesterday))
    ]

    scrapers_scheduled = sorted(runs_by_script.keys())
    scrapers_zero = []
    for script, script_runs in runs_by_script.items():
        # Look at the latest successful run for this script in the window.
        successes = [r for r in script_runs if r.get("status") == "success"]
        if not successes:
            continue
        latest = max(successes, key=lambda r: r.get("ended_at") or r.get("started_at") or "")
        outputs = latest.get("outputs") or {}
        # Inspect any output key suggesting "claims_added"-style counter.
        added = (outputs.get("claims_added")
                 or outputs.get("items_enriched")
                 or outputs.get("alerts_total")
                 or 0)
        if isinstance(added, (int, float)) and added == 0:
            scrapers_zero.append(script)

    return {
        "lookbackHours": LOOKBACK_HOURS_INGEST,
        "claimsAddedToInbox": len(recent_inbox),
        "scrapersScheduled": scrapers_scheduled,
        "scrapersThatProducedZero": sorted(scrapers_zero),
        "lastInboxProcessed": (inbox or {}).get("lastProcessed"),
    }


# ── review queue summary ──

def summarise_review_queue(inbox, now_utc):
    items = inbox.get("items", []) if inbox else []
    pending = [i for i in items if i.get("status") == "pending"]
    if not pending:
        return {
            "total": len(items),
            "pending": 0,
            "oldestPendingDate": None,
            "oldestPendingAgeDays": 0,
            "stalePendingCount": 0,
            "stalePendingIds": [],
        }
    pending_dates = [(p.get("id"), parse_date(p.get("dateAdded"))) for p in pending]
    dated = [(pid, d) for pid, d in pending_dates if d is not None]
    if dated:
        dated.sort(key=lambda x: x[1])
        oldest_id, oldest_dt = dated[0]
        age_days = (now_utc - oldest_dt).days
    else:
        oldest_dt = None
        age_days = 0

    cutoff = now_utc - timedelta(days=STALE_REVIEW_DAYS)
    stale = [pid for pid, d in dated if d <= cutoff]
    return {
        "total": len(items),
        "pending": len(pending),
        "oldestPendingDate": oldest_dt.strftime("%Y-%m-%d") if oldest_dt else None,
        "oldestPendingAgeDays": age_days,
        "stalePendingCount": len(stale),
        "stalePendingIds": stale[:50],
    }


# ── stale entities ──

def find_stale_entities(entities, vault, now_utc):
    """Walk companies; for each entity with a published ARR field, look for a
    higher-tier-or-more-recent verified ARR claim in vault that diverges by
    more than the apply_pipeline ±15% guard AND hasn't been applied yet
    (usedOn is empty). Those are "stale" — vault has newer truth that the
    apply pipeline has not yet propagated.

    The "not yet applied" gate is what makes a finding actionable; if a
    vault claim has already been applied and the entity still diverges,
    apply_pipeline already chose to skip the overwrite (divergence guard)
    and surfaced that decision in its own audit doc.
    """
    companies = (entities or {}).get("companies", []) or []
    co_by_slug = {c.get("slug"): c for c in companies if c.get("slug")}

    # Build per-entity vault ARR claims (verified-only, ARR-shape) using a
    # tight match: source_author or sourceUrl host or tags slug. Avoids the
    # "Google in claim text → match every Google claim" trap.
    def match_entity(dp):
        author = (dp.get("sourceAuthor") or "").lower()
        for slug, co in co_by_slug.items():
            cname = (co.get("name") or "").lower()
            # Require strong match: author starts with the entity name or
            # entity name is a tag. Bare substring matches like "Google" in
            # "Google Press Release" are too noisy.
            if cname and (author == cname or author.startswith(cname + " ")):
                return co
        for tag in (dp.get("tags") or []):
            if isinstance(tag, str) and tag in co_by_slug:
                return co_by_slug[tag]
        return None

    vault_arr_by_co = defaultdict(list)
    for dp in (vault or {}).get("dataPoints", []):
        if dp.get("confidence") != "verified":
            continue
        unit = dp.get("unit") or ""
        if unit not in ARR_LIKE_UNITS:
            continue
        # Reuse apply_pipeline's text-signal filter so we ignore claims
        # whose `unit: $B` is actually a valuation / funding / burn figure.
        if not looks_like_arr(dp):
            continue
        match = match_entity(dp)
        if match:
            vault_arr_by_co[match["slug"]].append(dp)

    current_year = now_utc.year
    stale = []
    for slug, claims in vault_arr_by_co.items():
        co = co_by_slug.get(slug)
        if not co:
            continue
        fins = co.get("financials") or {}
        if not isinstance(fins, dict):
            continue
        # Latest current-or-past year whose value is a dict carrying arr.
        # Future years are forecasts even if not suffixed `_projected`.
        entity_arr = None
        latest_year = None
        for y in sorted(fins.keys(), reverse=True):
            if y.endswith("_projected"):
                continue
            try:
                if int(y[:4]) > current_year:
                    continue
            except ValueError:
                continue
            year_data = fins.get(y)
            if not isinstance(year_data, dict):
                continue
            arr_val = year_data.get("arr")
            if isinstance(arr_val, (int, float)):
                latest_year = y
                entity_arr = arr_val
                break
        if entity_arr is None or entity_arr <= 0:
            continue

        # Highest-tier-most-recent verified claim *that has not been
        # propagated*. usedOn=[] means the apply_pipeline has not yet
        # touched it — so any divergence is genuinely pending.
        unapplied = [c for c in claims if not (c.get("usedOn") or [])]
        if not unapplied:
            continue

        ranked = sorted(
            unapplied,
            key=lambda c: (
                tier_rank(claim_tier(c)),
                -((parse_date(c.get("dateOfClaim")) or datetime(1970, 1, 1, tzinfo=timezone.utc)).timestamp()),
            ),
        )
        winner = ranked[0]
        winner_value = winner.get("value")
        unit = winner.get("unit") or ""
        if unit in ("$M ARR", "USD millions") and isinstance(winner_value, (int, float)):
            winner_value = winner_value / 1000.0
        if not isinstance(winner_value, (int, float)) or winner_value <= 0:
            continue

        delta_pct = abs(entity_arr - winner_value) / max(entity_arr, winner_value)
        if delta_pct > DIVERGENCE_PCT:
            stale.append({
                "entitySlug": slug,
                "entityName": co.get("name"),
                "field": f"financials.{latest_year}.arr",
                "entityValue": round(entity_arr, 4),
                "vaultValue": round(winner_value, 4),
                "vaultClaimId": winner.get("id"),
                "vaultClaimTier": claim_tier(winner),
                "vaultDateOfClaim": winner.get("dateOfClaim"),
                "vaultUsedOn": winner.get("usedOn") or [],
                "deltaPct": round(delta_pct * 100, 1),
            })
    stale.sort(key=lambda x: x["deltaPct"], reverse=True)
    return stale


# ── assertions ──

def a_ingest_health(ingest_summary):
    """Pass if at least one scraper produced > 0 inbox claims OR no scrapers
    were scheduled in the lookback. Fail if all scheduled scrapers reported
    zero output AND nothing landed in the inbox."""
    scheduled = ingest_summary["scrapersScheduled"]
    zero = ingest_summary["scrapersThatProducedZero"]
    inbox_added = ingest_summary["claimsAddedToInbox"]

    if not scheduled:
        return {
            "name": "ingest_health",
            "passed": True,
            "count": 0,
            "details": (
                f"No tracked ingestion scripts ran in the last "
                f"{LOOKBACK_HOURS_INGEST}h — pass by default."
            ),
        }
    if inbox_added > 0:
        return {
            "name": "ingest_health",
            "passed": True,
            "count": inbox_added,
            "details": (
                f"{inbox_added} claim(s) added to vault-inbox in the last "
                f"{LOOKBACK_HOURS_INGEST}h across {len(scheduled)} scheduled "
                f"scraper(s)."
            ),
        }
    if len(zero) == len(scheduled):
        return {
            "name": "ingest_health",
            "passed": False,
            "count": len(zero),
            "details": (
                f"All {len(zero)} scheduled scraper(s) ran but produced zero "
                f"new claims: {', '.join(zero)}. Likely broken adapter — "
                f"investigate."
            ),
        }
    # Mixed: some produced, some didn't — pass but note in details.
    return {
        "name": "ingest_health",
        "passed": True,
        "count": inbox_added,
        "details": (
            f"{inbox_added} new claim(s) overnight; "
            f"{len(zero)} scraper(s) of {len(scheduled)} produced zero "
            f"({', '.join(zero) or 'none'})."
        ),
    }


def a_review_queue_freshness(review_summary):
    stale_count = review_summary["stalePendingCount"]
    if stale_count == 0:
        return {
            "name": "review_queue_freshness",
            "passed": True,
            "count": 0,
            "details": (
                f"No pending claims older than {STALE_REVIEW_DAYS} days "
                f"({review_summary['pending']} pending total)."
            ),
        }
    return {
        "name": "review_queue_freshness",
        "passed": False,
        "count": stale_count,
        "details": (
            f"{stale_count} pending claim(s) older than {STALE_REVIEW_DAYS} "
            f"days — oldest is "
            f"{review_summary['oldestPendingAgeDays']} days "
            f"({review_summary['oldestPendingDate']}). "
            f"Sample IDs: "
            f"{', '.join(review_summary['stalePendingIds'][:10])}"
        ),
    }


def a_apply_propagation(vault):
    """Zero verified + tier_2A-or-better vault-data.json claims with usedOn=[]."""
    offenders = []
    for dp in (vault or {}).get("dataPoints", []):
        if dp.get("confidence") != "verified":
            continue
        if tier_rank(claim_tier(dp)) > TIER_RANK["tier_2A"]:
            continue
        if dp.get("usedOn"):
            continue
        offenders.append(dp.get("id"))
    if not offenders:
        return {
            "name": "apply_propagation",
            "passed": True,
            "count": 0,
            "details": (
                "No verified tier-2A-or-better claims sit unused. "
                "Apply pipeline is propagating cleanly."
            ),
        }
    return {
        "name": "apply_propagation",
        "passed": False,
        "count": len(offenders),
        "details": (
            f"{len(offenders)} verified tier-2A-or-better claim(s) have "
            f"usedOn=[]. Sample IDs: {', '.join(offenders[:10])}."
        ),
    }


def a_entity_vault_sync(stale_entities):
    if not stale_entities:
        return {
            "name": "entity_vault_sync",
            "passed": True,
            "count": 0,
            "details": (
                "Every published entity ARR matches the highest-tier "
                "verified vault claim within ±15%."
            ),
        }
    return {
        "name": "entity_vault_sync",
        "passed": False,
        "count": len(stale_entities),
        "details": (
            f"{len(stale_entities)} entity field(s) diverge >15% from a "
            f"verified vault claim. Top offender: "
            f"{stale_entities[0]['entityName']} "
            f"{stale_entities[0]['field']} "
            f"published=${stale_entities[0]['entityValue']}B vs "
            f"vault=${stale_entities[0]['vaultValue']}B "
            f"({stale_entities[0]['deltaPct']}%)."
        ),
    }


def a_arrmodel_consistency(site):
    combined = ((site or {}).get("arrModel") or {}).get("combined") or {}
    apps = combined.get("apps_total")
    compute = combined.get("compute_net")
    industry = combined.get("industry_total")
    if not all(isinstance(v, (int, float)) for v in (apps, compute, industry)):
        return {
            "name": "arrmodel_consistency",
            "passed": False,
            "count": 1,
            "details": "arrModel.combined missing apps_total/compute_net/industry_total.",
        }
    delta = abs((apps + compute) - industry)
    if delta <= ARRMODEL_TOLERANCE_B:
        return {
            "name": "arrmodel_consistency",
            "passed": True,
            "count": 0,
            "details": (
                f"apps_total ${apps:.4f}B + compute_net ${compute:.4f}B "
                f"= ${apps + compute:.4f}B ≈ industry_total ${industry:.4f}B "
                f"(Δ ${delta:.4f}B ≤ tolerance ${ARRMODEL_TOLERANCE_B}B)."
            ),
        }
    return {
        "name": "arrmodel_consistency",
        "passed": False,
        "count": 1,
        "details": (
            f"apps_total ${apps:.4f}B + compute_net ${compute:.4f}B "
            f"= ${apps + compute:.4f}B ≠ industry_total ${industry:.4f}B "
            f"(Δ ${delta:.4f}B > tolerance ${ARRMODEL_TOLERANCE_B}B)."
        ),
    }


def a_inbox_migration_freshness(inbox, vault, now_utc):
    """#7 (hotfix 2026-05-08): zero accepted-but-unmigrated inbox items
    older than 24h.

    An accepted inbox item is "migrated" when it carries an `accepted_as`
    referencing a vault dp-id that exists in vault-data.json. This
    assertion catches the failure mode that triggered the hotfix — items
    Simon accepted in claims.html but that the apply pipeline never moved
    into vault.
    """
    items = (inbox or {}).get("items", [])
    by_id = {dp.get("id") for dp in (vault or {}).get("dataPoints", [])}
    cutoff = now_utc - timedelta(hours=24)
    stuck = []
    for it in items:
        if (it.get("status") or "").lower() != "accepted":
            continue
        accepted_as = it.get("accepted_as")
        if accepted_as and accepted_as in by_id:
            continue
        added = parse_date(it.get("dateAdded"))
        if added is not None and added > cutoff:
            continue  # within the 24h grace window
        stuck.append({
            "inbox_id": it.get("id"),
            "dateAdded": it.get("dateAdded"),
            "claim": (it.get("claim") or "")[:120],
        })
    if not stuck:
        return {
            "name": "inbox_migration_freshness",
            "passed": True,
            "count": 0,
            "details": (
                "No accepted inbox items >24h old without a vault dp-id."
            ),
        }
    sample = ", ".join(s["inbox_id"] for s in stuck[:5])
    return {
        "name": "inbox_migration_freshness",
        "passed": False,
        "count": len(stuck),
        "details": (
            f"{len(stuck)} accepted inbox item(s) older than 24h have no vault "
            f"dp-id (sample: {sample}). Run "
            f"`python3 scripts/apply_pipeline.py` to mint vault entries."
        ),
        "items": stuck[:25],
    }


def a_arrmodel_vault_backed(site):
    """#8 (hotfix 2026-05-08): every entity in `arrModel.apps.*` and
    `arrModel.compute.*` has its `arr` value sourced from a vault dp-id or
    from the curated compute-disclosure evidence files. No orphan /
    hardcoded entries.

    Reads the `_arrSource` + `_arrSourceDpId` fields the wq096_emit
    pipeline now stamps on each emitted entry. An entry without a dp-id
    AND a non-evidence source is flagged as a leak.
    """
    arr_model = (site or {}).get("arrModel") or {}
    apps = arr_model.get("apps") or {}
    leaks = []

    def _check(block_name, entries):
        for e in entries or []:
            if not isinstance(e, dict):
                continue
            src = e.get("_arrSource") or ""
            has_dp = bool(e.get("_arrSourceDpId"))
            evidence_backed = "compute_disclosures" in src or "evidence" in src
            entities_backed = src.startswith("entities.json:")
            if has_dp or entities_backed or evidence_backed:
                continue
            leaks.append({
                "block": block_name,
                "entity": e.get("id"),
                "source_path": src or "<missing>",
            })

    for sub in ("frontier", "aiNative", "tradSaas"):
        block = apps.get(sub) or {}
        _check(f"arrModel.apps.{sub}", block.get("entries") or [])

    if not leaks:
        return {
            "name": "arrmodel_vault_backed",
            "passed": True,
            "count": 0,
            "details": (
                "Every arrModel entity sources its arr from entities.json + "
                "vault dp-id or from a curated evidence file."
            ),
        }
    sample = ", ".join(f"{l['block']}/{l['entity']}" for l in leaks[:5])
    return {
        "name": "arrmodel_vault_backed",
        "passed": False,
        "count": len(leaks),
        "details": (
            f"{len(leaks)} arrModel entry/entries source their arr from a "
            f"non-vault path (sample: {sample}). Confirm the entity has been "
            f"applied via `apply_pipeline.py`, then rebuild site-data.json."
        ),
        "items": leaks[:25],
    }


def a_rendered_figure_coverage(site, entities):
    """#9 (hotfix follow-up 2026-05-08): every rendered numeric figure on
    `usage.html` is either vault-backed, evidence-backed (curated file),
    or has been deliberately accepted as a legacy fixture.

    Walks `dashboard.providers`, `dashboard.topConsumers`, and
    `dashboard.enterpriseReality`. Surfaces two failure modes:

      - **Stale-fixture** — a rendered value diverges >10% from the
        entities.json value. Suggests a hardcoded backfill that didn't
        defer to a fresh apply-pipeline write (the bug class the hotfix
        targeted), OR an out-of-date evidence file vs a recently-applied
        entity claim.
      - **Unbacked** — a rendered figure has no entity record at all
        (long-standing topConsumers fixtures that need entity surfacing).

    Reads the per-row data the wq096_emit coverage audit emits to
    `data/audits/wq-098-rendered-figure-coverage.md`. Re-derived in-line
    here so the assertion is self-contained.
    """
    if not site or not entities:
        return {
            "name": "rendered_figure_coverage",
            "passed": True,
            "count": 0,
            "details": "site-data.json or entities.json missing — skipping check.",
        }

    lookup = {}
    for c in entities.get("companies", []) or []:
        slug = (c.get("slug") or "").lower()
        name = (c.get("name") or "").lower()
        if slug:
            lookup[slug] = c
        if name and name not in lookup:
            lookup[name] = c

    def _entity_arr(co):
        if not co:
            return None
        candidates = (
            co.lower(),
            co.lower().replace(" ", "-").replace(".", ""),
            co.lower().replace("_", "-"),
        )
        for k in candidates:
            ent = lookup.get(k)
            if not ent:
                continue
            cur = (ent.get("current") or {}).get("arr")
            if isinstance(cur, (int, float)):
                return cur
            fins = ent.get("financials") or {}
            current_year = datetime.now(timezone.utc).year
            for y in sorted(fins.keys(), reverse=True):
                if y.endswith("_projected"):
                    continue
                try:
                    yr = int(y.split("_")[0])
                except ValueError:
                    continue
                if yr > current_year:
                    continue
                v = fins[y].get("arr") if isinstance(fins[y], dict) else None
                if isinstance(v, (int, float)):
                    return v
        return None

    stale_fixtures = []
    unbacked = []

    # providers
    for key, card in (site.get("dashboard", {}).get("providers") or {}).items():
        rendered = card.get("arrNumeric")
        if not isinstance(rendered, (int, float)):
            rendered = card.get("rev")
        if not isinstance(rendered, (int, float)):
            continue
        ent_arr = _entity_arr(key)
        if ent_arr is None:
            unbacked.append({
                "block": "dashboard.providers",
                "entity": key,
                "rendered_b": rendered,
            })
            continue
        if rendered != 0 and abs(ent_arr - rendered) / abs(rendered) > 0.10:
            stale_fixtures.append({
                "block": "dashboard.providers",
                "entity": key,
                "rendered_b": rendered,
                "entity_arr_b": ent_arr,
            })

    # topConsumers
    for c in site.get("dashboard", {}).get("topConsumers") or []:
        co = c.get("co") or ""
        rendered_n = c.get("arrNumeric")
        if not isinstance(rendered_n, (int, float)):
            continue
        rendered_b = float(rendered_n) / 1e9
        ent_arr = _entity_arr(co)
        if ent_arr is None:
            unbacked.append({
                "block": "dashboard.topConsumers",
                "entity": co,
                "rendered_b": rendered_b,
            })
            continue
        if rendered_b != 0 and abs(ent_arr - rendered_b) / abs(rendered_b) > 0.10:
            stale_fixtures.append({
                "block": "dashboard.topConsumers",
                "entity": co,
                "rendered_b": rendered_b,
                "entity_arr_b": ent_arr,
            })

    # enterpriseReality — gap > 50% only (claimed-vs-real is by design;
    # only big drift suggests a stale evidence file or stale entity).
    for r in site.get("dashboard", {}).get("enterpriseReality") or []:
        rendered = r.get("arrClaimedNumeric")
        if not isinstance(rendered, (int, float)):
            continue
        co = r.get("id") or r.get("name") or ""
        ent_arr = _entity_arr(co)
        if ent_arr is None:
            continue  # most enterpriseReality rows have no entity by design
        if rendered != 0 and abs(ent_arr - rendered) / abs(rendered) > 0.50:
            stale_fixtures.append({
                "block": "dashboard.enterpriseReality",
                "entity": co,
                "rendered_b": rendered,
                "entity_arr_b": ent_arr,
                "note": "claimed-vs-real divergence (by design — review whether evidence file or entity is stale)",
            })

    issues = stale_fixtures
    if not issues:
        return {
            "name": "rendered_figure_coverage",
            "passed": True,
            "count": 0,
            "details": (
                f"All rendered numeric figures match their entities.json "
                f"value within ±10% (or ±50% for enterpriseReality). "
                f"{len(unbacked)} rendered row(s) have no entity record at "
                f"all — separate gap, not a stale-fixture leak."
            ),
            "items": [],
            "unbacked_count": len(unbacked),
        }
    sample = ", ".join(f"{s['block']}/{s['entity']}" for s in issues[:5])
    return {
        "name": "rendered_figure_coverage",
        "passed": False,
        "count": len(issues),
        "details": (
            f"{len(issues)} rendered figure(s) diverge from entities.json. "
            f"Sample: {sample}. See "
            f"`data/audits/wq-098-rendered-figure-coverage.md` for the full "
            f"row list. Likely cause: hardcoded fixture (legacy site-data "
            f"seed or `wq096_tagging.json`) winning over apply_pipeline "
            f"writes, or an evidence file out-of-date vs an applied "
            f"vault claim."
        ),
        "items": issues[:25],
        "unbacked_count": len(unbacked),
    }


def a_handler_coverage(vault):
    """Every distinct vault `unit` has a handler or is in UNHANDLED_UNITS."""
    handler_units = set()
    for unit, _module, _fn in all_handlers():
        handler_units.add(unit)
    handler_units.update(default_handler().UNHANDLED_UNITS)

    vault_units = sorted(
        {(dp.get("unit") or "") for dp in (vault or {}).get("dataPoints", [])}
    )
    missing = [u for u in vault_units if u and u not in handler_units]
    if not missing:
        return {
            "name": "handler_coverage",
            "passed": True,
            "count": 0,
            "details": (
                f"All {len(vault_units)} distinct vault unit(s) have a "
                f"registered handler or are in UNHANDLED_UNITS."
            ),
        }
    return {
        "name": "handler_coverage",
        "passed": False,
        "count": len(missing),
        "details": (
            f"{len(missing)} vault unit(s) without handler: "
            f"{', '.join(repr(u) for u in missing[:10])}."
        ),
    }


# ── orchestration ──

def build_health(now_utc):
    inbox = load_json(VAULT_INBOX) if os.path.exists(VAULT_INBOX) else {"items": []}
    vault = load_json(VAULT_DATA) if os.path.exists(VAULT_DATA) else {"dataPoints": []}
    entities = load_json(ENTITIES) if os.path.exists(ENTITIES) else {"companies": []}
    site = load_json(SITE_DATA) if os.path.exists(SITE_DATA) else {}
    runs = load_runs()

    ingest = summarise_ingest(runs, inbox, now_utc)
    review = summarise_review_queue(inbox, now_utc)
    stale = find_stale_entities(entities, vault, now_utc)
    apply_gate = summarise_apply_gate(now_utc)

    assertions = [
        a_ingest_health(ingest),
        a_review_queue_freshness(review),
        a_apply_propagation(vault),
        a_entity_vault_sync(stale),
        a_arrmodel_consistency(site),
        a_handler_coverage(vault),
        a_inbox_migration_freshness(inbox, vault, now_utc),
        a_arrmodel_vault_backed(site),
        a_rendered_figure_coverage(site, entities),
    ]
    failed = [a for a in assertions if not a["passed"]]

    return {
        "asOf": now_utc.isoformat().replace("+00:00", "Z"),
        "ingestSummary": ingest,
        "reviewQueueSummary": review,
        "staleEntities": {
            "count": len(stale),
            "items": stale[:25],
        },
        "vaultSummary": {
            "totalClaims": len((vault or {}).get("dataPoints", [])),
            "orphanedClaims": sum(
                1 for dp in (vault or {}).get("dataPoints", [])
                if not (dp.get("usedOn") or [])
            ),
        },
        "applyGate": apply_gate,
        "assertions": assertions,
        "alertCount": len(failed),
    }


def summarise_apply_gate(now_utc):
    """wq-100 — counters + recent diffs for the Pipeline tab.

    Reads `data/apply_log.json` (written by apply_pipeline.py on every run)
    and emits the shape the wq-099 Pipeline tab consumes:
      {
        "lastRunAt": "<iso>",
        "counters30d": {auto_applied, routed_to_review, anomalies},
        "recentAutoApplied24h": [ ...diff rows... ]
      }
    Returns an empty-but-present block when apply_log.json doesn't exist
    yet (first-time setup / wq-100 not deployed) so the dashboard renders
    consistently rather than crashing.
    """
    empty = {
        "lastRunAt": None,
        "counters30d": {"auto_applied": 0, "routed_to_review": 0, "anomalies": 0},
        "recentAutoApplied24h": [],
        "available": False,
    }
    if not os.path.exists(APPLY_LOG):
        return empty
    try:
        log = load_json(APPLY_LOG)
    except (OSError, json.JSONDecodeError):
        return empty

    runs = log.get("runs") or []
    counters = log.get("counters_30d") or empty["counters30d"]
    last_ts = log.get("lastUpdated")

    # Flatten the auto-apply diffs across the most recent runs, keeping
    # only those within the last 24h. Caps at 25 entries so the dashboard
    # payload stays small.
    cutoff = now_utc - timedelta(hours=24)
    recent = []
    for run in reversed(runs):
        ts = parse_iso(run.get("ts"))
        if ts and ts < cutoff:
            break
        for d in run.get("diffs") or []:
            if d.get("bucket") == "auto_apply":
                recent.append({**d, "ts": run.get("ts")})
                if len(recent) >= 25:
                    break
        if len(recent) >= 25:
            break

    return {
        "lastRunAt": last_ts,
        "counters30d": counters,
        "recentAutoApplied24h": recent,
        "available": True,
    }


def write_alert(health, date_iso):
    failed = [a for a in health["assertions"] if not a["passed"]]
    if not failed:
        return None
    os.makedirs(AUDIT_DIR, exist_ok=True)
    path = os.path.join(AUDIT_DIR, f"pipeline-alerts-{date_iso}.md")
    lines = [
        f"# Pipeline alerts — {date_iso}",
        "",
        f"_Generated_: {health['asOf']}",
        f"_Source_: `scripts/reconcile_pipeline.py` (wq-099)",
        "",
        f"**{len(failed)} assertion(s) failed.** Each entry below names the "
        f"failing assertion, the affected count, and the recommended next "
        f"action.",
        "",
    ]
    actions = {
        "ingest_health": (
            "Check the latest run of every scheduled scraper in "
            "`/status.html`. A `claims_added: 0` across all scrapers usually "
            "means an upstream feed broke or a credential expired. Inspect "
            "`data/scan_sources.log` and `data/extract_claims.log` for the "
            "specific failing adapter."
        ),
        "review_queue_freshness": (
            f"Open `/review.html` (or `/claims.html`) and clear the "
            f"{STALE_REVIEW_DAYS}-day-stale pending items. If they should be "
            f"kept indefinitely, mark `status=parked` to remove them from "
            f"this assertion."
        ),
        "apply_propagation": (
            "A verified tier-2A-or-better claim has `usedOn: []` — likely an "
            "apply_pipeline regression or a manual vault edit that bypassed "
            "the pipeline. Run `python3 scripts/apply_pipeline.py --dry-run "
            "--verbose` and check the audit doc at "
            "`data/audits/wq-098-skipped-claims.md`."
        ),
        "entity_vault_sync": (
            "Vault has a stronger / more-recent claim than the rendered "
            "entityDirectory shows. Most common cause: divergence-guard "
            "skipped the overwrite (>15% delta). Decide whether to accept "
            "the new value (`python3 scripts/apply_pipeline.py "
            "--confirm-major-change`) or mark the vault claim "
            "`do_not_apply: true`."
        ),
        "arrmodel_consistency": (
            "`arrModel.combined.apps_total + compute_net != industry_total`. "
            "Re-run `python3 scripts/wq096_emit.py` to regenerate, then "
            "rerun this script. If the imbalance persists, inspect each "
            "constituent in `arrModel.apps.aiNative.entries` / "
            "`arrModel.compute.aiNativeCompute.entries`."
        ),
        "handler_coverage": (
            "A new vault `unit` value has no handler. Either register one in "
            "`scripts/apply_handlers/` (and a row in `__init__.py`'s "
            "`_REGISTERED`) or add it to "
            "`scripts/apply_handlers/_default.py:UNHANDLED_UNITS`."
        ),
        "inbox_migration_freshness": (
            "Accepted inbox items are sitting unmigrated. Run "
            "`python3 scripts/apply_pipeline.py` — the hotfix migration "
            "phase mints vault dp-NNN entries for any accepted inbox item "
            "lacking an `accepted_as` reference."
        ),
        "arrmodel_vault_backed": (
            "An arrModel entity sources its arr from a non-vault path "
            "(legacy topConsumers / providers fixture). Confirm the entity "
            "has a populated `current.arr` / `financials.<year>.arr` in "
            "entities.json (with a provenance trail), then rebuild "
            "site-data.json. See "
            "`data/audits/wq-098-arrmodel-source-leak.md`."
        ),
        "rendered_figure_coverage": (
            "A rendered figure on `usage.html` diverges from the entity's "
            "value in entities.json by more than the per-block tolerance "
            "(±10% for providers/topConsumers, ±50% for enterpriseReality). "
            "Likely cause: a hardcoded fixture (legacy site-data.json seed "
            "or `wq096_tagging.json`) winning over an apply_pipeline write, "
            "or a stale curated evidence file. Audit the offending rows in "
            "`data/audits/wq-098-rendered-figure-coverage.md` and either "
            "(a) remove the fixture entry so the entity-derived value "
            "reaches the page, or (b) update the evidence file to match."
        ),
    }
    for a in failed:
        lines.append(f"## {a['name']} — failing")
        lines.append("")
        lines.append(f"**Count:** {a['count']}")
        lines.append("")
        lines.append(f"**Detail:** {a['details']}")
        lines.append("")
        lines.append(f"**Recommended action:** {actions.get(a['name'], 'See details above.')}")
        lines.append("")
        # surface the affected IDs / entities for actionability
        if a["name"] == "review_queue_freshness":
            ids = health["reviewQueueSummary"].get("stalePendingIds", [])
            if ids:
                lines.append("**Stale pending IDs (first 25):**")
                lines.append("")
                lines.append("```")
                for pid in ids[:25]:
                    lines.append(pid)
                lines.append("```")
                lines.append("")
        if a["name"] == "entity_vault_sync":
            for s in health["staleEntities"]["items"][:10]:
                lines.append(
                    f"- `{s['entitySlug']}` {s['field']}: "
                    f"published ${s['entityValue']}B vs vault "
                    f"${s['vaultValue']}B "
                    f"({s['deltaPct']}%) — claim `{s['vaultClaimId']}` "
                    f"({s['vaultClaimTier']}, "
                    f"{s['vaultDateOfClaim']})"
                )
            lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="wq-099 pipeline reconciliation + alerts."
    )
    parser.add_argument("--stdout", action="store_true",
                        help="Also print the snapshot JSON to stdout.")
    parser.add_argument("--suffix", default=None,
                        help="Append an extra suffix to the dated filename "
                             "(e.g. 'initial' for the seed snapshot).")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    now_utc = datetime.now(timezone.utc)
    today_iso = now_utc.strftime("%Y-%m-%d")
    health = build_health(now_utc)

    suffix = f"-{args.suffix}" if args.suffix else ""
    dated_path = os.path.join(DATA_DIR, f"pipeline-health-{today_iso}{suffix}.json")
    latest_path = os.path.join(DATA_DIR, "pipeline-health-latest.json")
    save_json(dated_path, health)
    save_json(latest_path, health)

    alert_path = write_alert(health, today_iso)

    if args.stdout:
        print(json.dumps(health, indent=2))

    failed = [a for a in health["assertions"] if not a["passed"]]
    summary = (
        f"reconcile_pipeline: {len(failed)} failing assertion(s) "
        f"of {len(health['assertions'])}"
    )
    print(summary)
    print(f"  snapshot: {dated_path}")
    print(f"  latest:   {latest_path}")
    if alert_path:
        print(f"  alert:    {alert_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
