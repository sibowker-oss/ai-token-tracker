#!/usr/bin/env node
// scripts/validate-provenance.mjs
// Enforces GUIDELINES.md §4.2, §4.4, §4.5, §5.2, §5.5, §5.6 against site-data.json.
// Standalone — no Playwright. Used by:
//   - `npm run release-check:provenance`
//   - the §5.5 build lint (supersedes scripts/build-lint.js)
//   - the release-check subagent (step 1 of the scripted suite)
//
// Exit codes:
//   0 — no findings
//   1 — findings present (CLI wrapper in release-check.mjs rewrites to 0 for advisory mode)

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const REQUIRED_FIELDS = ['value', 'label', 'unit', 'year', 'source', 'sourceUrl', 'retrievedAt', 'nextReview', 'confidence'];
const VALID_CONFIDENCE = new Set(['High', 'Med', 'Low']);
const RANGE_FIELDS = ['minMonths', 'maxMonths', 'medianMonths'];

const root = process.cwd();
const dataPath = process.env.RELEASE_CHECK_DATA ?? join(root, 'site-data.json');
const registryPath = join(root, 'data', 'sources.registry.md');

if (!existsSync(dataPath)) {
  console.error(`site-data.json not found at ${dataPath}`);
  process.exit(2);
}

const data = JSON.parse(readFileSync(dataPath, 'utf8'));
const registryText = existsSync(registryPath) ? readFileSync(registryPath, 'utf8') : '';

const findings = [];
const today = new Date().toISOString().slice(0, 10);

function walk(node, path = []) {
  if (node === null || typeof node !== 'object') return;
  if (Array.isArray(node)) {
    node.forEach((item, i) => walk(item, [...path, i]));
    return;
  }
  if (isDatapoint(node)) {
    validateDatapoint(node, path);
    return;
  }
  for (const [k, v] of Object.entries(node)) walk(v, [...path, k]);
}

function isDatapoint(node) {
  // A datapoint has at least one of: value, or all RANGE_FIELDS, plus a source field.
  if (!node || typeof node !== 'object') return false;
  const hasValue = 'value' in node;
  const hasRange = RANGE_FIELDS.every(f => f in node);
  const hasSource = 'source' in node || 'sources' in node;
  return (hasValue || hasRange) && hasSource;
}

function validateDatapoint(dp, path) {
  const ref = path.join('.') || '<root>';

  // §4.2 required fields
  const isRange = RANGE_FIELDS.every(f => f in dp);
  const required = isRange
    ? ['label', 'unit', 'year', 'sources', 'retrievedAt', 'nextReview', 'confidence']
    : REQUIRED_FIELDS;
  for (const field of required) {
    if (!(field in dp) || dp[field] === null || dp[field] === '') {
      findings.push({ severity: 'fail', section: '§4.2', ref, msg: `missing required field "${field}"` });
    }
  }

  // §4.4 confidence enum
  if (dp.confidence && !VALID_CONFIDENCE.has(dp.confidence)) {
    findings.push({ severity: 'fail', section: '§4.4', ref, msg: `confidence "${dp.confidence}" not in High/Med/Low` });
  }

  // §5.5 nextReview not in past
  if (dp.nextReview && dp.nextReview < today) {
    findings.push({ severity: 'fail', section: '§5.5', ref, msg: `nextReview ${dp.nextReview} is in the past (today ${today})` });
  }

  // §4.2 ISO date shape
  for (const dateField of ['retrievedAt', 'nextReview']) {
    if (dp[dateField] && !/^\d{4}-\d{2}-\d{2}$/.test(dp[dateField])) {
      findings.push({ severity: 'fail', section: '§4.2', ref, msg: `${dateField} "${dp[dateField]}" is not ISO YYYY-MM-DD` });
    }
  }

  // §4.5 revenue entries must declare booked vs run-rate
  const looksLikeRevenue = /revenue|arr/i.test(ref) || (dp.unit === 'USD' && /revenue|arr/i.test(dp.label ?? ''));
  if (looksLikeRevenue && !('revenueType' in dp)) {
    findings.push({
      severity: 'fail',
      section: '§4.5',
      ref,
      msg: 'revenue entry missing revenueType ("booked_ttm" | "run_rate"). ARR and booked revenue are not interchangeable.',
    });
  }

  // §5.6 label must be human-readable (not a slug / key)
  if (dp.label && /^[a-z0-9_-]+$/i.test(dp.label) && !dp.label.includes(' ')) {
    findings.push({
      severity: 'fail',
      section: '§5.6',
      ref,
      msg: `label "${dp.label}" looks like a raw key — must be publish-ready (has spaces, title case).`,
    });
  }

  // Cross-check: sourceUrl points at something plausibly primary
  if (dp.sourceUrl && !/^https?:\/\//.test(dp.sourceUrl)) {
    findings.push({ severity: 'fail', section: '§4.2', ref, msg: `sourceUrl "${dp.sourceUrl}" is not an http(s) URL` });
  }

  // §11.2 — source is registered in data/sources.registry.md
  if (dp.source && registryText && !registryText.includes(dp.source)) {
    findings.push({
      severity: 'advisory',
      section: '§5.4 / §11.2',
      ref,
      msg: `source "${dp.source}" not found in data/sources.registry.md — register it before promotion.`,
    });
  }
}

// §5.3.1 — dataReferences map integrity check
if (data.meta?.dataReferences) {
  for (const [canonicalKey, consumers] of Object.entries(data.meta.dataReferences)) {
    if (!resolveByDottedKey(data, canonicalKey)) {
      findings.push({
        severity: 'fail',
        section: '§5.3.1',
        ref: `meta.dataReferences.${canonicalKey}`,
        msg: `canonical key "${canonicalKey}" declared in dataReferences but missing from site-data.json`,
      });
    }
    if (!Array.isArray(consumers) || consumers.length === 0) {
      findings.push({
        severity: 'advisory',
        section: '§5.3.1',
        ref: `meta.dataReferences.${canonicalKey}`,
        msg: 'no consumers listed — if unused, remove from dataReferences.',
      });
    }
  }
} else {
  findings.push({
    severity: 'advisory',
    section: '§5.3.1',
    ref: 'meta.dataReferences',
    msg: 'dataReferences map absent from site-data.json.meta — required once more than one page reads from the same field.',
  });
}

function resolveByDottedKey(root, key) {
  return key.split('.').reduce((node, part) => (node == null ? undefined : node[part]), root) !== undefined;
}

walk(data);

// Output
const fails = findings.filter(f => f.severity === 'fail');
const advisories = findings.filter(f => f.severity === 'advisory');

if (findings.length === 0) {
  console.log('✓ provenance validator: all checks passed.');
  process.exit(0);
}

console.log(`provenance validator: ${fails.length} fail, ${advisories.length} advisory`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(9)}] ${f.section} ${f.ref} — ${f.msg}`);
}

// Machine-readable for the CLI wrapper
if (process.env.RELEASE_CHECK_JSON_OUT) {
  const { writeFileSync } = await import('node:fs');
  writeFileSync(process.env.RELEASE_CHECK_JSON_OUT, JSON.stringify(findings, null, 2));
}

process.exit(fails.length > 0 ? 1 : 0);
