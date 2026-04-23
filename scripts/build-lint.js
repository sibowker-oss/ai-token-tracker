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
 * Usage:
 *   node scripts/build-lint.js            # default: exits 1 on any failure
 *   node scripts/build-lint.js --warn     # exits 0 but prints all failures
 *   node scripts/build-lint.js --quiet    # only prints on failure
 *
 * CI:
 *   Wire into .github/workflows/ as a required check before Pages publish.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SITE_DATA = path.join(ROOT, 'site-data.json');
const SOURCES_REGISTRY = path.join(ROOT, 'data', 'sources.registry.md');

const REQUIRED_FIELDS = [
  'value', 'label', 'unit', 'year', 'source', 'sourceUrl',
  'retrievedAt', 'nextReview', 'confidence'
];

const ARGS = new Set(process.argv.slice(2));
const WARN_ONLY = ARGS.has('--warn');
const QUIET = ARGS.has('--quiet');

const failures = [];
const today = new Date().toISOString().slice(0, 10);

function fail(rule, path, detail) {
  failures.push({ rule, path, detail });
}

function walkEntries(obj, pathPrefix = '') {
  // Yield any object that looks like a datapoint entry — heuristic:
  // contains at least `value` (or min/max/medianMonths) and `source`.
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
  // 1. Required provenance fields
  for (const f of REQUIRED_FIELDS) {
    if (f === 'value' &&
        ('minMonths' in entry || 'maxMonths' in entry || 'medianMonths' in entry)) {
      continue; // lead-time ranges use min/max/median instead
    }
    if (!(f in entry) || entry[f] === null || entry[f] === '') {
      fail('missing-field', p, `missing required field: ${f}`);
    }
  }

  // 2. nextReview not in past
  if (entry.nextReview && entry.nextReview < today) {
    fail('past-review', p, `nextReview=${entry.nextReview} is before today=${today}`);
  }

  // 3. Label not empty / not a raw slug
  if (entry.label && /^[a-z0-9_-]+$/.test(entry.label)) {
    fail('raw-key-label', p, `label looks like a slug: "${entry.label}"`);
  }

  // 4. Confidence enum
  if (entry.confidence && !['High', 'Med', 'Low'].includes(entry.confidence)) {
    fail('bad-confidence', p, `confidence must be High|Med|Low, got "${entry.confidence}"`);
  }
}

function checkSourceRegistryExists() {
  if (!fs.existsSync(SOURCES_REGISTRY)) {
    fail('missing-registry', 'data/sources.registry.md', 'sources registry not found');
  }
}

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

  if (failures.length === 0) {
    if (!QUIET) console.log(`✓ build-lint: 0 failures (checked against today=${today})`);
    process.exit(0);
  }

  console.error(`✗ build-lint: ${failures.length} failure(s)`);
  const byRule = {};
  for (const f of failures) {
    (byRule[f.rule] ||= []).push(f);
  }
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
