#!/usr/bin/env node
// validate-pipeline-health-freshness.mjs
// wq-099 §2 Validators — assert data/pipeline-health-latest.json exists and
// is no more than 30 hours old. Catches the case where reconcile_pipeline.py
// silently stops running (broken cron / crashed step / missing dependency).
//
// Output JSON shape matches the other release-check validators so the
// release-check.mjs aggregator can render findings the same way.

import { readFileSync, existsSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { writeFileSync } from 'node:fs';

const ROOT = process.cwd();
const HEALTH_PATH = join(ROOT, 'data', 'pipeline-health-latest.json');
const STALE_HOURS = 30;
const findings = [];

function fail(section, ref, msg) {
  findings.push({ section, ref, severity: 'fail', msg });
}

if (!existsSync(HEALTH_PATH)) {
  fail(
    'pipeline-health',
    'data/pipeline-health-latest.json',
    'File missing — reconcile_pipeline.py has not produced a snapshot. ' +
    'Run `python3 scripts/reconcile_pipeline.py` or check the auto_update.py cron.'
  );
} else {
  let asOfMs = null;
  let alertCount = null;
  try {
    const raw = JSON.parse(readFileSync(HEALTH_PATH, 'utf8'));
    asOfMs = raw.asOf ? Date.parse(raw.asOf) : null;
    alertCount = raw.alertCount ?? null;
  } catch (e) {
    fail(
      'pipeline-health',
      'data/pipeline-health-latest.json',
      'Snapshot is not valid JSON: ' + e.message
    );
  }

  // Prefer the asOf timestamp inside the snapshot; fall back to file mtime
  // if asOf is missing or unparseable.
  const refMs = Number.isFinite(asOfMs) ? asOfMs : statSync(HEALTH_PATH).mtimeMs;
  const ageHrs = (Date.now() - refMs) / 3600000;
  if (ageHrs > STALE_HOURS) {
    fail(
      'pipeline-health',
      'data/pipeline-health-latest.json',
      `Snapshot is ${ageHrs.toFixed(1)}h old (>${STALE_HOURS}h ceiling). ` +
      'reconcile_pipeline.py may have stopped running.'
    );
  }

  if (alertCount !== null && alertCount > 0) {
    fail(
      'pipeline-health',
      'data/pipeline-health-latest.json',
      `${alertCount} reconciliation alert(s) active. See ` +
      'status.html#pipeline and the latest data/audits/pipeline-alerts-*.md.'
    );
  }
}

const outPath = process.env.RELEASE_CHECK_PIPELINE_HEALTH_JSON_OUT;
if (outPath) {
  writeFileSync(resolve(outPath), JSON.stringify(findings, null, 2));
}

if (findings.length === 0) {
  console.log('[pass] pipeline-health-freshness — snapshot fresh, no active alerts.');
  process.exit(0);
} else {
  for (const f of findings) {
    console.log(`[${f.severity}] ${f.section} — ${f.ref} — ${f.msg}`);
  }
  // Advisory: never block release-check overall. Aggregator decides.
  process.exit(0);
}
