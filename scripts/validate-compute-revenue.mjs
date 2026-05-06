#!/usr/bin/env node
// scripts/validate-compute-revenue.mjs
// wq-091 — Compute Ledger validator (v3: plain-English segment schema).
//
// Asserts (advisory by default):
//   1. site-data.json:compute exists with the headline aggregate fields under
//      the renamed schema (frontier_lab_compute_*, ai_workload_compute_*,
//      hosted_model_apis_gross_*, etc).
//   2. Every component has the full segment-schema provenance block:
//      frontier_lab_compute / ai_workload_compute / hosted_model_apis amounts
//      (2025 + Q1 2026), tier_*, segment_basis, principal_agent_confirmed,
//      retrievedAt, nextReview, copilot_excluded_*.
//   3. D6 verification gate: every component has principal_agent_confirmed: true
//      and treatment === 'principal'.
//   4. data/methodology_constants.json:compute_revenue.principal_agent_treatment
//      records principal treatment for all four entities (MSFT, AMZN, GOOGL, ORCL)
//      with filing_url, filing_date, verified_at.
//   5. Aggregation reconciles: sum of components.compute_gross_2025_usd_b
//      == compute.compute_revenue_2025_gross_usd_b within 2% (wq-091 tightened
//      from 0.5% to ±2% to match brief acceptance criteria); same for net.
//   6. Per-component segment_basis non-empty.
//   7. Segment sums reconcile: frontier_lab + ai_workload + hosted_model_apis_gross
//      == compute_gross (post-Copilot) within 2%.
//   8. Per-component AI line tie-out: segment sum + copilot_excluded must match
//      the per-provider AI line within ±2% (the bottom-up segment sizing should
//      reconcile tightly to disclosed/anchored AI line totals).
//   9. No legacy bucket_* keys remain in site-data.json:compute or in components.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const sitePath = join(root, 'site-data.json');
const methodologyPath = join(root, 'data', 'methodology_constants.json');
const disclosuresPath = join(root, 'data', 'compute_disclosures.json');
const TOLERANCE = 0.02; // wq-091: ±2% (was 0.5% under wq-089)
const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : (Math.abs(a - b) / denom);
}

// AI line targets per Final Locked Table in dec-2026-05-06-compute-ledger-bucket-sizing.md.
// segment sum + copilot_excluded must match these within ±2%.
const AI_LINE_TARGETS_2025 = {
  msft_ai: 28.0,
  amzn_aws_ai: 10.0,
  googl_cloud_ai: 7.0,
  oracle_cloud_ai: 3.0,
  coreweave: 4.5,
  nebius: 0.95,
  lambda: 0.60,
  crusoe: 0.40,
};

if (!existsSync(sitePath)) {
  findings.push({ severity: 'fail', section: 'compute', ref: 'site-data.json', msg: 'site-data.json not found' });
} else {
  const site = JSON.parse(readFileSync(sitePath, 'utf8'));
  const c = site.compute;

  if (!c) {
    findings.push({
      severity: 'fail',
      section: 'compute',
      ref: 'site-data.json:compute',
      msg: 'compute block absent — derive_compute_revenue.py did not run or was not applied',
    });
  } else {
    // Check 1 — headline fields (wq-091 schema)
    const requiredHeadline = [
      'lastReportedQuarter',
      'compute_revenue_2025_gross_usd_b',
      'compute_revenue_2025_net_usd_b',
      'model_pass_through_2025_usd_b',
      'compute_revenue_q1_2026_gross_usd_b',
      'compute_revenue_q1_2026_net_usd_b',
      'frontier_lab_compute_2025_usd_b',
      'ai_workload_compute_2025_usd_b',
      'hosted_model_apis_gross_2025_usd_b',
      'copilot_excluded_2025_usd_b',
      'concentration',
      'layer_stack_ratios',
      'components',
    ];
    for (const k of requiredHeadline) {
      if (c[k] == null) {
        findings.push({
          severity: 'fail',
          section: 'compute',
          ref: `compute.${k}`,
          msg: 'required headline field missing',
        });
      }
    }

    // Check 9 — no legacy bucket_* keys at headline level
    const legacyHeadlineKeys = Object.keys(c).filter(k => /^bucket_/i.test(k));
    if (legacyHeadlineKeys.length > 0) {
      findings.push({
        severity: 'fail',
        section: 'schema-rename',
        ref: 'compute',
        msg: `legacy bucket_* keys remain at headline: ${legacyHeadlineKeys.join(', ')}`,
      });
    }

    // Check 2/3/6 — every component has full segment-schema provenance + D6 gate
    const requiredCompFields = [
      'frontier_lab_compute_2025_usd_b',
      'ai_workload_compute_2025_usd_b',
      'hosted_model_apis_gross_2025_usd_b',
      'hosted_model_apis_pass_through_2025_usd_b',
      'hosted_model_apis_net_2025_usd_b',
      'copilot_excluded_2025_usd_b',
      'frontier_lab_compute_q1_2026_usd_b',
      'ai_workload_compute_q1_2026_usd_b',
      'hosted_model_apis_gross_q1_2026_usd_b',
      'hosted_model_apis_pass_through_q1_2026_usd_b',
      'copilot_excluded_q1_2026_usd_b',
      'compute_gross_2025_usd_b',
      'compute_net_2025_usd_b',
      'compute_gross_q1_2026_usd_b',
      'compute_net_q1_2026_usd_b',
      'tier_frontier_lab_compute',
      'tier_ai_workload_compute',
      'tier_hosted_model_apis',
      'segment_basis',
      'principal_agent_confirmed',
      'treatment',
      'retrievedAt',
      'nextReview',
    ];
    for (const [slug, comp] of Object.entries(c.components ?? {})) {
      for (const f of requiredCompFields) {
        if (comp[f] == null || comp[f] === '') {
          findings.push({
            severity: 'fail',
            section: 'compute-component',
            ref: `compute.components.${slug}.${f}`,
            msg: 'required field missing or empty',
          });
        }
      }
      if (comp.principal_agent_confirmed !== true) {
        findings.push({
          severity: 'fail',
          section: 'D6-gate',
          ref: `compute.components.${slug}.principal_agent_confirmed`,
          msg: 'D6 verification gate not satisfied — principal_agent_confirmed must be true. Re-verify against most recent 10-K accounting policy notes before publication.',
        });
      }
      if (comp.treatment && comp.treatment !== 'principal') {
        findings.push({
          severity: 'fail',
          section: 'D6-gate',
          ref: `compute.components.${slug}.treatment`,
          msg: `treatment is "${comp.treatment}" — aggregator assumes principal-everywhere; if any component shifts to agent treatment, the aggregation rule must change. File a decision file before continuing.`,
        });
      }

      // Check 9 (per component) — no legacy bucket_* keys
      const legacyCompKeys = Object.keys(comp).filter(k => /^bucket_/i.test(k) || k === 'tier_bucket_1' || k === 'tier_bucket_2' || k === 'tier_bucket_3');
      if (legacyCompKeys.length > 0) {
        findings.push({
          severity: 'fail',
          section: 'schema-rename',
          ref: `compute.components.${slug}`,
          msg: `legacy bucket_* keys remain on component: ${legacyCompKeys.join(', ')}`,
        });
      }

      // Segment sum tie-out per component (post-Copilot)
      const segmentSum = (comp.frontier_lab_compute_2025_usd_b ?? 0)
        + (comp.ai_workload_compute_2025_usd_b ?? 0)
        + (comp.hosted_model_apis_gross_2025_usd_b ?? 0);
      if (comp.compute_gross_2025_usd_b != null && pctDelta(segmentSum, comp.compute_gross_2025_usd_b) > TOLERANCE) {
        findings.push({
          severity: 'fail',
          section: 'aggregation',
          ref: `compute.components.${slug}.compute_gross_2025_usd_b`,
          msg: `per-component compute_gross_2025_usd_b (${comp.compute_gross_2025_usd_b}) does not match frontier_lab + ai_workload + hosted_model_apis_gross (${segmentSum.toFixed(3)})`,
        });
      }

      // Check 8 — AI line tie-out (segments + copilot ≈ disclosed/anchored AI line)
      const aiLineTarget = AI_LINE_TARGETS_2025[slug];
      if (aiLineTarget != null) {
        const fullSum = segmentSum + (comp.copilot_excluded_2025_usd_b ?? 0);
        if (pctDelta(fullSum, aiLineTarget) > TOLERANCE) {
          findings.push({
            severity: 'fail',
            section: 'ai-line-tie-out',
            ref: `compute.components.${slug}`,
            msg: `AI line tie-out fail: segment sum + copilot (${fullSum.toFixed(3)}) does not match Final Locked Table target ($${aiLineTarget}B) within ±2%. Per wq-091 brief: write a decision file rather than paper over.`,
          });
        }
      }
    }

    // Check 5 — headline aggregation reconciles
    const components = Object.values(c.components ?? {});
    const grossSum = components.reduce((s, comp) => s + (comp.compute_gross_2025_usd_b ?? 0), 0);
    const netSum = components.reduce((s, comp) => s + (comp.compute_net_2025_usd_b ?? 0), 0);
    if (c.compute_revenue_2025_gross_usd_b != null && pctDelta(grossSum, c.compute_revenue_2025_gross_usd_b) > TOLERANCE) {
      findings.push({
        severity: 'fail',
        section: 'aggregation',
        ref: 'compute.compute_revenue_2025_gross_usd_b',
        msg: `gross headline (${c.compute_revenue_2025_gross_usd_b}) does not match sum of components (${grossSum.toFixed(2)})`,
      });
    }
    if (c.compute_revenue_2025_net_usd_b != null && pctDelta(netSum, c.compute_revenue_2025_net_usd_b) > TOLERANCE) {
      findings.push({
        severity: 'fail',
        section: 'aggregation',
        ref: 'compute.compute_revenue_2025_net_usd_b',
        msg: `net headline (${c.compute_revenue_2025_net_usd_b}) does not match sum of components (${netSum.toFixed(2)})`,
      });
    }

    // Check 7 — segment sum tie-out at the headline
    const headlineSegmentSum = (c.frontier_lab_compute_2025_usd_b ?? 0)
      + (c.ai_workload_compute_2025_usd_b ?? 0)
      + (c.hosted_model_apis_gross_2025_usd_b ?? 0);
    if (c.compute_revenue_2025_gross_usd_b != null && pctDelta(headlineSegmentSum, c.compute_revenue_2025_gross_usd_b) > TOLERANCE) {
      findings.push({
        severity: 'fail',
        section: 'aggregation',
        ref: 'compute.segment_sum',
        msg: `headline frontier_lab + ai_workload + hosted_model_apis_gross (${headlineSegmentSum.toFixed(2)}) does not match compute_revenue_2025_gross_usd_b (${c.compute_revenue_2025_gross_usd_b})`,
      });
    }
  }
}

// Check 4 — methodology_constants principal/agent record + segment_model_doc presence
if (!existsSync(methodologyPath)) {
  findings.push({
    severity: 'fail',
    section: 'D6-gate',
    ref: 'data/methodology_constants.json',
    msg: 'methodology_constants.json not found',
  });
} else {
  const m = JSON.parse(readFileSync(methodologyPath, 'utf8'));
  const cr = m.compute_revenue ?? {};
  const t = cr.principal_agent_treatment ?? {};
  const requiredEntities = ['msft_azure_openai_service', 'amzn_aws_bedrock', 'googl_vertex_partner_models', 'orcl_oci_partner_workloads'];
  for (const e of requiredEntities) {
    const rec = t[e];
    if (!rec) {
      findings.push({
        severity: 'fail',
        section: 'D6-gate',
        ref: `methodology_constants.compute_revenue.principal_agent_treatment.${e}`,
        msg: 'D6 verification record missing — must read most recent 10-K accounting policy notes before publication',
      });
      continue;
    }
    if (rec.treatment !== 'principal') {
      findings.push({
        severity: 'fail',
        section: 'D6-gate',
        ref: `methodology_constants.compute_revenue.principal_agent_treatment.${e}.treatment`,
        msg: `treatment is "${rec.treatment}" — aggregator assumes principal-everywhere; aggregation rule changes if any entity uses agent treatment`,
      });
    }
    for (const reqd of ['filing_url', 'filing_date', 'verified_at', 'basis']) {
      if (!rec[reqd]) {
        findings.push({
          severity: 'advisory',
          section: 'D6-gate',
          ref: `methodology_constants.compute_revenue.principal_agent_treatment.${e}.${reqd}`,
          msg: `${reqd} should be populated for full citation reproducibility`,
        });
      }
    }
  }

  // Check 9 — bucket_model_doc legacy key absent; segment_model_doc present
  if (cr.bucket_model_doc != null) {
    findings.push({
      severity: 'fail',
      section: 'schema-rename',
      ref: 'methodology_constants.compute_revenue.bucket_model_doc',
      msg: 'legacy bucket_model_doc key remains — should be renamed to segment_model_doc per wq-091 D8',
    });
  }
  if (!cr.segment_model_doc) {
    findings.push({
      severity: 'fail',
      section: 'schema-rename',
      ref: 'methodology_constants.compute_revenue.segment_model_doc',
      msg: 'segment_model_doc field missing — required after wq-091 D8 rename',
    });
  }
}

// Check 9 (disclosures file) — no bucket_* keys remain in compute_disclosures.json
if (existsSync(disclosuresPath)) {
  const raw = readFileSync(disclosuresPath, 'utf8');
  const legacyTokens = ['"bucket_1_', '"bucket_2_', '"bucket_3_', '"bucket_basis"', '"tier_bucket_'];
  for (const tok of legacyTokens) {
    if (raw.includes(tok)) {
      findings.push({
        severity: 'fail',
        section: 'schema-rename',
        ref: 'data/compute_disclosures.json',
        msg: `legacy schema token "${tok}" remains — should be renamed per wq-091 D8`,
      });
    }
  }
}

const jsonOut = process.env.RELEASE_CHECK_COMPUTE_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ compute-revenue: site-data.json:compute segment schema + D6 gate + aggregation reconciled (±2%).');
  process.exit(0);
}
const fails = findings.filter(f => f.severity === 'fail').length;
const advs = findings.filter(f => f.severity === 'advisory').length;
console.log(`compute-revenue: ${fails} fail, ${advs} advisory`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(8)}] ${f.ref} — ${f.msg}`);
}
process.exit(fails > 0 ? 1 : 0);
