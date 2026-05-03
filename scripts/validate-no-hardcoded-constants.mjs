#!/usr/bin/env node
// scripts/validate-no-hardcoded-constants.mjs
// wq-073 §3 #5 — assert no regression of hardcoded methodology constants
// or ratio literals in the audited HTML files.
//
// For each watched file, scan the visible HTML/JS for patterns that should
// have been replaced by data-driven hydration:
//   - "$X:$1" or "$X per $1" ratio literals OUTSIDE of [data-ratio]/[data-method] spans
//   - SCENARIOS = { ... } object literals containing scenario revenue numbers
//     (the wq-073 pattern uses `let SCENARIOS = {…}; fetch(...).then(s => SCENARIOS = s)`)
//
// Uses a coarse rule: if a watched HTML file contains a ratio literal AND
// does not use [data-ratio] / [data-method] alongside it, flag.
//
// Skipped: index.html (wq-063 wired SCENARIOS via _buildScenarios; different pattern).

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();

// File-by-file rules
const RULES = [
  {
    file: 'capital.html',
    require: [
      { pattern: /fetch\(['"]data\/scenarios\.json/, msg: 'must fetch data/scenarios.json (wq-073 SCENARIOS wire)' },
      // Ratio displays must be wrapped in data-ratio attribute (inline literal is graceful fallback)
      { pattern: /id="cf-ratio-from"[^>]*data-ratio=/, msg: '#cf-ratio-from must carry data-ratio attribute (wq-073 ratio hydration wire)' },
      { pattern: /id="cf-ratio-to"[^>]*data-ratio=/, msg: '#cf-ratio-to must carry data-ratio attribute (wq-073 ratio hydration wire)' },
    ],
  },
  {
    file: 'revenue.html',
    require: [
      { pattern: /fetch\(['"]data\/scenarios\.json/, msg: 'must fetch data/scenarios.json (wq-073 SCENARIOS wire)' },
    ],
  },
  {
    file: 'ask.html',
    require: [
      { pattern: /fetch\(['"]data\/methodology_constants\.json/, msg: 'must fetch data/methodology_constants.json (wq-073 methodology wire)' },
      { pattern: /data-method="headline\.investment_to_revenue_ratio_label"/, msg: '$15:$1 reference must be wrapped in [data-method="headline.investment_to_revenue_ratio_label"]' },
    ],
  },
  {
    file: 'in-development.html',
    require: [
      { pattern: /fetch\(['"]data\/methodology_constants\.json/, msg: 'must fetch data/methodology_constants.json (wq-073 methodology wire)' },
      { pattern: /data-method="headline\.annual_ai_investment_usd_b_label"/, msg: '$260B reference must be wrapped in [data-method="headline.annual_ai_investment_usd_b_label"]' },
      { pattern: /data-method="headline\.annual_ai_investment_per_day_usd_m_label"/, msg: '$711M reference must be wrapped in [data-method="headline.annual_ai_investment_per_day_usd_m_label"]' },
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
  for (const f of rule.forbid ?? []) {
    if (f.pattern.test(text)) {
      findings.push({ severity: 'fail', file: rule.file, ref: f.pattern.toString(), msg: f.msg });
    }
  }
  for (const r of rule.require ?? []) {
    if (!r.pattern.test(text)) {
      findings.push({ severity: 'fail', file: rule.file, ref: r.pattern.toString(), msg: 'required pattern absent: ' + r.msg });
    }
  }
}

const jsonOut = process.env.RELEASE_CHECK_NO_HARDCODED_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ no-hardcoded-constants: capital + revenue + ask + in-development all wired correctly.');
  process.exit(0);
}
console.log(`no-hardcoded-constants: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.file} — ${f.msg}`);
}
process.exit(1);
