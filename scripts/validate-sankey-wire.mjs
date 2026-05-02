#!/usr/bin/env node
// scripts/validate-sankey-wire.mjs
// wq-044 wire-completion §1.4 — assert site-data.json:sankey.providers matches
// entities.json:market_aggregates.<current_year>.providers within 1%. Catches
// the exact bug 2026-05-02 hit: engine wrote new values into entities.json
// but generate_site_data.py was never run (or only ran the totals path),
// so the rendered Sankey shipped stale hand-curated values silently.
//
// What it checks:
//   1. For every provider in market_aggregates.<year>.providers that has a
//      mapped entry in site-data.json:sankey.providers, the values must
//      agree within 1% of the larger value.
//   2. site-data.json:sankey.totalCustomerRevenue must agree with
//      market_aggregates.<year>.total_customer_revenue within 1%.
//   3. site-data.json:sankey.totalVCSubsidy must agree with
//      market_aggregates.<year>.total_vc_subsidy within 1%.
//
// What it DOESN'T check (intentionally):
//   - Aggregation nodes in site-data.json:sankey.providers (like IaaS) that
//     don't map to a single entity slug — those stay hand-curated and the
//     engine doesn't try to derive them.
//   - data/sankey-projections.json — that file is the renderer's secondary
//     source (used by follow-the-trillion.html); generate_site_data.py
//     regenerates it from the same engine block, so checking site-data.json
//     parity catches both files' regressions in practice.
//
// Exit non-zero on any divergence so release-gate fails before shipping.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const entitiesPath = join(root, 'entities.json');
const siteDataPath = join(root, 'site-data.json');

if (!existsSync(entitiesPath) || !existsSync(siteDataPath)) {
  console.error('entities.json and/or site-data.json not found');
  process.exit(2);
}

const TOLERANCE_PCT = 1.0;
const CURRENT_YEAR = process.env.WQ044_CURRENT_YEAR ?? '2025';

// Slug → display label mapping. Mirrors the inline mapping in
// generate_site_data.py + derive_market_aggregates.py:SLUG_TO_DISPLAY.
// Kept in sync manually; if you add a new model_provider entity, add it
// here too OR move all three to data/sankey-structure.json (brief §3.1
// follow-on).
const SLUG_TO_LABEL = {
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  google: 'Google (Gemini)',
  meta: 'Meta (Llama)',
  deepseek: 'DeepSeek',
  mistral: 'Mistral',
  xai: 'xAI',
  minimax: 'Minimax',
  moonshot: 'Moonshot',
};

const entities = JSON.parse(readFileSync(entitiesPath, 'utf8'));
const siteData = JSON.parse(readFileSync(siteDataPath, 'utf8'));

const yearBlock = entities?.market_aggregates?.[CURRENT_YEAR];
if (!yearBlock) {
  console.error(`entities.json:market_aggregates.${CURRENT_YEAR} not found`);
  process.exit(2);
}

const providers = yearBlock.providers ?? {};
const sankeyProviders = siteData?.sankey?.providers ?? [];
const sankeyByLabel = new Map(sankeyProviders.map(p => [p.label, p]));

const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : (Math.abs(a - b) / denom) * 100;
}

// 1. Per-provider value parity
for (const [slug, p] of Object.entries(providers)) {
  const label = SLUG_TO_LABEL[slug];
  if (!label) {
    findings.push({
      severity: 'fail',
      ref: `market_aggregates.${CURRENT_YEAR}.providers.${slug}`,
      msg: `slug ${slug} has no SLUG_TO_LABEL mapping in this validator. Add it here AND in generate_site_data.py + derive_market_aggregates.py:SLUG_TO_DISPLAY.`,
    });
    continue;
  }
  const sankeyEntry = sankeyByLabel.get(label);
  if (!sankeyEntry) {
    // Not necessarily a fail — small providers might not appear in sankey.providers
    // if their value is 0. Only fail if value > 0.
    if (p.value > 0) {
      findings.push({
        severity: 'fail',
        ref: `site-data.json:sankey.providers[${label}]`,
        msg: `engine value=${p.value} but no matching entry in site-data.json:sankey.providers. Did you forget to run generate_site_data.py?`,
      });
    }
    continue;
  }
  const delta = pctDelta(p.value, sankeyEntry.value);
  if (delta > TOLERANCE_PCT) {
    findings.push({
      severity: 'fail',
      ref: `site-data.json:sankey.providers[${label}].value`,
      msg: `engine=${p.value}, site-data=${sankeyEntry.value}, delta ${delta.toFixed(2)}% > ${TOLERANCE_PCT}%. Run scripts/generate_site_data.py to refresh.`,
    });
  }
}

// 2. Totals parity
const totalCRDelta = pctDelta(yearBlock.total_customer_revenue ?? 0, siteData?.sankey?.totalCustomerRevenue ?? 0);
if (totalCRDelta > TOLERANCE_PCT) {
  findings.push({
    severity: 'fail',
    ref: 'site-data.json:sankey.totalCustomerRevenue',
    msg: `engine=${yearBlock.total_customer_revenue}, site-data=${siteData.sankey.totalCustomerRevenue}, delta ${totalCRDelta.toFixed(2)}% > ${TOLERANCE_PCT}%`,
  });
}
const totalVCDelta = pctDelta(yearBlock.total_vc_subsidy ?? 0, siteData?.sankey?.totalVCSubsidy ?? 0);
if (totalVCDelta > TOLERANCE_PCT) {
  findings.push({
    severity: 'fail',
    ref: 'site-data.json:sankey.totalVCSubsidy',
    msg: `engine=${yearBlock.total_vc_subsidy}, site-data=${siteData.sankey.totalVCSubsidy}, delta ${totalVCDelta.toFixed(2)}% > ${TOLERANCE_PCT}%`,
  });
}

const jsonOut = process.env.RELEASE_CHECK_SANKEY_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log(`✓ sankey-wire: site-data.json:sankey matches market_aggregates.${CURRENT_YEAR} within ${TOLERANCE_PCT}%.`);
  process.exit(0);
}

console.log(`sankey-wire: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.ref} — ${f.msg}`);
}
process.exit(1);
