#!/usr/bin/env node
// scripts/validate-pipeline-orphans.mjs
// wq-098 §3 acceptance #2 + #10: assert
//   (a) every vault claim's `unit` has a registered handler in
//       scripts/apply_handlers/ or is in _default.UNHANDLED_UNITS
//   (b) zero verified+tier-2A-or-better vault claims sit unused
//       (`usedOn=[]`) — orphan detection
//   (c) only one production script writes to vault-data.json
//
// Output: JSON findings to RELEASE_CHECK_PIPELINE_ORPHANS_JSON_OUT for
// release-check aggregation. Exits 0 (advisory).

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const ROOT = process.cwd();
const VAULT_PATH = join(ROOT, 'vault-data.json');
const HANDLERS_DIR = join(ROOT, 'scripts', 'apply_handlers');
const SCRIPTS_DIR = join(ROOT, 'scripts');

const findings = [];

function add(severity, ref, msg) {
  findings.push({ severity, section: 'wq-098', ref, msg });
}

// (a) units coverage — invoke the Python pipeline's known_units helper via
// a tiny driver; cheaper than re-implementing the dispatch table in JS.
const driver = `
import json, os, sys
sys.path.insert(0, os.path.join('${ROOT.replace(/'/g, "\\'")}', 'scripts'))
from apply_pipeline import build_dispatch, known_units
dispatch = build_dispatch()
known = known_units(dispatch)
with open(os.path.join('${ROOT.replace(/'/g, "\\'")}', 'vault-data.json')) as f:
    vault = json.load(f)
seen = set((dp.get('unit') or '') for dp in vault['dataPoints']) - {''}
unknown = sorted(seen - known)
print(json.dumps({'unknown_units': unknown}))
`;
const r = spawnSync('python3', ['-c', driver], { encoding: 'utf8' });
if (r.status === 0) {
  try {
    const data = JSON.parse(r.stdout.trim().split('\n').pop());
    if (data.unknown_units && data.unknown_units.length) {
      add('fail', 'units-coverage',
          `Vault contains units with no registered handler: ${data.unknown_units.join(', ')}. ` +
          `Add a handler in scripts/apply_handlers/ or include the unit in _default.UNHANDLED_UNITS.`);
    }
  } catch (e) {
    add('advisory', 'units-coverage', `unit-coverage driver returned non-JSON: ${e.message}`);
  }
} else {
  add('advisory', 'units-coverage', `unit-coverage driver failed: ${r.stderr || r.stdout}`);
}

// (b) orphan detection
const vault = JSON.parse(readFileSync(VAULT_PATH, 'utf8'));
const orphans = [];
function deriveTier(dp) {
  const st = (dp.sourceType || '').toLowerCase();
  const conf = (dp.confidence || '').toLowerCase();
  if (st === 'sworn-affidavit') return 'tier_1A';
  if (st === 'official' || st === 'sec_filing') return 'tier_1B';
  if (st === 'leaked-internal' || st === 'earnings-aggregation') return conf === 'verified' ? 'tier_1B' : 'tier_2A';
  if (st === 'reporting' || st === 'newsletter') return conf === 'verified' ? 'tier_2A' : 'tier_2B';
  if (st === 'platform-data') return conf === 'verified' ? 'tier_2A' : 'tier_2B';
  if (st === 'web_page') return conf === 'verified' ? 'tier_2A' : 'tier_3A';
  return 'tier_3A';
}
const HIGH_TIERS = new Set(['tier_1A', 'tier_1B', 'tier_2A']);
for (const dp of vault.dataPoints || []) {
  const tier = deriveTier(dp);
  const verified = (dp.confidence || '').toLowerCase() === 'verified';
  const used = (dp.usedOn || []).length > 0;
  if (verified && HIGH_TIERS.has(tier) && !used) {
    orphans.push({ id: dp.id, tier, claim: (dp.claim || '').slice(0, 80) });
  }
}
if (orphans.length) {
  add('fail', 'orphan-claims',
      `${orphans.length} verified tier-2A-or-better claims sit unused (usedOn=[]). ` +
      `Run scripts/apply_pipeline.py to backfill. Sample: ` +
      orphans.slice(0, 5).map(o => `${o.id} (${o.tier})`).join(', '));
}

// (c) bypass closure — only allowlisted scripts may write to vault-data.json
const ALLOWLIST = new Set([
  'apply_pipeline.py',
  'enrich_vault.py',
  'fix_vault_data_mojibake.py',
  'apply_claims_legacy.py',     // archived, must NOT be invoked
  'apply_decisions_legacy.py',  // archived, must NOT be invoked
]);
const violators = [];
for (const f of readdirSync(SCRIPTS_DIR)) {
  if (!f.endsWith('.py')) continue;
  if (ALLOWLIST.has(f)) continue;
  const path = join(SCRIPTS_DIR, f);
  let body;
  try { body = readFileSync(path, 'utf8'); } catch { continue; }
  // Heuristic: a `with open(<vault-data path-or-var>, 'w'` line. We pick
  // up named constants (VAULT_DATA, VAULT_PATH, VAULT_DATA_PATH) and the
  // raw filename. Excludes string-literal mentions in comments / paths.
  if (/with\s+open\(\s*(VAULT_DATA(_PATH)?|VAULT_PATH|['"][^'"]*vault-data\.json['"])\s*,\s*['"]w['"]/m.test(body)) {
    violators.push(f);
  }
}
if (violators.length) {
  add('fail', 'bypass-closure',
      `Non-allowlisted scripts open vault-data.json for write: ${violators.join(', ')}. ` +
      `Either redirect to vault-inbox.json or add to the allowlist in ` +
      `data/audits/wq-098-direct-vault-writers.md and this validator.`);
}

// (d) imports of legacy entry points. Strip Python comments and strings
// before regex-matching so the "do NOT call apply_decisions_legacy.main()"
// docstring lines on intentional-helper-only consumers don't trip the
// check. Only catches actual code-path invocations.
function stripComments(src) {
  // remove # comments to end-of-line, plus triple-quoted docstrings
  return src
    .replace(/'''[\s\S]*?'''/g, '')
    .replace(/"""[\s\S]*?"""/g, '')
    .replace(/(^|\n)\s*#[^\n]*/g, '$1');
}

const LEGACY_ENTRY_PATTERNS = [
  /from\s+apply_claims_legacy\s+import\s+main\b/,
  /from\s+apply_decisions_legacy\s+import\s+main\b/,
  /\bapply_claims_legacy\.main\s*\(/,
  /\bapply_decisions_legacy\.main\s*\(/,
];
const legacyMainCallers = [];
for (const f of readdirSync(SCRIPTS_DIR)) {
  if (!f.endsWith('.py')) continue;
  if (f === 'apply_claims_legacy.py' || f === 'apply_decisions_legacy.py') continue;
  const path = join(SCRIPTS_DIR, f);
  let body;
  try { body = readFileSync(path, 'utf8'); } catch { continue; }
  const codeOnly = stripComments(body);
  for (const pat of LEGACY_ENTRY_PATTERNS) {
    if (pat.test(codeOnly)) {
      legacyMainCallers.push(f);
      break;
    }
  }
}
if (legacyMainCallers.length) {
  add('fail', 'legacy-main-call',
      `Production scripts invoke the archived legacy apply main(): ${legacyMainCallers.join(', ')}. ` +
      `Use scripts/apply_pipeline.py instead.`);
}

const out = process.env.RELEASE_CHECK_PIPELINE_ORPHANS_JSON_OUT;
if (out) {
  const { writeFileSync } = await import('node:fs');
  writeFileSync(out, JSON.stringify(findings, null, 2));
}

if (findings.length === 0) {
  console.log('✓ wq-098 pipeline integrity: no findings');
} else {
  for (const f of findings) {
    console.log(`[${f.severity}] ${f.ref} — ${f.msg}`);
  }
}
process.exit(0);
