#!/usr/bin/env node
// scripts/validate-narrative-hydration.mjs
// wq-077 §3 #6 — assert known narrative dollar references are wrapped in
// [data-narrative] spans on capital.html + revenue.html. Catches future
// regressions where someone reverts a hydrated value to a hardcoded literal.
//
// Approach: file × required-substring assertions. Each watched file has a
// list of substrings that MUST be present (the data-narrative wrappers).
// If any are missing, the wire was reverted or never landed.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();

const RULES = [
  {
    file: 'capital.html',
    require: [
      // hero intro paragraph
      { pattern: /data-narrative="capital_sankey_total"[^>]*>\$745B</, msg: 'hero intro $745B → capital_sankey_total wire' },
      // 2025-revenue + 2025-capex callouts
      { pattern: /data-narrative="market_2025_total_capex"/, msg: '2025 total_capex narrative wire' },
      { pattern: /data-narrative="market_2025_total_customer_revenue_gross"/, msg: '2025 customer revenue narrative wire' },
      // hydrator invocation
      { pattern: /hydrateNarrative\s*\(/, msg: 'hydrateNarrative() must be invoked from capital.html fetch handler' },
    ],
  },
  {
    file: 'revenue.html',
    require: [
      { pattern: /hydrateNarrative\s*\(/, msg: 'hydrateNarrative() must be invoked from revenue.html init()' },
      // The 2025 subtitle branch — was hardcoded "$17.5B" / "$9.4B"; now formats from engine
      { pattern: /formatCurrency\(grossYr\)|d\.totalCustomerRevenue_gross/, msg: '2025 subtitle branch must read engine values not hardcoded "$17.5B" / "$9.4B"' },
    ],
  },
];

const findings = [];

for (const rule of RULES) {
  const path = join(root, rule.file);
  if (!existsSync(path)) {
    findings.push({ severity: 'fail', file: rule.file, msg: 'file not found' });
    continue;
  }
  const text = readFileSync(path, 'utf8');
  for (const r of rule.require) {
    if (!r.pattern.test(text)) {
      findings.push({
        severity: 'fail',
        file: rule.file,
        ref: r.pattern.toString(),
        msg: 'required pattern absent: ' + r.msg,
      });
    }
  }
}

const jsonOut = process.env.RELEASE_CHECK_NARRATIVE_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ narrative-hydration: capital + revenue narrative wires intact.');
  process.exit(0);
}
console.log(`narrative-hydration: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.file} — ${f.msg}`);
}
process.exit(1);
