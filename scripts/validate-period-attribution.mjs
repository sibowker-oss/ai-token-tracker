#!/usr/bin/env node
// scripts/validate-period-attribution.mjs
// wq-054 §3 #6 — assert no provenance entry on an annual field has claim
// text containing a sub-period qualifier without explanation. Catches
// regression where an extractor or manual edit silently writes a sub-period
// claim into an annual field path.
//
// Detection mirrors apply_decisions.py:detect_period_scope. A finding fires
// when:
//   1) prov_key implies annual scope (no _h1/_q3 suffix on year, no
//      exit_/monthly_peak_ prefix on field, year ≠ 'current')
//   2) claim text matches one of the sub-period qualifier patterns
//   3) claim does NOT have a stored time_period_scope of 'annual' OR a
//      `period_attribution_explained` note explaining why the qualifier
//      appears in annual-field text (e.g. comparison: "H1 grew 30% — full
//      year guidance still $20B").
//
// Severity: advisory by default (large pre-existing audit set documented
// in data/wq-054-existing-misroutes.md). Promotes to fail when CHECK_MODE
// is strict OR when the offender is a NEWLY accepted claim (origin=accepted
// AND date >= STRICT_AFTER).

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const STRICT_AFTER = '2026-06-01';
const STRICT_MODE = (process.env.CHECK_MODE === 'strict');

const QUALIFIER_REGEXES = [
  ['exit_snapshot', /\bexit\s+arr\b|year[\-\s]?end\s+(run[\-\s]?rate|arr)|as\s+of\s+(dec|december)|best[\-\s]?(4|four)[\-\s]?week/i],
  ['monthly_peak',  /\bmonthly\s+peak\b|\bper\s+month\b|single\s+month\s+(peak|run[\-\s]?rate)|\$\d+(\.\d+)?[MB]?\s*\/\s*month/i],
  ['q1', /\bQ1\b|first\s+quarter/i],
  ['q2', /\bQ2\b|second\s+quarter/i],
  ['q3', /\bQ3\b|third\s+quarter/i],
  ['q4', /\bQ4\b|fourth\s+quarter/i],
  ['h1', /\bH1\b|first\s+half|jan(uary)?\s*[-–to]+\s*jun/i],
  ['h2', /\bH2\b|second\s+half|jul(y)?\s*[-–to]+\s*dec/i],
];

function detectScope(text) {
  if (!text) return null;
  for (const [scope, re] of QUALIFIER_REGEXES) {
    if (re.test(text)) return scope;
  }
  return null;
}

function impliedScope(year_part, field_part) {
  if (year_part === 'current') return 'point_in_time';
  if (year_part && year_part.includes('_')) {
    const suffix = year_part.split('_')[1];
    if (['h1','h2','q1','q2','q3','q4'].includes(suffix)) return suffix;
  }
  if (field_part.startsWith('exit_')) return 'exit_snapshot';
  if (field_part.startsWith('monthly_peak_')) return 'monthly_peak';
  return 'annual';
}

const findings = [];
const entitiesPath = join(root, 'entities.json');

if (!existsSync(entitiesPath)) {
  findings.push({ severity: 'fail', file: 'entities.json', msg: 'file not found' });
} else {
  const ent = JSON.parse(readFileSync(entitiesPath, 'utf8'));
  let scanned = 0, flaggedNew = 0, flaggedLegacy = 0;

  for (const c of (ent.companies || [])) {
    const slug = c.slug;
    const prov = c.provenance || {};
    for (const [key, block] of Object.entries(prov)) {
      if (!key.includes('.')) continue;
      const [yearPart, fieldPart] = [key.split('.')[0], key.split('.').slice(1).join('.')];
      const implied = impliedScope(yearPart, fieldPart);
      for (const claim of (block.claims || [])) {
        scanned++;
        const stored = claim.time_period_scope;
        if (stored && stored !== 'annual' && stored !== implied) {
          // Stored scope contradicts the field path — definite misroute.
          const isNew = (claim.origin === 'accepted' || claim.origin === 'consensus_engine_derived')
            && (claim.date || '') >= STRICT_AFTER;
          const sev = (STRICT_MODE || isNew) ? 'fail' : 'advisory';
          (sev === 'fail') ? flaggedNew++ : flaggedLegacy++;
          findings.push({
            severity: sev,
            file: 'entities.json',
            msg: `${slug}.${key}: stored scope "${stored}" but field path implies "${implied}" (claim ${claim.id})`,
          });
          continue;
        }
        if (stored === 'annual' || stored === implied) continue;
        // Fall back to text detection
        const detected = detectScope(claim.claim || '');
        if (!detected) continue;
        if (detected === implied) continue;
        // Skip claims that explicitly note period explanation
        if ((claim.period_attribution_explained || '').length > 0) continue;
        const isNew = (claim.origin === 'accepted' || claim.origin === 'consensus_engine_derived')
          && (claim.date || '') >= STRICT_AFTER;
        const sev = (STRICT_MODE || isNew) ? 'fail' : 'advisory';
        (sev === 'fail') ? flaggedNew++ : flaggedLegacy++;
        findings.push({
          severity: sev,
          file: 'entities.json',
          msg: `${slug}.${key}: claim text contains "${detected}" qualifier but field is annual (claim ${claim.id})`,
        });
      }
    }
  }

  findings.push({
    severity: 'advisory',
    file: 'entities.json',
    msg: `scanned ${scanned} claims · ${flaggedNew} fail(s) · ${flaggedLegacy} advisory legacy · strict-after ${STRICT_AFTER} · CHECK_MODE=${process.env.CHECK_MODE || 'advisory'}`,
  });
}

const jsonOut = process.env.RELEASE_CHECK_PERIOD_ATTRIBUTION_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

const fails = findings.filter(f => f.severity === 'fail').length;
const advisories = findings.filter(f => f.severity === 'advisory').length;

if (fails === 0 && advisories <= 1) {
  console.log('✓ period-attribution: no sub-period claims found on annual field paths.');
  process.exit(0);
}
console.log(`period-attribution: ${fails} fail · ${advisories} advisory`);
for (const f of findings.slice(0, 50)) {
  console.log(`  [${f.severity.padEnd(8)}] ${f.file} — ${f.msg}`);
}
if (findings.length > 50) {
  console.log(`  …${findings.length - 50} more — see ${jsonOut || 'RELEASE_CHECK_PERIOD_ATTRIBUTION_JSON_OUT'}`);
}
process.exit(fails > 0 ? 1 : 0);
