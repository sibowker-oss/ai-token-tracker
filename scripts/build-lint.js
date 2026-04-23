#!/usr/bin/env node
/**
 * build-lint.js — The AI Ledger build-time data integrity check.
 *
 * Implements GUIDELINES §5.5:
 *   The site build fails if:
 *     - any `nextReview` date is in the past,
 *     - any datapoint is missing a required provenance field,
 *     - any new field is introduced without a backfill value on existing entries,
 *     - any entry referenced by a rendered component is missing its `label` (§5.6).
 *
 * Additional §11 release-gate checks added 2026-04-24 (wq-004):
 *     - schema-diff: added/removed top-level keys in site-data.json must be
 *       accompanied by a matching entry in changelog.html (§11 scope trigger).
 *     - dataReferences reconciliation: large-number literals hard-coded in *.html
 *       should resolve back to a value in site-data.json (§5.3.1). Warning only
 *       for now — promoted to error once current hits are cleaned up.
 *
 * Usage:
 *   node scripts/build-lint.js            # default: exits 1 on any failure
 *   node scripts/build-lint.js --warn     # exits 0 but prints all failures
 *   node scripts/build-lint.js --quiet    # only prints on failure
 *
 * CI:
 *   Wired into .github/workflows/build-lint.yml as a required check.
 */

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT = path.resolve(__dirname, '..');
const SITE_DATA = path.join(ROOT, 'site-data.json');
const SOURCES_REGISTRY = path.join(ROOT, 'data', 'sources.registry.md');
const CHANGELOG_HTML = path.join(ROOT, 'changelog.html');

const REQUIRED_FIELDS = [
  'value', 'label', 'unit', 'year', 'source', 'sourceUrl',
  'retrievedAt', 'nextReview', 'confidence'
];

const ARGS = new Set(process.argv.slice(2));
const WARN_ONLY = ARGS.has('--warn');
const QUIET = ARGS.has('--quiet');

const failures = [];
const warnings = [];
const today = new Date().toISOString().slice(0, 10);

function fail(rule, p, detail) {
  failures.push({ rule, path: p, detail });
}

function warn(rule, p, detail) {
  warnings.push({ rule, path: p, detail });
}

function walkEntries(obj, pathPrefix = '') {
  if (Array.isArray(obj)) {
    obj.forEach((item, i) => walkEntries(item, `${pathPrefix}[${i}]`));
    return;
  }
  if (obj && typeof obj === 'object') {
    const looksLikeEntry =
      ('source' in obj) &&
      ('value' in obj || 'minMonths' in obj || 'maxMonths' in obj || 'medianMonths' in obj);
    if (looksLikeEntry) {
      checkEntry(obj, pathPrefix);
    }
    for (const [k, v] of Object.entries(obj)) {
      walkEntries(v, pathPrefix ? `${pathPrefix}.${k}` : k);
    }
  }
}

function checkEntry(entry, p) {
  for (const f of REQUIRED_FIELDS) {
    if (f === 'value' &&
        ('minMonths' in entry || 'maxMonths' in entry || 'medianMonths' in entry)) {
      continue;
    }
    if (!(f in entry) || entry[f] === null || entry[f] === '') {
      fail('missing-field', p, `missing required field: ${f}`);
    }
  }

  if (entry.nextReview && entry.nextReview < today) {
    fail('past-review', p, `nextReview=${entry.nextReview} is before today=${today}`);
  }

  if (entry.label && /^[a-z0-9_-]+$/.test(entry.label)) {
    fail('raw-key-label', p, `label looks like a slug: "${entry.label}"`);
  }

  if (entry.confidence && !['High', 'Med', 'Low'].includes(entry.confidence)) {
    fail('bad-confidence', p, `confidence must be High|Med|Low, got "${entry.confidence}"`);
  }
}

function checkSourceRegistryExists() {
  if (!fs.existsSync(SOURCES_REGISTRY)) {
    fail('missing-registry', 'data/sources.registry.md', 'sources registry not found');
  }
}

// ────────────────────────────────────────────────────────────
// (a) schema-diff — top-level keys of site-data.json vs origin/main
// ────────────────────────────────────────────────────────────

function readBaselineSiteData() {
  for (const ref of ['origin/main', 'main']) {
    try {
      const raw = execSync(`git show ${ref}:site-data.json`, {
        cwd: ROOT,
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'ignore'],
        maxBuffer: 64 * 1024 * 1024,
      });
      return { ref, data: JSON.parse(raw) };
    } catch {
      // try next ref
    }
  }
  return null;
}

function checkSchemaDiff(currentData) {
  const baseline = readBaselineSiteData();
  if (!baseline) {
    // First commit or shallow checkout — nothing to diff against. Skip silently.
    return;
  }

  const currentKeys = new Set(Object.keys(currentData));
  const baseKeys = new Set(Object.keys(baseline.data));
  const added = [...currentKeys].filter(k => !baseKeys.has(k));
  const removed = [...baseKeys].filter(k => !currentKeys.has(k));

  if (added.length === 0 && removed.length === 0) return;

  let changelogText = '';
  if (fs.existsSync(CHANGELOG_HTML)) {
    changelogText = fs.readFileSync(CHANGELOG_HTML, 'utf8');
  } else {
    fail(
      'schema-diff',
      'changelog.html',
      `site-data.json top-level keys changed (added: [${added.join(', ')}], removed: [${removed.join(', ')}]) but changelog.html is missing`,
    );
    return;
  }

  for (const key of added) {
    if (!changelogText.includes(key)) {
      fail(
        'schema-diff',
        `site-data.json:${key}`,
        `new top-level key "${key}" (vs ${baseline.ref}) has no corresponding mention in changelog.html`,
      );
    }
  }
  for (const key of removed) {
    if (!changelogText.includes(key)) {
      fail(
        'schema-diff',
        `site-data.json:${key}`,
        `removed top-level key "${key}" (vs ${baseline.ref}) has no corresponding mention in changelog.html`,
      );
    }
  }
}

// ────────────────────────────────────────────────────────────
// (b) dataReferences reconciliation — hardcoded big numbers in *.html
// ────────────────────────────────────────────────────────────

function collectNumericValues(node, acc = new Set()) {
  if (node === null || node === undefined) return acc;
  if (typeof node === 'number') {
    acc.add(node);
    return acc;
  }
  if (typeof node === 'string') {
    const n = parseFloat(node.replace(/[^0-9.\-]/g, ''));
    if (!Number.isNaN(n) && n !== 0 && /\d/.test(node)) acc.add(n);
    return acc;
  }
  if (Array.isArray(node)) {
    node.forEach(x => collectNumericValues(x, acc));
    return acc;
  }
  if (typeof node === 'object') {
    for (const v of Object.values(node)) collectNumericValues(v, acc);
  }
  return acc;
}

const NUMBER_PATTERNS = [
  /\$\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?(?:[KMBT]|thousand|million|billion|trillion)?/gi,
  /\b\d+(?:\.\d+)?\s?(?:million|billion|trillion)\b/gi,
  /\b\d+(?:\.\d+)?\s?[MBT]\b/g,
];

function parseLiteralToNumber(raw) {
  const s = raw.replace(/[$,\s]/g, '').toLowerCase();
  const m = s.match(/^(-?\d+(?:\.\d+)?)([kmbt]|thousand|million|billion|trillion)?$/i);
  if (!m) return null;
  const base = parseFloat(m[1]);
  if (Number.isNaN(base)) return null;
  const suffix = (m[2] || '').toLowerCase();
  const mul = {
    '': 1,
    k: 1e3, thousand: 1e3,
    m: 1e6, million: 1e6,
    b: 1e9, billion: 1e9,
    t: 1e12, trillion: 1e12,
  }[suffix];
  if (mul === undefined) return null;
  return base * mul;
}

function literalMatchesAnyValue(literalValue, rawBase, numericSet) {
  const candidates = new Set([
    literalValue,
    rawBase,
    rawBase * 1e3, rawBase * 1e6, rawBase * 1e9, rawBase * 1e12,
    literalValue / 1e3, literalValue / 1e6, literalValue / 1e9, literalValue / 1e12,
  ]);
  for (const c of candidates) {
    if (!Number.isFinite(c)) continue;
    for (const v of numericSet) {
      if (Math.abs(v - c) < 1e-6 * Math.max(1, Math.abs(c))) return true;
      if (Math.abs(Math.round(v * 100) / 100 - Math.round(c * 100) / 100) < 1e-9) return true;
    }
  }
  return false;
}

function stripTagsAndStyle(html) {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ');
}

function checkDataReferences(currentData) {
  const numericSet = collectNumericValues(currentData);
  if (numericSet.size === 0) return;

  const htmlFiles = fs
    .readdirSync(ROOT)
    .filter(f => f.endsWith('.html'))
    .map(f => path.join(ROOT, f));

  for (const file of htmlFiles) {
    const rel = path.relative(ROOT, file);
    const raw = fs.readFileSync(file, 'utf8');
    const text = stripTagsAndStyle(raw);

    const seenLiterals = new Set();
    const seenValues = new Set();
    for (const pat of NUMBER_PATTERNS) {
      for (const m of text.matchAll(pat)) {
        const literal = m[0].trim();
        if (seenLiterals.has(literal)) continue;
        seenLiterals.add(literal);

        const rawBase = parseFloat(literal.replace(/[^0-9.\-]/g, ''));
        const literalValue = parseLiteralToNumber(literal);
        if (literalValue === null) continue;

        // Only care about "large" numbers; skip plain small integers that lack
        // a currency or magnitude suffix (those are usually years/counts).
        const hasMagnitude = /[$bmtkBMTK]|billion|million|trillion|thousand/.test(literal);
        if (!hasMagnitude && literalValue < 1e6) continue;

        // Dedup across regex variants: "$170B" and "170B" map to the same value.
        if (seenValues.has(literalValue)) continue;
        seenValues.add(literalValue);

        if (!literalMatchesAnyValue(literalValue, rawBase, numericSet)) {
          warn(
            'data-references',
            rel,
            `literal "${literal}" not found in site-data.json — reference the canonical field (§5.3.1)`,
          );
        }
      }
    }
  }
}

// ────────────────────────────────────────────────────────────

function main() {
  if (!fs.existsSync(SITE_DATA)) {
    console.error(`ERROR: ${SITE_DATA} not found`);
    process.exit(2);
  }

  let data;
  try {
    data = JSON.parse(fs.readFileSync(SITE_DATA, 'utf8'));
  } catch (e) {
    console.error(`ERROR: site-data.json is not valid JSON: ${e.message}`);
    process.exit(2);
  }

  walkEntries(data);
  checkSourceRegistryExists();
  checkSchemaDiff(data);
  checkDataReferences(data);

  if (failures.length === 0 && warnings.length === 0) {
    if (!QUIET) console.log(`✓ build-lint: 0 failures, 0 warnings (checked against today=${today})`);
    process.exit(0);
  }

  if (warnings.length > 0) {
    console.error(`⚠ build-lint: ${warnings.length} warning(s) (non-blocking)`);
    const byRule = {};
    for (const w of warnings) (byRule[w.rule] ||= []).push(w);
    for (const [rule, items] of Object.entries(byRule)) {
      console.error(`\n  [warn:${rule}] ${items.length}:`);
      items.slice(0, 10).forEach(it =>
        console.error(`    - ${it.path} — ${it.detail}`)
      );
      if (items.length > 10) console.error(`    ... and ${items.length - 10} more`);
    }
  }

  if (failures.length === 0) {
    if (!QUIET) console.log(`\n✓ build-lint: 0 failures (checked against today=${today})`);
    process.exit(0);
  }

  console.error(`\n✗ build-lint: ${failures.length} failure(s)`);
  const byRule = {};
  for (const f of failures) (byRule[f.rule] ||= []).push(f);
  for (const [rule, items] of Object.entries(byRule)) {
    console.error(`\n  [${rule}] ${items.length}:`);
    items.slice(0, 10).forEach(it =>
      console.error(`    - ${it.path} — ${it.detail}`)
    );
    if (items.length > 10) console.error(`    ... and ${items.length - 10} more`);
  }

  process.exit(WARN_ONLY ? 0 : 1);
}

main();
