#!/usr/bin/env node
// scripts/validate-telemetry-routing.mjs
// wq-047 §3 #7 — assert no operational-telemetry items leak into vault-inbox.json.
//
// After 2026-06-01 the validator emits FAIL findings for any vault-inbox item
// that matches the telemetry routing rules from scripts/_telemetry_router.py.
// Before that date the same items emit ADVISORY (transition window — existing
// items grandfathered, new items expected to route via _telemetry_router).
//
// Detection rules (mirror _telemetry_router.py:is_telemetry):
//   - sourceType ∈ TELEMETRY_SOURCE_TYPES
//   - metricKey ∈ TELEMETRY_METRIC_KEYS
//   - metricKey starts with "X-" or ends with "_downloads"
//   - type ∈ TELEMETRY_STRUCTURED_TYPES (hiring/patent/power_project)
//
// Items already accepted/archived/rejected are skipped — only `pending` and
// `raw_pool` items count, since those are the queue Simon would actually see.

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const STRICT_AFTER = '2026-06-01';
const today = new Date().toISOString().slice(0, 10);
const STRICT = today >= STRICT_AFTER;

const TELEMETRY_SOURCE_TYPES = new Set([
  'ats_api', 'package_index', 'github_repo', 'sec_filing', 'patent_index', 'permit_db',
]);
const TELEMETRY_METRIC_KEYS = new Set([
  'X-hiring_snapshot', 'X-patent_snapshot', 'X-power_project',
  'pypi_downloads', 'npm_downloads', 'docker_pulls',
  'github_stars', 'recent_filings',
]);
const TELEMETRY_STRUCTURED_TYPES = new Set([
  'hiring_snapshot', 'patent_snapshot', 'power_project',
]);

function isTelemetry(item) {
  if (TELEMETRY_STRUCTURED_TYPES.has(item.type || '')) return true;
  if (TELEMETRY_SOURCE_TYPES.has(item.sourceType || '')) return true;
  const m = item.metricKey || '';
  if (TELEMETRY_METRIC_KEYS.has(m)) return true;
  if (m.startsWith('X-')) return true;
  if (m.endsWith('_downloads')) return true;
  return false;
}

const findings = [];
const inboxPath = join(root, 'vault-inbox.json');

if (!existsSync(inboxPath)) {
  findings.push({ severity: 'fail', file: 'vault-inbox.json', msg: 'file not found' });
} else {
  const inbox = JSON.parse(readFileSync(inboxPath, 'utf8'));
  const items = inbox.items || [];
  const queueable = items.filter(it => it.status === 'pending' || it.status === 'raw_pool');
  const offenders = queueable.filter(isTelemetry);

  if (offenders.length > 0) {
    const severity = STRICT ? 'fail' : 'advisory';
    // Group by source_id for cleaner output
    const bySource = new Map();
    for (const it of offenders) {
      const k = it.source_id || '(unknown)';
      bySource.set(k, (bySource.get(k) || 0) + 1);
    }
    for (const [src, n] of bySource) {
      findings.push({
        severity,
        file: 'vault-inbox.json',
        msg: `${n} telemetry item(s) from ${src} routed to inbox instead of data/telemetry-feed.json (wq-047)`,
      });
    }
    findings.push({
      severity: 'advisory',
      file: 'vault-inbox.json',
      msg: `mode: ${STRICT ? 'STRICT' : `transitional until ${STRICT_AFTER}`} · ${offenders.length} total offender(s) across ${bySource.size} source(s)`,
    });
  }
}

const jsonOut = process.env.RELEASE_CHECK_TELEMETRY_ROUTING_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

const fails = findings.filter(f => f.severity === 'fail').length;
const advisories = findings.filter(f => f.severity === 'advisory').length;

if (findings.length === 0) {
  console.log('✓ telemetry-routing: no telemetry items in vault-inbox.json (wq-047 §3 #7).');
  process.exit(0);
}
console.log(`telemetry-routing: ${fails} fail · ${advisories} advisory`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(8)}] ${f.file} — ${f.msg}`);
}
process.exit(fails > 0 ? 1 : 0);
