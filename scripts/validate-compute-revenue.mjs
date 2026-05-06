#!/usr/bin/env node
// scripts/validate-compute-revenue.mjs
// wq-087 §7 + wq-089 §"Acceptance criteria" — Compute Ledger validator (v2: bucket schema).
//
// Asserts (advisory by default):
//   1. site-data.json:compute exists with the wq-089 headline aggregate fields.
//   2. Every component has the full bucket-schema provenance block:
//      bucket_1/2/3 amounts (2025 + Q1 2026), tier_bucket_*, bucket_basis,
//      principal_agent_confirmed, retrievedAt, nextReview, copilot_excluded_*.
//   3. D6 verification gate: every component has principal_agent_confirmed: true
//      and treatment === 'principal'.
//   4. data/methodology_constants.json:compute_revenue.principal_agent_treatment
//      records principal treatment for all four entities (MSFT, AMZN, GOOGL, ORCL)
//      with filing_url, filing_date, verified_at.
//   5. Aggregation reconciles: sum of components.compute_gross_2025_usd_b
//      == compute.compute_revenue_2025_gross_usd_b within 0.5%; same for net.
//   6. Per-component bucket_basis non-empty.
//   7. Bucket sums reconcile: bucket_1+bucket_2+bucket_3_gross == compute_gross
//      (post-Copilot) within 0.5%.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const sitePath = join(root, 'site-data.json');
const methodologyPath = join(root, 'data', 'methodology_constants.json');
const TOLERANCE = 0.005;
const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : (Math.abs(a - b) / denom);
}

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
    // Check 1 — headline fields (wq-089 schema)
    const requiredHeadline = [
      'lastReportedQuarter',
      'compute_revenue_2025_gross_usd_b',
      'compute_revenue_2025_net_usd_b',
      'model_pass_through_2025_usd_b',
      'compute_revenue_q1_2026_gross_usd_b',
      'compute_revenue_q1_2026_net_usd_b',
      'bucket_1_2025_usd_b',
      'bucket_2_2025_usd_b',
      'bucket_3_gross_2025_usd_b',
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

    // Check 2/3/6 — every component has full bucket-schema provenance + D6 gate
    const requiredCompFields = [
      'bucket_1_2025_usd_b',
      'bucket_2_2025_usd_b',
      'bucket_3_gross_2025_usd_b',
      'bucket_3_pass_through_2025_usd_b',
      'bucket_3_net_2025_usd_b',
      'copilot_excluded_2025_usd_b',
      'bucket_1_q1_2026_usd_b',
      'bucket_2_q1_2026_usd_b',
      'bucket_3_gross_q1_2026_usd_b',
      'bucket_3_pass_through_q1_2026_usd_b',
      'copilot_excluded_q1_2026_usd_b',
      'compute_gross_2025_usd_b',
      'compute_net_2025_usd_b',
      'compute_gross_q1_2026_usd_b',
      'compute_net_q1_2026_usd_b',
      'tier_bucket_1',
      'tier_bucket_2',
      'tier_bucket_3',
      'bucket_basis',
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
      // Bucket sum tie-out per component
      const bucketSum = (comp.bucket_1_2025_usd_b ?? 0)
        + (comp.bucket_2_2025_usd_b ?? 0)
        + (comp.bucket_3_gross_2025_usd_b ?? 0);
      if (comp.compute_gross_2025_usd_b != null && pctDelta(bucketSum, comp.compute_gross_2025_usd_b) > TOLERANCE) {
        findings.push({
          severity: 'fail',
          section: 'aggregation',
          ref: `compute.components.${slug}.compute_gross_2025_usd_b`,
          msg: `per-component compute_gross_2025_usd_b (${comp.compute_gross_2025_usd_b}) does not match bucket_1+2+3_gross (${bucketSum.toFixed(3)})`,
        });
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

    // Check 7 — bucket sum tie-out at the headline
    const headlineBucketSum = (c.bucket_1_2025_usd_b ?? 0)
      + (c.bucket_2_2025_usd_b ?? 0)
      + (c.bucket_3_gross_2025_usd_b ?? 0);
    if (c.compute_revenue_2025_gross_usd_b != null && pctDelta(headlineBucketSum, c.compute_revenue_2025_gross_usd_b) > TOLERANCE) {
      findings.push({
        severity: 'fail',
        section: 'aggregation',
        ref: 'compute.bucket_sum',
        msg: `headline bucket_1+2+3_gross (${headlineBucketSum.toFixed(2)}) does not match compute_revenue_2025_gross_usd_b (${c.compute_revenue_2025_gross_usd_b})`,
      });
    }
  }
}

// Check 4 — methodology_constants principal/agent record
if (!existsSync(methodologyPath)) {
  findings.push({
    severity: 'fail',
    section: 'D6-gate',
    ref: 'data/methodology_constants.json',
    msg: 'methodology_constants.json not found',
  });
} else {
  const m = JSON.parse(readFileSync(methodologyPath, 'utf8'));
  const t = (m.compute_revenue ?? {}).principal_agent_treatment ?? {};
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
}

const jsonOut = process.env.RELEASE_CHECK_COMPUTE_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ compute-revenue: site-data.json:compute bucket schema + D6 gate + aggregation reconciled.');
  process.exit(0);
}
const fails = findings.filter(f => f.severity === 'fail').length;
const advs = findings.filter(f => f.severity === 'advisory').length;
console.log(`compute-revenue: ${fails} fail, ${advs} advisory`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(8)}] ${f.ref} — ${f.msg}`);
}
process.exit(fails > 0 ? 1 : 0);
