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
//   5. wq-062 — per provider Column C balance:
//        sum(routing inflows for slug) + vc_subsidy == provider.value
//      within 0.5%. Required because the wq-055 renderer routed channels
//      to providers proportionally, which silently masked per-provider
//      gaps (OpenAI 12.40 in vs 13.65 out at the 2026-05-03 audit).
//      Skipped when sankey.routing is absent (renderer fell back to
//      proportional — old data).
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

  // Rule 2 — wq-062: with grossed-up channels, channel margins flow direct
  // to cashflow without passing through providers. So buyers+VC equals
  // providers + channel_margins, not providers alone. Subtract the margin
  // contribution. When marginPcts is absent (pre-wq-062 data) the term is
  // zero and the original wq-055 invariant (buyers+VC=providers) applies.
  const marginPcts = sankey.costParams?.marginPcts ?? {};
  const channelMargins = channels.reduce((s, c) => s + (c.value ?? 0) * (marginPcts[c.label] ?? 0), 0);
  const buyersAndVc = sumNonVc + vcVal;
  const providersPlusMargins = sumProviders + channelMargins;
  if (pctDelta(buyersAndVc, providersPlusMargins) > TOLERANCE) {
    findings.push({
      severity: 'fail',
      ref: `${name}.sankey.buyers + VC vs providers + channel_margins`,
      msg: `sum(buyers)=${buyersAndVc.toFixed(4)} vs sum(providers)+channel_margins=${sumProviders.toFixed(4)}+${channelMargins.toFixed(4)}=${providersPlusMargins.toFixed(4)} — delta ${(pctDelta(buyersAndVc, providersPlusMargins) * 100).toFixed(2)}%`,
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

  // Rule 5 (wq-062) — per-provider Column C balance.
  // sum(routing[slug]) + vcSubsidy[label] must equal provider.value.
  const routing = sankey.routing;
  if (routing && typeof routing === 'object') {
    const vcByLabel = (sankey.costParams?.vcSubsidy) ?? {};
    for (const p of providers) {
      const slug = p.slug;
      if (!slug) {
        findings.push({
          severity: 'fail',
          ref: `${name}.sankey.providers[${p.label}].slug`,
          msg: `provider has no slug field — required for routing-aware balance check`,
        });
        continue;
      }
      const provRouting = routing[slug];
      if (!provRouting) {
        findings.push({
          severity: 'fail',
          ref: `${name}.sankey.routing[${slug}]`,
          msg: `routing entry missing for provider ${p.label} (slug=${slug})`,
        });
        continue;
      }
      const inflow = Object.values(provRouting).reduce((s, v) => s + (v ?? 0), 0);
      const vc = vcByLabel[p.label] ?? 0;
      const total = inflow + vc;
      if (pctDelta(total, p.value) > TOLERANCE) {
        findings.push({
          severity: 'fail',
          ref: `${name}.sankey.providers[${p.label}].column-C-balance`,
          msg: `routing inflow=${inflow.toFixed(4)} + vc_subsidy=${vc.toFixed(4)} = ${total.toFixed(4)} vs provider.value=${p.value.toFixed(4)} — delta ${(pctDelta(total, p.value) * 100).toFixed(2)}% > ${TOLERANCE * 100}%`,
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
