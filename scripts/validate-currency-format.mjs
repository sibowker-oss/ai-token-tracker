#!/usr/bin/env node
// scripts/validate-currency-format.mjs
// wq-076 §3 #6 — assert no excess-decimal dollar literals leak into HTML.
//
// Catches accidental `$1234.56B`, `$0.95B` (should be `$950M`), `$176.48B`
// (should be `$176B` per formatCurrency rule). Scans wq-076-wired pages for
// patterns that bypass formatCurrency:
//   $\d+\.\d{2,}B    (two or more decimal places — never produced by formatCurrency)
//
// Excludes: comments (//, /* */), inline strings inside obvious provenance text,
// data attribute values, and the FALLBACK_FLOWS comment block in capital.html.
//
// Skipped intentionally: follow-the-trillion.html (uses T-scale formatter
// outside formatCurrency's design range; brief §6 out-of-scope).

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();

// Pages that should use formatCurrency for all dollar displays.
const WATCHED_PAGES = [
  'capital.html',
  'revenue.html',
  'index.html',
  'ipo-watch.html',
];

// Pattern: $123.45B or $1.234B etc — two-or-more decimal places signals
// formatCurrency was bypassed (formatCurrency only ever produces 0 or 1 decimal).
const EXCESS_DECIMAL = /\$\d{1,4}\.\d{2,}\s*B\b/;

const findings = [];

for (const file of WATCHED_PAGES) {
  const path = join(root, file);
  if (!existsSync(path)) {
    findings.push({ severity: 'fail', file, msg: 'file not found' });
    continue;
  }
  const lines = readFileSync(path, 'utf8').split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Skip comment-only lines
    if (/^\s*\/\//.test(line) || /^\s*\*/.test(line)) continue;
    // Skip provenance / data block lines that may contain literal historical numbers
    if (/"src"\s*:|"claim"\s*:|"reason"\s*:|"_doc"\s*:/.test(line)) continue;
    if (EXCESS_DECIMAL.test(line)) {
      // Capture the matching literal for the message
      const m = line.match(/\$\d{1,4}\.\d{2,}\s*B\b/g) || [];
      findings.push({
        severity: 'fail',
        file,
        line: i + 1,
        msg: `excess-decimal literal(s) ${m.join(', ')} — should use formatCurrency() (rounds ≥$10B to integer, $1-10B to one decimal, <$1B to M)`,
      });
    }
  }
  // Verify format-helpers.js is loaded on every watched page.
  const text = lines.join('\n');
  if (!/data\/format-helpers\.js/.test(text)) {
    findings.push({
      severity: 'fail',
      file,
      msg: 'data/format-helpers.js not loaded — formatCurrency() will be undefined',
    });
  }
}

const jsonOut = process.env.RELEASE_CHECK_CURRENCY_FORMAT_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ currency-format: no excess-decimal dollar literals; format-helpers.js loaded everywhere expected.');
  process.exit(0);
}
console.log(`currency-format: ${findings.length} fail`);
for (const f of findings) {
  const loc = f.line ? `${f.file}:${f.line}` : f.file;
  console.log(`  [${f.severity.padEnd(4)}] ${loc} — ${f.msg}`);
}
process.exit(1);
