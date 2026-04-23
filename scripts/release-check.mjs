#!/usr/bin/env node
// scripts/release-check.mjs
// CLI entry point for the AI Ledger release-check suite.
// Advisory by default: always exits 0 after writing a report.
// Set CHECK_MODE=strict to bubble failures up as non-zero exit (used sparingly, e.g. in a future blocking CI gate).

import { spawnSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const MODE = process.env.CHECK_MODE ?? 'advisory';
const SOURCE = process.env.RELEASE_CHECK_SOURCE ?? 'local-cli';
const root = process.cwd();
const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const reportDir = join(root, 'tests', 'reports', stamp);
mkdirSync(reportDir, { recursive: true });

function run(cmd, args, env = {}) {
  const res = spawnSync(cmd, args, {
    stdio: 'inherit',
    env: { ...process.env, ...env },
  });
  return res.status ?? 1;
}

console.log(`\n=== AI Ledger release-check — ${stamp} (${MODE}) ===\n`);

// Step 1: provenance validator
console.log('\n→ 1/3  Provenance validator (§4.2, §4.4, §4.5, §5.5, §5.6, §11.2)');
const provJson = join(reportDir, 'provenance.json');
const provStatus = run('node', ['scripts/validate-provenance.mjs'], { RELEASE_CHECK_JSON_OUT: provJson });

// Step 2: Playwright suite
console.log('\n→ 2/3  Playwright suite (smoke, structure, labels, mobile, freshness, links, reconciliation, visual)');
const pwStatus = run('npx', ['playwright', 'test', '--output', join(reportDir, 'playwright-artefacts')]);

// Step 3: editorial (human / subagent — no-op from CLI)
console.log('\n→ 3/3  Editorial read-through (§11.5)');
console.log('  CLI cannot perform editorial review. Run `/release-check` in Claude Code for §11.5.');

// Build report.md
const provFindings = existsSync(provJson) ? JSON.parse(readFileSync(provJson, 'utf8')) : [];
const provFails = provFindings.filter(f => f.severity === 'fail');
const provAdvisories = provFindings.filter(f => f.severity === 'advisory');

const pwResultsPath = join(root, 'tests', 'reports', 'playwright-results.json');
let pwSummary = { tests: 0, failures: 0 };
if (existsSync(pwResultsPath)) {
  try {
    const pw = JSON.parse(readFileSync(pwResultsPath, 'utf8'));
    pwSummary.tests = pw.stats?.expected ?? 0;
    pwSummary.failures = (pw.stats?.unexpected ?? 0) + (pw.stats?.flaky ?? 0);
  } catch {}
}

const report = `# Release-check report

- **Run:** ${stamp}
- **Source:** ${SOURCE}
- **Mode:** ${MODE}
- **Commit:** ${gitShortSha()}

## Summary

| Stage | Pass | Advisory | Fail |
|---|---|---|---|
| Provenance (§4.2/§5.5) | ${provFindings.length === 0 ? '✓' : ''} | ${provAdvisories.length} | ${provFails.length} |
| Playwright suite | ${pwSummary.tests - pwSummary.failures} | — | ${pwSummary.failures} |
| Editorial (§11.5) | — | via \`/release-check\` | — |

## Verdict

${verdict(provFails.length + pwSummary.failures, provAdvisories.length)}

## Provenance findings

${renderFindings(provFindings)}

## Playwright suite

See \`${join('tests', 'reports', 'html', 'index.html')}\` for the full Playwright HTML report.
Artefacts (screenshots, traces): \`${join('tests', 'reports', stamp, 'playwright-artefacts')}\`

## Agent log

An entry for this run should be appended to \`data/agents.log.md\`. The Claude Code subagent does this automatically. CLI runs: copy the stub below.

\`\`\`markdown
## ${stamp} — release-check@1.0.0

- **Source:** ${SOURCE}
- **Commit:** ${gitShortSha()}
- **Report:** tests/reports/${stamp}/report.md
- **Scripted:** ${provFindings.length + pwSummary.tests - provAdvisories.length - provFails.length - pwSummary.failures} passed, ${provAdvisories.length} advisory, ${provFails.length + pwSummary.failures} fail
- **Editorial:** not run (CLI invocation)
- **Summary:** ${verdictLine(provFails.length + pwSummary.failures, provAdvisories.length)}
\`\`\`
`;

writeFileSync(join(reportDir, 'report.md'), report);
writeFileSync(join(reportDir, 'report.json'), JSON.stringify({
  stamp,
  source: SOURCE,
  mode: MODE,
  commit: gitShortSha(),
  provenance: provFindings,
  playwright: pwSummary,
}, null, 2));

console.log(`\n=== Report written to ${join(reportDir, 'report.md')} ===`);
console.log(verdictLine(provFails.length + pwSummary.failures, provAdvisories.length));

if (MODE === 'strict') {
  process.exit(provFails.length + pwSummary.failures > 0 ? 1 : 0);
}
// Advisory mode: always 0
process.exit(0);

function renderFindings(findings) {
  if (findings.length === 0) return '_No findings._';
  return findings
    .map(f => `- **[${f.severity}]** ${f.section} — \`${f.ref}\` — ${f.msg}`)
    .join('\n');
}

function verdict(fails, advisories) {
  if (fails === 0 && advisories === 0) return '**Ship-ready** — no findings.';
  if (fails === 0) return `**Advisory findings — operator call** — ${advisories} advisory, 0 fail.`;
  return `**Blocking issues (advisory-only run)** — ${fails} fail, ${advisories} advisory. Operator must address fails before promotion per §11.`;
}

function verdictLine(fails, advisories) {
  if (fails === 0 && advisories === 0) return 'Ship-ready.';
  if (fails === 0) return `${advisories} advisory finding${advisories === 1 ? '' : 's'}. Operator call.`;
  return `${fails} fail, ${advisories} advisory. Do not promote without addressing fails.`;
}

function gitShortSha() {
  const r = spawnSync('git', ['rev-parse', '--short', 'HEAD'], { encoding: 'utf8' });
  return (r.stdout ?? '').trim() || 'unknown';
}
