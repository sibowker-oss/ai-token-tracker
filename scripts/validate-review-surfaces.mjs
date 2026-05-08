// validate-review-surfaces.mjs — wq-100 §2 Validators.
//
// Asserts:
//   1. claims.html and review.html no longer contain a browser-download
//      submit path (no `a.download = 'approved-claims.json'` etc.).
//   2. apply_pipeline.py imports the variance gate and apply_handlers/
//      _variance_gate.py exists with all four D3 conditions.
//   3. admin_server.py registers POST /api/decision and POST /api/override.
//   4. data/apply_log.json is well-formed when present (forward-compat for
//      the wq-099 dashboard counters).
//
// Output schema (matches sibling validators):
//   [ { name: 'browser-download-removed', severity: 'fail' | 'pass',
//       detail: '...' }, ... ]

import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(__dirname);

const findings = [];

function add(name, severity, detail) {
  findings.push({ name, severity, detail });
}

// 1. Browser-download path removed from both UIs.
for (const file of ['claims.html', 'review.html']) {
  const path = join(ROOT, file);
  if (!existsSync(path)) {
    add('browser-download-removed', 'fail', `${file} not found`);
    continue;
  }
  const src = readFileSync(path, 'utf8');
  // The submit handoff that wq-100 eliminated was the `approved-claims.json`
  // download from claims.html. The `exportDecisions()` user-export utility
  // is allowed to keep its own download (explicit user action, not a
  // submit-path handoff). Our check fails only on the legacy submit
  // handoff and on either submit function still NOT calling fetch().
  const forbidden = [
    /a\.download\s*=\s*['"]approved-claims\.json['"]/,
  ];
  const hits = forbidden.filter(re => re.test(src));
  // Sanity: writeApproved / writeApprovedClaims must POST to admin_server.py.
  const submitFn = src.match(/(?:async\s+)?function\s+writeApproved(?:Claims)?\s*\(/);
  if (submitFn) {
    const body = src.slice(submitFn.index, submitFn.index + 4000);
    if (!/fetch\(['"]http:\/\/localhost:8080\/api\/decision['"]/.test(body)) {
      hits.push({ source: 'submit-fn-missing-admin-server-fetch' });
    }
  }
  if (hits.length) {
    const detail = hits.map(h => typeof h === 'object' ? h.source : h.source || String(h)).join(', ');
    add('browser-download-removed', 'fail',
        `${file} still contains a browser-download submit path: ${detail}`);
  } else {
    add('browser-download-removed', 'pass',
        `${file} submit path uses admin_server.py POST`);
  }
}

// 2. Variance gate module + import.
const vgPath = join(ROOT, 'scripts', 'apply_handlers', '_variance_gate.py');
if (!existsSync(vgPath)) {
  add('variance-gate-present', 'fail',
      'scripts/apply_handlers/_variance_gate.py missing');
} else {
  const vg = readFileSync(vgPath, 'utf8');
  const required = [
    /VARIANCE_AUTO_APPLY\s*=\s*0\.15/,
    /VARIANCE_ANOMALY\s*=\s*0\.50/,
    /ABS_FLOOR_B\s*=\s*0\.05/,
    /def\s+evaluate\s*\(/,
  ];
  const missing = required.filter(re => !re.test(vg));
  if (missing.length) {
    add('variance-gate-present', 'fail',
        `_variance_gate.py missing constants: ${missing.map(r => r.source).join(', ')}`);
  } else {
    add('variance-gate-present', 'pass',
        '_variance_gate.py exports D3/D4/D5 constants and evaluate()');
  }
}

const apPath = join(ROOT, 'scripts', 'apply_pipeline.py');
if (existsSync(apPath)) {
  const ap = readFileSync(apPath, 'utf8');
  if (!/_variance_gate as VG/.test(ap) && !/import\s+_variance_gate/.test(ap)) {
    add('variance-gate-wired', 'fail',
        'apply_pipeline.py does not import _variance_gate');
  } else if (!/apply_variance_gate\s*\(/.test(ap)) {
    add('variance-gate-wired', 'fail',
        'apply_pipeline.py imports the gate but does not call apply_variance_gate()');
  } else {
    add('variance-gate-wired', 'pass',
        'apply_pipeline.py invokes apply_variance_gate() on each run');
  }
}

// 3. admin_server.py registers the new endpoints.
const adminPath = join(ROOT, 'scripts', 'admin_server.py');
if (existsSync(adminPath)) {
  const admin = readFileSync(adminPath, 'utf8');
  const checks = [
    [/['"]\/api\/decision['"]/, '/api/decision endpoint'],
    [/['"]\/api\/override['"]/, '/api/override endpoint'],
    [/def\s+handle_decision\s*\(/, 'handle_decision()'],
    [/def\s+handle_override\s*\(/, 'handle_override()'],
  ];
  const missing = checks.filter(([re]) => !re.test(admin)).map(([, name]) => name);
  if (missing.length) {
    add('admin-server-endpoints', 'fail',
        `admin_server.py missing: ${missing.join(', ')}`);
  } else {
    add('admin-server-endpoints', 'pass',
        'admin_server.py registers /api/decision and /api/override');
  }
}

// 4. apply_log.json shape (forward-compat for wq-099 dashboard).
const applyLogPath = join(ROOT, 'data', 'apply_log.json');
if (existsSync(applyLogPath)) {
  try {
    const log = JSON.parse(readFileSync(applyLogPath, 'utf8'));
    const required = ['lastUpdated', 'runs', 'counters_30d'];
    const missing = required.filter(k => !(k in log));
    if (missing.length) {
      add('apply-log-shape', 'fail',
          `data/apply_log.json missing keys: ${missing.join(', ')}`);
    } else if (!Array.isArray(log.runs)) {
      add('apply-log-shape', 'fail',
          'data/apply_log.json runs is not an array');
    } else {
      add('apply-log-shape', 'pass',
          `data/apply_log.json has ${log.runs.length} run(s) recorded`);
    }
  } catch (e) {
    add('apply-log-shape', 'fail',
        `data/apply_log.json failed to parse: ${e.message}`);
  }
} else {
  // Advisory — apply_log.json is created on first apply_pipeline.py run.
  add('apply-log-shape', 'advisory',
      'data/apply_log.json not present yet (first apply_pipeline.py run will create it)');
}

const out = process.env.RELEASE_CHECK_REVIEW_SURFACES_JSON_OUT;
if (out) {
  const { writeFileSync, mkdirSync } = await import('node:fs');
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, JSON.stringify(findings, null, 2));
}

const fails = findings.filter(f => f.severity === 'fail');
for (const f of findings) {
  console.log(`  [${f.severity}] ${f.name}: ${f.detail}`);
}
if (fails.length) {
  console.error(`\n${fails.length} review-surfaces validation failure(s).`);
  process.exit(1);
}
console.log('\n✓ review-surfaces validation passed');
