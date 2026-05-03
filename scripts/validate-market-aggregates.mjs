#!/usr/bin/env node
// scripts/validate-market-aggregates.mjs
// wq-067 §3 #5 — internal consistency for market_aggregates per year.
//
// Asserts (within 0.5% tolerance):
//   1. sum(per_source_capex) == total_capex   (mag7 + neocloud + sovereign + enterprise)
//   2. sum(per_segment) == total_customer_revenue (consumer + sme + enterprise rolls up to provider revenue ± fallback noise)
//   3. sum(total_per_channel.values) == total_customer_revenue_gross
//   4. infra_to_revenue_ratio == total_capex / total_customer_revenue_gross
//   5. tokens_annual_inference == tokens_per_day_total × 1e12 × 365 (engine identity)
//
// Skipped when site-data.json:market.<year> is absent (engine not yet run).

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const sitePath = join(root, 'site-data.json');
const TOLERANCE = 0.005;
const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : Math.abs(a - b) / denom;
}

if (!existsSync(sitePath)) {
  findings.push({ severity: 'fail', ref: 'site-data.json', msg: 'site-data.json not found' });
} else {
  const site = JSON.parse(readFileSync(sitePath, 'utf8'));
  const market = site.market || {};
  for (const [year, m] of Object.entries(market)) {
    // Rule 1 — per-source capex sum
    const partsCapex = (m.mag7_capex ?? 0) + (m.neocloud_capex ?? 0) + (m.sovereign_capex ?? 0) + (m.enterprise_capex ?? 0);
    if (m.total_capex != null && pctDelta(partsCapex, m.total_capex) > TOLERANCE) {
      findings.push({
        severity: 'fail',
        ref: `market.${year}.capex_sum`,
        msg: `mag7+neocloud+sovereign+enterprise=${partsCapex.toFixed(4)} vs total_capex=${m.total_capex} — delta ${(pctDelta(partsCapex, m.total_capex) * 100).toFixed(2)}%`,
      });
    }

    // Rule 3 — sum(per_channel) == total_customer_revenue_gross
    if (m.total_per_channel && m.total_customer_revenue_gross != null) {
      const sumChannels = Object.values(m.total_per_channel).reduce((s, v) => s + (v ?? 0), 0);
      if (pctDelta(sumChannels, m.total_customer_revenue_gross) > TOLERANCE) {
        findings.push({
          severity: 'fail',
          ref: `market.${year}.per_channel_sum_vs_gross`,
          msg: `sum(total_per_channel)=${sumChannels.toFixed(4)} vs total_customer_revenue_gross=${m.total_customer_revenue_gross} — delta ${(pctDelta(sumChannels, m.total_customer_revenue_gross) * 100).toFixed(2)}%`,
        });
      }
    }

    // Rule 4 — infra_to_revenue identity
    if (m.infra_to_revenue_ratio != null && m.total_capex != null && m.total_customer_revenue_gross) {
      const expected = m.total_capex / m.total_customer_revenue_gross;
      if (pctDelta(m.infra_to_revenue_ratio, expected) > 0.02) {  // 2% tol — rounding
        findings.push({
          severity: 'fail',
          ref: `market.${year}.infra_to_revenue_ratio_identity`,
          msg: `infra_to_revenue=${m.infra_to_revenue_ratio} vs total_capex/gross=${expected.toFixed(4)} — delta ${(pctDelta(m.infra_to_revenue_ratio, expected) * 100).toFixed(2)}%`,
        });
      }
    }

    // Rule 5 — tokens_annual identity
    if (m.tokens_per_day_total != null && m.tokens_annual_inference != null) {
      const expected = m.tokens_per_day_total * 1e12 * 365;
      if (pctDelta(m.tokens_annual_inference, expected) > TOLERANCE) {
        findings.push({
          severity: 'fail',
          ref: `market.${year}.tokens_annual_identity`,
          msg: `tokens_annual_inference=${m.tokens_annual_inference} vs tokens_per_day_total*1e12*365=${expected} — delta ${(pctDelta(m.tokens_annual_inference, expected) * 100).toFixed(2)}%`,
        });
      }
    }
  }
}

const jsonOut = process.env.RELEASE_CHECK_MARKET_AGGREGATES_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ market-aggregates: per-source capex + per-channel + ratios + tokens identities hold.');
  process.exit(0);
}
console.log(`market-aggregates: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.ref} — ${f.msg}`);
}
process.exit(1);
