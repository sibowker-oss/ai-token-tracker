#!/usr/bin/env node
// scripts/validate-sankey-conservation.mjs
// wq-055 §3.2 — conservation validation gate. Checked against
// data/sankey-projections.json (the file the Sankey renderer reads via
// follow-the-trillion.html) AND site-data.json:sankey (the file
// revenue.html reads). Both must satisfy the conservation laws.
//
// Rules checked (tolerance 0.5%):
//   1. sum(non-VC buyers) == sum(channels)
//      (both equal total customer revenue routed through channels)
//   2. sum(non-VC buyers) + VC buyer == sum(providers)
//      (provider total = customer revenue + VC subsidy aggregated)
//   3. sum(outcomes) == totalSystem
//      (Inference + People/SG&A + Op Cash Flow == published total system)
//   4. Per provider: implied customer_revenue (= value - vc_subsidy) >= 0
//      (engine self-consistency; sankey-projections.json only)
//
// What we DON'T check (intentionally):
//   - sum(providers) == sum(outcomes): they differ by cashflow (channel
//     margins that don't reach providers). Not a bug — the Sankey
//     structure routes channel margins → cashflow without going through
//     providers.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const sitePath = join(root, 'site-data.json');
const projPath = join(root, 'data', 'sankey-projections.json');

if (!existsSync(sitePath) || !existsSync(projPath)) {
  console.error('site-data.json and/or data/sankey-projections.json not found');
  process.exit(2);
}

const TOLERANCE = 0.005;  // 0.5%
const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : (Math.abs(a - b) / denom);
}

function checkSankey(name, sankey, opts = {}) {
  const buyers = sankey.buyers ?? [];
  const channels = sankey.channels ?? [];
  const providers = sankey.providers ?? [];
  const outcomes = sankey.outcomes ?? [];

  const nonVcBuyers = buyers.filter(b => b.label !== 'VC/Investors');
  const sumNonVc = nonVcBuyers.reduce((s, b) => s + (b.value ?? 0), 0);
  const vcBuyer = buyers.find(b => b.label === 'VC/Investors');
  const vcVal = vcBuyer?.value ?? 0;
  const sumChannels = channels.reduce((s, c) => s + (c.value ?? 0), 0);
  const sumProviders = providers.reduce((s, p) => s + (p.value ?? 0), 0);
  const sumOutcomes = outcomes.reduce((s, o) => s + (o.value ?? 0), 0);
  const totalSystem = sankey.totalSystem ?? 0;

  // Rule 1
  if (pctDelta(sumNonVc, sumChannels) > TOLERANCE) {
    findings.push({
      severity: 'fail',
      ref: `${name}.sankey.buyers vs channels`,
      msg: `sum(non-VC buyers)=${sumNonVc.toFixed(4)} vs sum(channels)=${sumChannels.toFixed(4)} — delta ${(pctDelta(sumNonVc, sumChannels) * 100).toFixed(2)}% > ${TOLERANCE * 100}%`,
    });
  }

  // Rule 2
  if (pctDelta(sumNonVc + vcVal, sumProviders) > TOLERANCE) {
    findings.push({
      severity: 'fail',
      ref: `${name}.sankey.buyers + VC vs providers`,
      msg: `sum(buyers)=${(sumNonVc + vcVal).toFixed(4)} vs sum(providers)=${sumProviders.toFixed(4)} — delta ${(pctDelta(sumNonVc + vcVal, sumProviders) * 100).toFixed(2)}%`,
    });
  }

  // Rule 3
  if (pctDelta(sumOutcomes, totalSystem) > TOLERANCE) {
    findings.push({
      severity: 'fail',
      ref: `${name}.sankey.outcomes vs totalSystem`,
      msg: `sum(outcomes)=${sumOutcomes.toFixed(4)} vs totalSystem=${totalSystem.toFixed(4)} — delta ${(pctDelta(sumOutcomes, totalSystem) * 100).toFixed(2)}%`,
    });
  }

  // Rule 4
  if (opts.checkPerProviderSelfConsistency) {
    const vcByLabel = (sankey.costParams?.vcSubsidy) ?? {};
    for (const p of providers) {
      const vc = vcByLabel[p.label];
      if (vc === undefined) continue;
      const cr = p.value - vc;
      if (cr < 0) {
        findings.push({
          severity: 'fail',
          ref: `${name}.sankey.providers[${p.label}].self-consistency`,
          msg: `implied customer_revenue=${cr.toFixed(4)} < 0 (value=${p.value} - vc_subsidy=${vc})`,
        });
      }
    }
  }
}

const site = JSON.parse(readFileSync(sitePath, 'utf8'));
checkSankey('site-data.json', site.sankey ?? {});

const proj = JSON.parse(readFileSync(projPath, 'utf8'));
const proj2025 = proj['2025'] ?? {};
checkSankey('sankey-projections.json:2025', proj2025, { checkPerProviderSelfConsistency: true });

const jsonOut = process.env.RELEASE_CHECK_SANKEY_CONSERVATION_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log(`✓ sankey-conservation: site-data.json + sankey-projections.json both balance within ${TOLERANCE * 100}% tolerance.`);
  process.exit(0);
}

console.log(`sankey-conservation: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.ref} — ${f.msg}`);
}
process.exit(1);
