#!/usr/bin/env node
// scripts/validate-cross-page-consistency.mjs
// wq-063 §3 #6 — cross-page consistency check.
//
// Asserts:
//   1. site-data.json:cumulative.by_year[2025].customer_revenue_gross
//      matches site-data.json:sankey.totalCustomerRevenue_gross within 0.5%
//      (cumulative aggregator and Sankey engine agree on the latest year).
//   2. index.html SCENARIOS object literal contains no hardcoded $X dollar
//      values for revenue/capex/tokens — they must be data-driven (built
//      via _buildScenarios from cumulative aggregates).
//
// Failure of (1) means cumulative + sankey diverged (engine bug or stale
// regen). Failure of (2) means a developer regressed the SCENARIOS to
// hardcoded values, defeating the wq-063 wire.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const sitePath = join(root, 'site-data.json');
const indexPath = join(root, 'index.html');
const TOLERANCE = 0.005; // 0.5%
const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : (Math.abs(a - b) / denom);
}

if (!existsSync(sitePath)) {
  findings.push({ severity: 'fail', ref: 'site-data.json', msg: 'site-data.json not found' });
} else {
  const site = JSON.parse(readFileSync(sitePath, 'utf8'));
  const cumulative = site.cumulative;
  const sankey = site.sankey ?? {};

  // Check 1 — cumulative ↔ sankey latest-year agreement.
  if (!cumulative) {
    findings.push({
      severity: 'fail',
      ref: 'site-data.json:cumulative',
      msg: 'cumulative block absent — wq-063 aggregator did not run or generate_site_data.py did not propagate it',
    });
  } else {
    const yr2025 = (cumulative.by_year ?? {})['2025'];
    const cumGross = yr2025?.customer_revenue_gross;
    const sankeyGross = sankey.totalCustomerRevenue_gross;
    if (cumGross == null) {
      findings.push({
        severity: 'fail',
        ref: 'site-data.json:cumulative.by_year[2025].customer_revenue_gross',
        msg: '2025 customer_revenue_gross missing from cumulative block',
      });
    } else if (sankeyGross == null) {
      findings.push({
        severity: 'fail',
        ref: 'site-data.json:sankey.totalCustomerRevenue_gross',
        msg: 'sankey.totalCustomerRevenue_gross missing — generate_site_data.py did not propagate gross from market_aggregates',
      });
    } else if (pctDelta(cumGross, sankeyGross) > TOLERANCE) {
      findings.push({
        severity: 'fail',
        ref: 'cross-page consistency',
        msg: `cumulative.by_year[2025].customer_revenue_gross=${cumGross} vs sankey.totalCustomerRevenue_gross=${sankeyGross} — delta ${(pctDelta(cumGross, sankeyGross) * 100).toFixed(2)}% > ${TOLERANCE * 100}%`,
      });
    }
  }
}

// Check 2 — index.html SCENARIOS must not be hardcoded literals.
if (!existsSync(indexPath)) {
  findings.push({ severity: 'fail', ref: 'index.html', msg: 'index.html not found' });
} else {
  const html = readFileSync(indexPath, 'utf8');
  // Match the SCENARIOS object literal (with hardcoded dollar values).
  // Old form: bear: { capex: '$745B', revenue: '$22B', tokens: '~360T' ... }
  // New form: SCENARIOS = _buildScenarios(...)
  // Trigger fails if we see two or more hardcoded $XB values inside a
  // SCENARIOS = { ... } literal (catches reversion).
  const match = html.match(/SCENARIOS\s*=\s*\{[\s\S]{0,800}?\};/);
  if (match) {
    const block = match[0];
    const dollarCount = (block.match(/'\$\d+B'/g) ?? []).length;
    if (dollarCount >= 2) {
      findings.push({
        severity: 'fail',
        ref: 'index.html SCENARIOS literal',
        msg: `${dollarCount} hardcoded '$XB' values found inside a SCENARIOS = { ... } literal — wq-063 requires data-driven scenarios via _buildScenarios(cumulative)`,
      });
    }
  }
  // Sanity: assert _buildScenarios + cumulativeData fetch wire is present.
  if (!/_buildScenarios\s*\(/.test(html)) {
    findings.push({
      severity: 'fail',
      ref: 'index.html _buildScenarios',
      msg: '_buildScenarios() helper not present — SCENARIOS cannot be built from cumulative data',
    });
  }
  if (!/window\.cumulativeData|d\.cumulative/.test(html)) {
    findings.push({
      severity: 'fail',
      ref: 'index.html cumulative fetch',
      msg: 'no fetch of site-data.json:cumulative — SCENARIOS will only ever show fallback values',
    });
  }
}

const jsonOut = process.env.RELEASE_CHECK_CROSS_PAGE_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ cross-page-consistency: cumulative + sankey + index.html SCENARIOS aligned.');
  process.exit(0);
}
console.log(`cross-page-consistency: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.ref} — ${f.msg}`);
}
process.exit(1);
