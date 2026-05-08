#!/usr/bin/env python3
"""apply_pipeline.py — the canonical TAIL apply layer (wq-098).

Replaces the legacy `apply_claims.py` + `apply_decisions.py` pair. Reads
`vault-data.json`, dispatches each unprocessed claim to a registered typed
handler, and writes resolved values to `entities.json` + provenance + the
vault `usedOn` field. Idempotent.

USAGE
    # see what would change without writing
    python3 scripts/apply_pipeline.py --dry-run

    # apply for real (will halt if industry_total moves >$5B without flag)
    python3 scripts/apply_pipeline.py

    # explicitly authorise a >$5B aggregate change
    python3 scripts/apply_pipeline.py --confirm-major-change

    # verbose per-claim trace
    python3 scripts/apply_pipeline.py --verbose

EXIT CODES
    0  — success (dry-run or apply)
    2  — material-change gate triggered, --confirm-major-change required
    3  — unhandled unit detected (CI-level failure)

NOTES
    * Auto-apply gate (D2): only claims with confidence='verified' AND
      tier in {tier_1A, tier_1B, tier_2A} are written. Tier_2B+ stays in
      vault-data.json with usedOn=[] until manually approved (wq-100).
    * Conflict resolution (D6): stronger tier wins; ties → latest
      dateOfClaim → latest dateAdded.
    * Bypass closure (D5): only this script writes vault-data.json
      (allowlist documented in data/audits/wq-098-direct-vault-writers.md).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from apply_handlers import all_handlers, default_handler  # noqa: E402
from apply_handlers import _shared as S  # noqa: E402
from apply_handlers import _variance_gate as VG  # noqa: E402

VAULT_DATA = os.path.join(ROOT_DIR, "vault-data.json")
ENTITIES = os.path.join(ROOT_DIR, "entities.json")
SCHEMA = os.path.join(ROOT_DIR, "metric-schema.json")
SITE_DATA = os.path.join(ROOT_DIR, "site-data.json")
COMPUTE_DISCLOSURES_DIR = os.path.join(ROOT_DIR, "data", "evidence", "compute_disclosures")
LOG_FILE = os.path.join(ROOT_DIR, "data", "apply_pipeline.log")
SKIPPED_AUDIT = os.path.join(ROOT_DIR, "data", "audits", "wq-098-skipped-claims.md")
APPLY_LOG_JSON = os.path.join(ROOT_DIR, "data", "apply_log.json")
ANOMALIES_DIR = os.path.join(ROOT_DIR, "data", "audits")

MATERIAL_CHANGE_THRESHOLD_B = 5.0  # D9


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@dataclass
class PipelineContext:
    entities: dict
    schema: dict
    dry_run: bool = False
    verbose: bool = False
    log_lines: list = field(default_factory=list)
    audit_rows: list = field(default_factory=list)

    def log(self, level, msg):
        line = f"[{level}] {msg}"
        self.log_lines.append(line)
        if self.verbose or level in ("WARN", "ERROR"):
            print(line)

    def audit(self, row):
        self.audit_rows.append(row)


def build_dispatch():
    """Map vault `unit` value → handler module + handle function."""
    table = {}
    for unit, module, fn in all_handlers():
        # Last-wins is fine — handlers are written so each unit lives in one
        # module. If a unit is registered twice, that's a bug, surface it.
        if unit in table and table[unit][0] is not module:
            raise RuntimeError(
                f"unit '{unit}' registered by multiple handlers: "
                f"{table[unit][0].__name__} and {module.__name__}"
            )
        table[unit] = (module, fn)
    return table


def known_units(dispatch):
    handler_units = set(dispatch.keys())
    handler_units.update(default_handler().UNHANDLED_UNITS)
    return handler_units


def vault_units(vault):
    return {(dp.get("unit") or "") for dp in vault.get("dataPoints", [])}


def process_claim(claim, dispatch, ctx):
    """Dispatch a claim to its handler. Returns HandlerResult."""
    if S.is_do_not_apply(claim):
        ctx.log("INFO", f"{claim.get('id')} — do_not_apply / parked, skipped")
        result = S.HandlerResult(skip_reason="do_not_apply")
        return result

    if not S.is_auto_apply(claim):
        # Tier 2B+ or non-verified — leave for manual review (wq-100)
        result = S.HandlerResult(skip_reason="below_auto_apply_threshold")
        return result

    unit = claim.get("unit") or ""
    handler = dispatch.get(unit)
    if not handler:
        # Defer to default — it routes to audit and logs
        return default_handler().handle(claim, ctx)

    module, fn = handler
    try:
        result = fn(claim, ctx)
    except Exception as exc:  # surface, don't crash the whole run
        ctx.log("ERROR", f"{claim.get('id')} handler {module.__name__} crashed: {exc}")
        return S.HandlerResult(
            skip_reason=f"handler_exception:{exc!s}"[:120],
            audit_rows=[{
                "id": claim.get("id"),
                "category": module.__name__.split(".")[-1],
                "reason": f"handler crashed: {exc!s}"[:200],
                "claim": (claim.get("claim") or "")[:120],
            }],
        )

    # Fallthrough: when an "$B"-class claim isn't ARR-shaped (valuation /
    # funding / credit / burn), try routing to a sibling handler based on
    # text signals. This lets us keep one handler-per-unit registration
    # while still catching the common case where unit "$B" carries a
    # non-ARR meaning. Order: valuation → burn → growth → telemetry.
    if not result.applied and result.skip_reason == "unit_matches_but_not_arr_claim":
        text = " ".join([
            claim.get("claim", "") or "",
            " ".join(str(t) for t in (claim.get("tags") or [])),
            claim.get("metricKey", "") or "",
        ]).lower()
        from apply_handlers import valuation as _val, burn as _burn
        if any(t in text for t in ("valuation", "valued at", "post money",
                                    "investor offer", "implied ipo")):
            return _val.handle(claim, ctx)
        if any(t in text for t in ("burn", "operating loss", "cash burn",
                                    "cumulative burn")):
            return _burn.handle(claim, ctx)
    return result


def _claim_sort_key(write):
    """Sort writes per D6: highest tier wins; ties → latest dateOfClaim →
    latest dateAdded. Returned tuple is comparable, larger = wins."""
    tier = write.prov_entry.get("tier") or "tier_3B"
    rank = S.TIER_RANK.get(tier, 0)
    date_of_claim = (write.prov_entry.get("date") or "")
    return (rank, date_of_claim)


def collapse_writes(writes, ctx):
    """Within a single run, deduplicate writes targeting (entity, period,
    field). Per D6: keep the highest-tier + latest-date write; route
    losers to audit so the operator sees what was suppressed.
    """
    groups = {}
    for w in writes:
        key = (w.entity_slug.lower(), w.year_key, w.field_key)
        groups.setdefault(key, []).append(w)

    winners = []
    losers = []
    for key, group in groups.items():
        if len(group) == 1:
            winners.append(group[0])
            continue
        group_sorted = sorted(group, key=_claim_sort_key, reverse=True)
        winners.append(group_sorted[0])
        for loser in group_sorted[1:]:
            losers.append(loser)
            ctx.log(
                "DEDUP",
                f"suppressed within-run: {loser.label} "
                f"(winner: {group_sorted[0].prov_entry.get('id')})",
            )
    return winners, losers


# Acceptance #9 threshold — if existing field value diverges from incoming
# by more than this fraction, log WARN and skip the value overwrite (we
# still append to provenance trail). Kept in sync with VG.VARIANCE_AUTO_APPLY
# so the legacy guard and the wq-100 gate agree on the band edge.
MATERIAL_DIVERGENCE_PCT = 0.15


def _write_index_by_claim_id(writes):
    """Group writes by their source claim id so we can attribute gate
    decisions back to the originating vault claim."""
    by_id = {}
    for w in writes:
        cid = (w.prov_entry or {}).get("id")
        by_id.setdefault(cid, []).append(w)
    return by_id


def apply_variance_gate(writes, entities, ctx, counters, diffs, anomalies):
    """wq-100 D3/D4/D5 gate.

    Partitions `writes` into (auto_apply_writes, review_writes, anomaly_writes).
    Side effects:
      - Increments counters['routed_to_review'] and counters['anomalies'].
      - Appends one entry per auto-applied write to `diffs` (used by
        write_apply_log_json — the data wq-099 reads).
      - Appends one entry per anomaly to `anomalies` (used by
        write_anomalies_doc).
      - Writes a single audit row per non-auto-applied claim into
        ctx.audit_rows so the operator sees why the gate routed it.

    Returns (auto, review, anomaly) lists of FieldWrite. Caller uses `auto`
    for the entities.json commit; `review` and `anomaly` are reported but
    not written to entities.json.
    """
    by_slug = {c["slug"].lower(): c for c in entities.get("companies", [])}
    auto, review, anomaly = [], [], []

    for w in writes:
        ent = by_slug.get(w.entity_slug.lower())
        decision = VG.evaluate(w, ent)

        diff_row = {
            "claim_id": (w.prov_entry or {}).get("id"),
            "entity_slug": w.entity_slug,
            "year_key": w.year_key,
            "field_key": w.field_key,
            "incoming_value": w.value,
            "prior_value": VG._resolve_prior(ent, w.year_key, w.field_key),
            "incoming_tier": decision.incoming_tier,
            "existing_tier": decision.existing_tier,
            "variance": decision.variance,
            "is_first_time": decision.is_first_time,
            "label": w.label,
            "reason": decision.reason,
        }

        if decision.bucket == "auto_apply":
            auto.append(w)
            diffs.append({**diff_row, "bucket": "auto_apply"})
            ctx.log("GATE", f"auto-apply {w.label} — {decision.reason}")
        elif decision.bucket == "anomaly":
            anomaly.append(w)
            anomalies.append(diff_row)
            counters["anomalies"] += 1
            counters["routed_to_review"] += 1
            ctx.log("ANOMALY", f"{w.label} — {decision.reason}")
            ctx.audit_rows.append({
                "id": diff_row["claim_id"],
                "category": "wq100_anomaly",
                "reason": decision.reason,
                "claim": w.label,
            })
        else:  # review
            review.append(w)
            counters["routed_to_review"] += 1
            ctx.log("REVIEW", f"{w.label} — {decision.reason}")
            ctx.audit_rows.append({
                "id": diff_row["claim_id"],
                "category": "wq100_review",
                "reason": decision.reason,
                "claim": w.label,
            })

    return auto, review, anomaly


def mark_pending_review(vault, claim_ids, reason_by_id):
    """For each vault dataPoint whose id is in `claim_ids`, set
    `pending_review: true` with the reason. Strips any `:auto` usedOn
    markers so the orphan validator surfaces the claim again. Returns the
    count of vault items updated."""
    updated = 0
    for dp in vault.get("dataPoints", []):
        cid = dp.get("id")
        if cid not in claim_ids:
            continue
        dp["pending_review"] = True
        dp["pending_review_reason"] = reason_by_id.get(cid, "")[:240]
        used = [k for k in (dp.get("usedOn") or []) if not k.endswith(":auto")]
        dp["usedOn"] = used
        updated += 1
    return updated


def write_anomalies_doc(anomalies, dry_run=False):
    """Write data/audits/anomalies-YYYY-MM-DD.md when any >50% writes
    surfaced this run. Always rewrites today's file (idempotent — running
    apply_pipeline.py twice in a day produces the same content, not
    duplicates)."""
    if not anomalies:
        return None
    os.makedirs(ANOMALIES_DIR, exist_ok=True)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    path = os.path.join(ANOMALIES_DIR, f"anomalies-{today}.md")
    if dry_run:
        return path
    lines = [
        f"# wq-100 — Variance anomalies ({today})",
        "",
        f"_Generated_: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        "",
        "Writes whose incoming value diverged >50% from the existing entity "
        "value. The gate routes them to human review and logs them here so "
        "Simon's morning glance surfaces them.",
        "",
        "| claim | entity.field@period | prior | incoming | variance | incoming tier | existing tier |",
        "|---|---|---|---|---|---|---|",
    ]
    for a in anomalies:
        var_pct = (f"{a['variance'] * 100:.1f}%"
                   if a.get("variance") is not None else "—")
        lines.append(
            f"| {a.get('claim_id') or ''} "
            f"| {a['entity_slug']}.{a['field_key']}@{a['year_key']} "
            f"| {a['prior_value']!r} | {a['incoming_value']!r} "
            f"| {var_pct} "
            f"| {a.get('incoming_tier') or '—'} "
            f"| {a.get('existing_tier') or '—'} |"
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def write_apply_log_json(counters, diffs, dry_run=False):
    """Append a run summary to data/apply_log.json — the structured rolling
    log wq-099 reads for the Pipeline tab counters and the
    "Recently auto-applied (last 24h)" card.

    Schema:
      {
        "lastUpdated": "<iso>",
        "runs": [
          {
            "ts": "<iso>",
            "auto_applied": int,
            "routed_to_review": int,
            "anomalies": int,
            "diffs": [...]    # only the auto-applied writes (with prior/new)
          },
          ...
        ],
        "counters_30d": { "auto_applied": int, ... }
      }

    Keeps the last 200 runs (the 30-day counter ignores older entries by
    timestamp). Idempotent — dry-run mode is a no-op so test runs don't
    poison the dashboard.
    """
    if dry_run:
        return None
    os.makedirs(os.path.dirname(APPLY_LOG_JSON), exist_ok=True)
    log = {"lastUpdated": "", "runs": [], "counters_30d": {
        "auto_applied": 0, "routed_to_review": 0, "anomalies": 0,
    }}
    if os.path.exists(APPLY_LOG_JSON):
        try:
            with open(APPLY_LOG_JSON, encoding="utf-8") as f:
                log = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    now = datetime.utcnow()
    auto_diffs = [d for d in diffs if d.get("bucket") == "auto_apply"]
    run_entry = {
        "ts": now.isoformat(timespec="seconds") + "Z",
        "auto_applied": counters.get("auto_applied", 0),
        "routed_to_review": counters.get("routed_to_review", 0),
        "anomalies": counters.get("anomalies", 0),
        "diffs": auto_diffs[:50],  # cap per-run payload
    }
    log.setdefault("runs", []).append(run_entry)
    log["runs"] = log["runs"][-200:]
    log["lastUpdated"] = run_entry["ts"]

    # Recompute the rolling 30-day counter on every write so the file is
    # the single source of truth for the dashboard.
    cutoff = now.timestamp() - 30 * 86400
    c30 = {"auto_applied": 0, "routed_to_review": 0, "anomalies": 0}
    for r in log["runs"]:
        try:
            ts = datetime.strptime(
                r["ts"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S",
            ).replace(tzinfo=None).timestamp()
        except (KeyError, ValueError):
            continue
        if ts < cutoff:
            continue
        c30["auto_applied"] += r.get("auto_applied", 0)
        c30["routed_to_review"] += r.get("routed_to_review", 0)
        c30["anomalies"] += r.get("anomalies", 0)
    log["counters_30d"] = c30

    with open(APPLY_LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    return APPLY_LOG_JSON


def apply_writes_to_entities(entities, writes, ctx):
    """Apply a list of FieldWrite to entities.json in place.

    Behaviour per claim:
      1. Always append to provenance trail (deduped on claim id)
      2. Gap-fill: if existing field value is None, write incoming value
      3. Confirm: if existing value within ±MATERIAL_DIVERGENCE_PCT of
         incoming, write the more-precise value (= no-op if equal)
      4. Diverge: if existing value differs >MATERIAL_DIVERGENCE_PCT, WARN
         and skip the overwrite (keeps existing value; provenance still
         records the conflict)
    """
    by_slug = {c["slug"].lower(): c for c in entities.get("companies", [])}
    applied = 0
    diverged = 0
    for w in writes:
        ent = by_slug.get(w.entity_slug.lower())
        if not ent:
            ctx.log("WARN", f"entity {w.entity_slug} not in entities.json — skipped {w.label}")
            continue

        # Resolve current scalar value
        if w.year_key == "current":
            container = ent.setdefault("current", {})
        else:
            container = ent.setdefault("financials", {}).setdefault(w.year_key, {})
        prior = container.get(w.field_key)

        # Decide write/no-write
        write_value = False
        if prior is None:
            write_value = True
        elif isinstance(prior, (int, float)) and isinstance(w.value, (int, float)):
            if prior == 0:
                # avoid div-by-zero; use absolute-delta heuristic
                write_value = abs(w.value - prior) < 1e-6 or abs(w.value) < 0.5
            else:
                divergence = abs(w.value - prior) / abs(prior)
                if divergence <= MATERIAL_DIVERGENCE_PCT:
                    # close enough — accept incoming (more precise, more recent)
                    write_value = True
                else:
                    diverged += 1
                    ctx.log(
                        "WARN",
                        f"DIVERGE {w.label}: existing={prior!r} differs "
                        f"{divergence:.0%} from incoming — kept existing, "
                        f"provenance trail extended",
                    )
                    write_value = False
        else:
            # non-numeric existing — overwrite cautiously only if same type
            write_value = type(prior) is type(w.value)

        if write_value and prior != w.value:
            container[w.field_key] = w.value
            ctx.log("APPLY", f"{w.label} (was {prior!r})")
            applied += 1
        elif write_value and prior == w.value:
            # idempotent equal — record but don't count as a change
            ctx.log("OK-EQUAL", f"{w.label} (already at value)")

        # Provenance trail — append regardless of value-write decision
        prov_key = f"{w.year_key}.{w.field_key}" if w.year_key != "current" \
            else f"current.{w.field_key}"
        prov = ent.setdefault("provenance", {}).setdefault(
            prov_key, {"confidence": "medium", "claim_count": 0, "claims": []}
        )
        existing_ids = {c.get("id") for c in prov.get("claims", [])}
        if w.prov_entry.get("id") not in existing_ids:
            prov["claims"].append(w.prov_entry)
            prov["claim_count"] = len(prov["claims"])
            tier = w.prov_entry.get("tier")
            current_conf = prov.get("confidence", "low")
            if tier in ("tier_1A", "tier_1B") and current_conf != "high":
                prov["confidence"] = "high"
            elif tier == "tier_2A" and current_conf == "low":
                prov["confidence"] = "medium"
            prov["needs_source"] = False

    if diverged:
        ctx.log("INFO", f"{diverged} writes diverged >15% — provenance updated, value kept")
    return applied


def reconcile_compute_disclosures(vault, ctx):
    """Match unresolved ARR-shape claims against evidence/compute_disclosures.

    Per acceptance #6: dp-239 ($37B Microsoft AI run-rate) propagates to
    "wherever the Compute Ledger MSFT figure lives." That value is already
    in `data/evidence/compute_disclosures/azure.json:arrGrossDisclosed`.
    We don't overwrite the evidence file (those are hand-curated); we just
    mark the vault claim's `usedOn` so the orphan validator stops pinging.

    Match rule: the claim's coerced $B value is within ±10% of the
    evidence file's arrGrossDisclosed AND the claim text mentions a token
    associated with the disclosure (e.g. "microsoft" / "azure" /
    "msft" for azure.json).
    """
    if not os.path.isdir(COMPUTE_DISCLOSURES_DIR):
        return []

    disclosures = []
    for fname in sorted(os.listdir(COMPUTE_DISCLOSURES_DIR)):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(COMPUTE_DISCLOSURES_DIR, fname), encoding="utf-8") as f:
                rec = json.load(f)
            disclosures.append((fname[:-5], rec))
        except (OSError, json.JSONDecodeError):
            continue

    DISCLOSURE_TOKENS = {
        "azure": ("microsoft", "azure", "msft"),
        "aws": ("amazon", "aws", "amzn"),
        "gcp": ("google cloud", "gcp", "alphabet"),
        "oci": ("oracle", "oci"),
    }

    matched = []
    for dp in vault.get("dataPoints", []):
        # Skip already-processed claims (any non-empty usedOn).
        if dp.get("usedOn"):
            continue
        if not S.is_auto_apply(dp):
            continue
        text = " ".join([
            dp.get("claim", "") or "",
            dp.get("notes", "") or "",
            " ".join(str(t) for t in (dp.get("tags") or [])),
            dp.get("metricKey", "") or "",
        ]).lower()
        value_b = S.coerce_value_to_billions(dp.get("value"), dp.get("unit"))
        if value_b is None:
            continue

        for disc_id, rec in disclosures:
            tokens = DISCLOSURE_TOKENS.get(disc_id, (disc_id,))
            if not any(t in text for t in tokens):
                continue
            gross = rec.get("arrGrossDisclosed")
            if not isinstance(gross, (int, float)):
                continue
            if gross == 0:
                continue
            divergence = abs(value_b - gross) / abs(gross)
            if divergence <= 0.10:
                key = f"evidence:compute_disclosures/{disc_id}"
                if append_used_on(vault, dp.get("id"), [key]):
                    matched.append((dp.get("id"), key, value_b, gross))
                    ctx.log(
                        "OK",
                        f"{dp.get('id')} matched evidence "
                        f"compute_disclosures/{disc_id} "
                        f"(${value_b:.2f}B vs ${gross:.2f}B disclosed)",
                    )
                break

    return matched


def append_used_on(vault, claim_id, keys):
    """Mark vault.dataPoints[].usedOn with new consumer keys (deduped)."""
    for dp in vault.get("dataPoints", []):
        if dp.get("id") == claim_id:
            existing = list(dp.get("usedOn") or [])
            for k in keys:
                if k not in existing:
                    existing.append(k)
            dp["usedOn"] = existing
            return True
    return False


def update_top_consumers(site, entities, ctx):
    """Refresh dashboard.topConsumers[].arrNumeric from entities.json.

    Mirrors the existing logic in generate_site_data.py:410-450 so the
    pipeline can update the rendered numbers without round-tripping through
    a full site rebuild on each apply. The full site build (running
    generate_site_data.py + wq096_emit) still happens after — this is just
    so the pipeline's own dry-run report can show the move.
    """
    ai_apps = [c for c in entities["companies"] if "ai_app" in c.get("roles", [])]
    app_lookup = {}
    for app in ai_apps:
        app_lookup[app["name"].lower()] = app
        app_lookup[app["slug"].lower()] = app

    moved = 0
    for consumer in site.get("dashboard", {}).get("topConsumers", []) or []:
        co_name = (consumer.get("co") or "").lower()
        co_slug = co_name.replace(" ", "-").replace(".", "")
        ent = app_lookup.get(co_name) or app_lookup.get(co_slug)
        if not ent:
            continue
        # latest non-projected year
        fins = ent.get("financials") or {}
        latest_year = None
        for y in sorted(fins.keys(), reverse=True):
            if not y.endswith("_projected"):
                latest_year = y
                break
        year_data = fins.get(latest_year, {}) if latest_year else {}
        arr = year_data.get("arr") or (ent.get("current") or {}).get("arr")
        if arr is None or not isinstance(arr, (int, float)):
            continue
        new_arr_numeric = int(arr * 1e9) if arr < 100 else int(arr)
        if consumer.get("arrNumeric") != new_arr_numeric:
            ctx.log("APPLY",
                    f"topConsumers[{consumer.get('co')}] arrNumeric "
                    f"{consumer.get('arrNumeric')} → {new_arr_numeric}")
            consumer["arrNumeric"] = new_arr_numeric
            consumer["arr"] = (
                f"${arr:.1f}B" if arr >= 1 else f"${arr * 1000:.0f}M"
            )
            moved += 1
    return moved


def industry_total(site):
    return ((site.get("arrModel") or {}).get("combined") or {}).get(
        "industry_total", 0.0
    )


def regenerate_site_data():
    """Run generate_site_data.py to rebuild site-data.json from entities.json."""
    import subprocess
    res = subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "generate_site_data.py")],
        capture_output=True, text=True, cwd=ROOT_DIR,
    )
    return res.returncode, res.stdout, res.stderr


def write_audit_doc(rows, summary):
    os.makedirs(os.path.dirname(SKIPPED_AUDIT), exist_ok=True)
    lines = [
        "# wq-098 — Apply pipeline skipped claims",
        "",
        f"_Generated_: {datetime.utcnow().isoformat()}Z",
        "",
        "Auto-generated by `scripts/apply_pipeline.py`. Lists every vault claim",
        "that was inspected but not auto-applied — by category and reason.",
        "",
        "## Summary",
        "",
    ]
    for k, v in summary.items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## Rows")
    lines.append("")
    if not rows:
        lines.append("_No skipped claims._")
    else:
        lines.append("| dp-id | category | reason | claim |")
        lines.append("|---|---|---|---|")
        for r in rows:
            lines.append(
                f"| {r.get('id', '')} | {r.get('category', '')} | "
                f"{r.get('reason', '')} | {(r.get('claim') or '').replace('|', '/')[:140]} |"
            )

    with open(SKIPPED_AUDIT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def write_log(ctx):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    ts = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n=== apply_pipeline.py — {ts}Z ===\n")
        for line in ctx.log_lines:
            f.write(line + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--dry-run", action="store_true",
                   help="report what would change without writing files")
    p.add_argument("--verbose", action="store_true",
                   help="echo every claim trace to stdout")
    p.add_argument("--confirm-major-change", action="store_true",
                   help="authorise an apply run that moves industry_total >$5B (D9)")
    p.add_argument("--report", action="store_true",
                   help="alias for --dry-run + --verbose")
    args = p.parse_args(argv)

    if args.report:
        args.dry_run = True
        args.verbose = True

    vault = load_json(VAULT_DATA)
    entities = load_json(ENTITIES)
    schema = load_json(SCHEMA)
    site = load_json(SITE_DATA)

    ctx = PipelineContext(entities=entities, schema=schema,
                          dry_run=args.dry_run, verbose=args.verbose)

    # CI-level: every unit in vault must be known
    dispatch = build_dispatch()
    known = known_units(dispatch)
    seen = vault_units(vault)
    unknown = seen - known - {""}
    if unknown:
        msg = (f"FAIL: vault contains units with no registered handler and not "
               f"in UNHANDLED_UNITS: {sorted(unknown)}")
        print(msg, file=sys.stderr)
        ctx.log("ERROR", msg)
        write_log(ctx)
        return 3

    pre_industry_total = industry_total(site)

    counters = {
        "auto_applied": 0,
        "routed_to_review": 0,   # wq-100 D3/D4/D5 gate
        "anomalies": 0,           # wq-100 D5 — variance >50%
        "skipped_below_threshold": 0,
        "skipped_do_not_apply": 0,
        "skipped_entity_unresolved": 0,
        "skipped_multi_tier": 0,
        "skipped_value_uncoercible": 0,
        "skipped_existing_tier_higher": 0,
        "skipped_no_handler": 0,
        "skipped_other": 0,
        "writes_queued": 0,
    }

    all_writes = []
    used_on_updates = []  # (claim_id, [keys])
    gate_diffs = []        # wq-100 — every write's gate decision (auto/review/anomaly)
    gate_anomalies = []    # wq-100 — variance >50% rows (subset of gate_diffs)

    for dp in vault.get("dataPoints", []):
        # Idempotency (D8): a non-empty usedOn means this claim was already
        # processed by an apply pass (this script or its predecessor) — skip.
        # Keys we recognise: "entityDirectory", "dashboard", "sankey",
        # "timeline", "telemetry-signals", "evidence:*", and the wq-096
        # arrModel.* keys. Treat any pre-existing usedOn as terminal.
        if dp.get("usedOn"):
            continue

        result = process_claim(dp, dispatch, ctx)

        if result.audit_rows:
            ctx.audit_rows.extend(result.audit_rows)

        if result.applied and result.writes:
            counters["auto_applied"] += 1
            counters["writes_queued"] += len(result.writes)
            all_writes.extend(result.writes)
            used_on_updates.append((dp.get("id"), result.consumer_keys))
            ctx.log(
                "OK",
                f"{dp.get('id')} → {len(result.writes)} writes "
                f"({result.writes[0].label})",
            )
        elif result.applied and not result.writes:
            # Telemetry case — handler "applied" but no entity write
            counters["auto_applied"] += 1
            used_on_updates.append((dp.get("id"), result.consumer_keys))
        else:
            reason = result.skip_reason or "unknown"
            if reason == "below_auto_apply_threshold":
                counters["skipped_below_threshold"] += 1
            elif reason == "do_not_apply":
                counters["skipped_do_not_apply"] += 1
            elif reason == "entity_unresolved":
                counters["skipped_entity_unresolved"] += 1
            elif reason == "multi_tier_ambiguous":
                counters["skipped_multi_tier"] += 1
            elif reason == "value_uncoercible":
                counters["skipped_value_uncoercible"] += 1
            elif reason.startswith("existing_tier_higher"):
                counters["skipped_existing_tier_higher"] += 1
            elif reason.startswith("no_handler_for_unit"):
                counters["skipped_no_handler"] += 1
            else:
                counters["skipped_other"] += 1

    # Within-run dedup per D6: highest tier + latest date wins
    if all_writes:
        winners, losers = collapse_writes(all_writes, ctx)
        for loser in losers:
            ctx.audit_rows.append({
                "id": loser.prov_entry.get("id"),
                "category": "within_run_dedup",
                "reason": "lower-tier or older claim suppressed by D6",
                "claim": loser.label,
            })
        all_writes = winners

    # wq-100 variance gate (D3 / D4 / D5). Partition writes BEFORE the
    # material-change gate and the entities.json commit so that
    # routed-to-review writes don't count against the $5B aggregate
    # threshold and don't mutate entities.json.
    review_writes = []
    anomaly_writes = []
    if all_writes:
        all_writes, review_writes, anomaly_writes = apply_variance_gate(
            all_writes, entities, ctx, counters, gate_diffs, gate_anomalies,
        )

    # Mark vault claims whose writes were routed to human review or flagged
    # as anomalies so the next reviewer surface picks them up. These claims
    # still belong in vault-data.json — they just don't auto-flow through.
    pending_ids = set()
    pending_reasons = {}
    for w in (review_writes + anomaly_writes):
        cid = (w.prov_entry or {}).get("id")
        if not cid:
            continue
        # Match the audit-row reason for traceability
        match = next(
            (r for r in ctx.audit_rows
             if r.get("id") == cid and r.get("category", "").startswith("wq100_")),
            None,
        )
        if match:
            pending_reasons[cid] = match.get("reason", "")
        pending_ids.add(cid)
    if pending_ids:
        # Strip the auto-applied counter for claims that produced a write
        # that the gate actually rejected — those claims didn't auto-apply
        # despite having a successful handler return. Their handler-level
        # `applied: True` was decremented at the gate, not at process_claim.
        counters["auto_applied"] = max(0, counters["auto_applied"] - len(pending_ids))
        # Drop their pre-staged usedOn updates so they aren't marked applied.
        used_on_updates = [
            (cid, keys) for (cid, keys) in used_on_updates if cid not in pending_ids
        ]

    # Material change gate — net delta across ARR fields on entities that
    # feed arrModel.combined.industry_total (ai_app + model_provider). The
    # gate counts only writes that will actually commit (gap-fill or within-
    # ±15% confirm); diverged-and-skipped writes do not move industry_total.
    arr_delta = 0.0
    by_slug = {c["slug"].lower(): c for c in entities.get("companies", [])}
    for w in all_writes:
        if w.field_key != "arr":
            continue
        ent = by_slug.get(w.entity_slug.lower())
        if not ent:
            continue
        roles = ent.get("roles") or []
        if not any(r in roles for r in ("ai_app", "model_provider")):
            continue
        if w.year_key == "current":
            prior = (ent.get("current") or {}).get("arr")
        else:
            prior = ((ent.get("financials") or {}).get(w.year_key) or {}).get("arr")
        if isinstance(prior, (int, float)) and prior != 0:
            divergence = abs(w.value - prior) / abs(prior)
            if divergence > MATERIAL_DIVERGENCE_PCT:
                continue  # would not be written; doesn't move totals
            arr_delta += float(w.value) - float(prior)
        elif isinstance(prior, (int, float)):  # prior == 0
            arr_delta += float(w.value)
        else:  # gap-fill
            arr_delta += float(w.value)
    arr_delta = abs(arr_delta)

    if arr_delta > MATERIAL_CHANGE_THRESHOLD_B and not args.confirm_major_change:
        msg = (f"HALT: cumulative ARR movement ${arr_delta:.2f}B exceeds "
               f"${MATERIAL_CHANGE_THRESHOLD_B:.0f}B threshold (D9). "
               f"Re-run with --confirm-major-change to apply.")
        print(msg, file=sys.stderr)
        ctx.log("ERROR", msg)
        write_log(ctx)
        # Still write the audit doc so the operator can review
        write_audit_doc(ctx.audit_rows, {**counters,
                                          "arr_delta_b": round(arr_delta, 2),
                                          "pre_industry_total_b": pre_industry_total})
        return 2

    # Apply writes to entities.json (after gate passes)
    if all_writes:
        apply_writes_to_entities(entities, all_writes, ctx)

    # Mark auto-applied writes with the wq-100 :auto suffix so the override
    # endpoint can find them and the dashboard can show "Recently auto-applied".
    for w in all_writes:
        cid = (w.prov_entry or {}).get("id")
        if not cid:
            continue
        # Find or extend the existing usedOn update for this claim id
        for i, (uid, keys) in enumerate(used_on_updates):
            if uid == cid:
                if "entityDirectory:auto" not in keys:
                    used_on_updates[i] = (uid, list(keys) + ["entityDirectory:auto"])
                break
        else:
            used_on_updates.append((cid, ["entityDirectory:auto"]))

    # Update vault usedOn
    for claim_id, keys in used_on_updates:
        append_used_on(vault, claim_id, keys)

    # wq-100 — flip routed-to-review and anomaly claims to pending_review.
    pending_count = mark_pending_review(vault, pending_ids, pending_reasons)
    counters["pending_review_marked"] = pending_count

    # Reconcile compute disclosures (Microsoft AI / hyperscaler ARR claims
    # whose value already lives in data/evidence/compute_disclosures/*.json
    # — mark them used without rewriting the evidence file).
    evidence_matches = reconcile_compute_disclosures(vault, ctx)
    counters["evidence_reconciled"] = len(evidence_matches)

    # Update vault meta
    vault.setdefault("meta", {})
    vault["meta"]["lastUpdated"] = datetime.utcnow().strftime("%Y-%m-%d")

    # Pre-flight: refresh site preview to estimate industry_total move
    update_top_consumers(site, entities, ctx)

    # Commit (skip if dry-run)
    if not args.dry_run:
        save_json(VAULT_DATA, vault)
        save_json(ENTITIES, entities)
        # site-data.json is regenerated by generate_site_data.py
        rc, stdout, stderr = regenerate_site_data()
        if rc != 0:
            ctx.log("ERROR", f"generate_site_data.py failed: {stderr}")
            write_log(ctx)
            return 4
        ctx.log("INFO", "site-data.json regenerated")

    # wq-100 emissions — anomaly doc + apply log JSON for the wq-099 dashboard.
    anomalies_path = write_anomalies_doc(gate_anomalies, dry_run=args.dry_run)
    apply_log_path = write_apply_log_json(counters, gate_diffs, dry_run=args.dry_run)
    if anomalies_path:
        ctx.log("INFO", f"anomalies report: {anomalies_path}")
    if apply_log_path:
        ctx.log("INFO", f"apply_log: {apply_log_path}")

    # Audit doc
    summary = {
        **counters,
        "arr_delta_b": round(arr_delta, 2),
        "pre_industry_total_b": pre_industry_total,
        "dry_run": args.dry_run,
    }
    write_audit_doc(ctx.audit_rows, summary)

    write_log(ctx)
    print()
    print("apply_pipeline summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"  audit_doc: {SKIPPED_AUDIT}")
    if apply_log_path:
        print(f"  apply_log: {apply_log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
