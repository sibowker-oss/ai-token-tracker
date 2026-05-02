#!/usr/bin/env node
// scripts/validate-consensus-provenance.mjs
// wq-048 §2 #10 — every entity-year `collected_revenue` field must have a
// provenance entry whose origin is one of:
//   - consensus_engine_derived (engine output)
//   - editorial_override       (data/consensus_overrides.json)
//   - accepted                 (raw claim accepted via review queue)
//   - editorial_reconciliation (Phase A/C manual reconciliation entries)
//   - editorial_balance_calculation (wq-044: vc_subsidy editorial-balance values)
//
// wq-044 extension: same gate also applies to `vc_subsidy` fields, which the
// Sankey wire reads in preference to operating_loss for provider VC node values.
//
// No silent untraceable values. Exit non-zero if any tracked field lacks a
// matching-origin provenance claim.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const entitiesPath = join(root, 'entities.json');

if (!existsSync(entitiesPath)) {
  console.error(`entities.json not found at ${entitiesPath}`);
  process.exit(2);
}

const ALLOWED_ORIGINS = new Set([
  'consensus_engine_derived',
  'editorial_override',
  'accepted',
  'editorial_reconciliation',
  // wq-044: vc_subsidy fields are editorial-balance values that don't have
  // a single underlying claim (they're derived from a Sankey-balancing
  // judgment, not from data). Allow this origin so the wq-044 wire passes
  // the same provenance gate as collected_revenue.
  'editorial_balance_calculation',
]);

// Fields whose values must trace back to an allowed origin.
const TRACKED_FIELDS = ['collected_revenue', 'vc_subsidy'];

const data = JSON.parse(readFileSync(entitiesPath, 'utf8'));
const findings = [];

for (const company of data.companies ?? []) {
  const slug = company.slug ?? '<unknown>';
  const fin = company.financials ?? {};
  const prov = company.provenance ?? {};

  for (const [year, yearBlock] of Object.entries(fin)) {
    if (!yearBlock || typeof yearBlock !== 'object') continue;
    for (const field of TRACKED_FIELDS) {
      if (!(field in yearBlock)) continue;
      const value = yearBlock[field];
      if (value === null || value === undefined) continue;

      const provKey = `${year}.${field}`;
      const provBlock = prov[provKey];

      if (!provBlock || !Array.isArray(provBlock.claims) || provBlock.claims.length === 0) {
        findings.push({
          severity: 'fail',
          section: 'wq-048 §2 #10',
          ref: `${slug}.financials.${year}.${field}`,
          msg: `value=${value} has no provenance entry at provenance['${provKey}']`,
        });
        continue;
      }

      // At least one PRIMARY (non-superseded) claim must have an allowed origin.
      const primaryClaims = provBlock.claims.filter(c => c.role !== 'superseded');
      if (primaryClaims.length === 0) {
        findings.push({
          severity: 'fail',
          section: 'wq-048 §2 #10',
          ref: `${slug}.financials.${year}.${field}`,
          msg: `provenance['${provKey}'] has only superseded claims — no current attribution`,
        });
        continue;
      }
      const matchedOrigin = primaryClaims.find(c => ALLOWED_ORIGINS.has(c.origin));
      if (!matchedOrigin) {
        const seenOrigins = primaryClaims.map(c => c.origin || '<missing>').join(', ');
        findings.push({
          severity: 'fail',
          section: 'wq-048 §2 #10',
          ref: `${slug}.financials.${year}.${field}`,
          msg: `value=${value} provenance origins [${seenOrigins}] don't include any allowed origin (${[...ALLOWED_ORIGINS].join('|')})`,
        });
      }
    }
  }
}

const jsonOut = process.env.RELEASE_CHECK_CONSENSUS_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log(`✓ consensus-provenance: every ${TRACKED_FIELDS.join(' / ')} field has traceable provenance.`);
  process.exit(0);
}

console.log(`consensus-provenance: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.section} ${f.ref} — ${f.msg}`);
}

process.exit(1);
