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
console.log('\n→ 1/4  Provenance validator (§4.2, §4.4, §4.5, §5.5, §5.6, §11.2)');
const provJson = join(reportDir, 'provenance.json');
const provStatus = run('node', ['scripts/validate-provenance.mjs'], { RELEASE_CHECK_JSON_OUT: provJson });

// Step 2 (wq-048): consensus provenance — every entity-year collected_revenue
// must trace to consensus_engine_derived | editorial_override | accepted |
// editorial_reconciliation. Catches silent untraceable values from a
// future engine bug or a partial backfill.
console.log('\n→ 2/5  Consensus provenance (wq-048 §2 #10)');
const consensusJson = join(reportDir, 'consensus-provenance.json');
const consensusStatus = run('node', ['scripts/validate-consensus-provenance.mjs'], {
  RELEASE_CHECK_CONSENSUS_JSON_OUT: consensusJson,
});

// Step 3 (wq-055 §3.2): Sankey conservation — sums balance across all
// 4 columns of the rendered Sankey (buyers / channels / providers /
// outcomes) within 0.5%. Per-provider self-consistency: implied
// customer_revenue (= value - vc_subsidy) >= 0.
console.log('\n→ 3/5  Sankey conservation (wq-055 §3.2)');
const sankeyConservationJson = join(reportDir, 'sankey-conservation.json');
const sankeyConservationStatus = run('node', ['scripts/validate-sankey-conservation.mjs'], {
  RELEASE_CHECK_SANKEY_CONSERVATION_JSON_OUT: sankeyConservationJson,
});

// Step 4 (wq-063 §3 #6): cross-page consistency — site-data.json:cumulative
// and site-data.json:sankey must agree on the latest year's gross figure;
// index.html SCENARIOS must be data-driven (no hardcoded $X literals).
console.log('\n→ 4/7  Cross-page consistency (wq-063 §3 #6)');
const crossPageJson = join(reportDir, 'cross-page-consistency.json');
const crossPageStatus = run('node', ['scripts/validate-cross-page-consistency.mjs'], {
  RELEASE_CHECK_CROSS_PAGE_JSON_OUT: crossPageJson,
});

// Step 5 (wq-067 §3 #5): market-aggregates internal consistency — sum(per_source_capex)
// == total_capex; sum(per_channel) == total_customer_revenue_gross; tokens identity.
console.log('\n→ 5/8  Market-aggregates internal consistency (wq-067 §3 #5)');
const marketAggJson = join(reportDir, 'market-aggregates.json');
const marketAggStatus = run('node', ['scripts/validate-market-aggregates.mjs'], {
  RELEASE_CHECK_MARKET_AGGREGATES_JSON_OUT: marketAggJson,
});

// Step 6 (wq-073 §3 #5): no-hardcoded-constants — assert capital/revenue/ask/in-development
// HTML pages stay wired to data files (catches future regressions where someone
// re-hardcodes a ratio literal or scenario object).
console.log('\n→ 6/9  No-hardcoded-constants (wq-073 §3 #5)');
const noHardcodedJson = join(reportDir, 'no-hardcoded-constants.json');
const noHardcodedStatus = run('node', ['scripts/validate-no-hardcoded-constants.mjs'], {
  RELEASE_CHECK_NO_HARDCODED_JSON_OUT: noHardcodedJson,
});

// Step 7 (wq-074 §3 #6): capital-sankey per-node conservation — sum(sources)
// == sum(destinations) == sum(utilization) == total; per-source outflow ==
// source value; per-destination inflow == outflow == destination value;
// per-utilization inflow == utilization value. Same lesson as wq-044/062 —
// rendered output must reconcile to engine input at every node boundary.
console.log('\n→ 7/10  Capital-sankey conservation (wq-074 §3 #6)');
const capitalSankeyJson = join(reportDir, 'capital-sankey.json');
const capitalSankeyStatus = run('node', ['scripts/validate-capital-sankey.mjs'], {
  RELEASE_CHECK_CAPITAL_SANKEY_JSON_OUT: capitalSankeyJson,
});

// Step 8 (wq-076 §3 #6): currency-format — assert no excess-decimal dollar
// literals (e.g. $176.48B) in wq-076-wired pages, and that format-helpers.js
// is loaded so formatCurrency() is defined.
console.log('\n→ 8/11  Currency-format (wq-076 §3 #6)');
const currencyFormatJson = join(reportDir, 'currency-format.json');
const currencyFormatStatus = run('node', ['scripts/validate-currency-format.mjs'], {
  RELEASE_CHECK_CURRENCY_FORMAT_JSON_OUT: currencyFormatJson,
});

// Step 9 (wq-077 §3 #6): narrative-hydration — assert known narrative dollar
// references on capital + revenue are wrapped in [data-narrative] spans and
// hydrated by hydrateNarrative() at render time.
console.log('\n→ 9/11  Narrative-hydration (wq-077 §3 #6)');
const narrativeJson = join(reportDir, 'narrative-hydration.json');
const narrativeStatus = run('node', ['scripts/validate-narrative-hydration.mjs'], {
  RELEASE_CHECK_NARRATIVE_JSON_OUT: narrativeJson,
});

// Step 10 (wq-054 §3 #6): period-attribution — assert no provenance entry on
// an annual field has claim text containing a sub-period qualifier (H1/Q3/
// exit-snapshot/monthly-peak) without explanation. Catches regression where
// an extractor or manual edit silently writes a sub-period claim into an
// annual field path.
console.log('\n→ 10/12  Period-attribution (wq-054 §3 #6)');
const periodAttrJson = join(reportDir, 'period-attribution.json');
const periodAttrStatus = run('node', ['scripts/validate-period-attribution.mjs'], {
  RELEASE_CHECK_PERIOD_ATTRIBUTION_JSON_OUT: periodAttrJson,
});

// Step 11: Playwright suite
console.log('\n→ 11/12  Playwright suite (smoke, structure, labels, mobile, freshness, links, reconciliation, visual)');
const pwStatus = run('npx', ['playwright', 'test', '--output', join(reportDir, 'playwright-artefacts')]);

// Step 12: editorial (human / subagent — no-op from CLI)
console.log('\n→ 12/12  Editorial read-through (§11.5)');
console.log('  CLI cannot perform editorial review. Run `/release-check` in Claude Code for §11.5.');

// Build report.md
const provFindings = existsSync(provJson) ? JSON.parse(readFileSync(provJson, 'utf8')) : [];
const provFails = provFindings.filter(f => f.severity === 'fail');
const provAdvisories = provFindings.filter(f => f.severity === 'advisory');

const consensusFindings = existsSync(consensusJson) ? JSON.parse(readFileSync(consensusJson, 'utf8')) : [];
const consensusFails = consensusFindings.filter(f => f.severity === 'fail');

const sankeyConsFindings = existsSync(sankeyConservationJson) ? JSON.parse(readFileSync(sankeyConservationJson, 'utf8')) : [];
const sankeyConsFails = sankeyConsFindings.filter(f => f.severity === 'fail');

const crossPageFindings = existsSync(crossPageJson) ? JSON.parse(readFileSync(crossPageJson, 'utf8')) : [];
const crossPageFails = crossPageFindings.filter(f => f.severity === 'fail');

const marketAggFindings = existsSync(marketAggJson) ? JSON.parse(readFileSync(marketAggJson, 'utf8')) : [];
const marketAggFails = marketAggFindings.filter(f => f.severity === 'fail');

const noHardcodedFindings = existsSync(noHardcodedJson) ? JSON.parse(readFileSync(noHardcodedJson, 'utf8')) : [];
const noHardcodedFails = noHardcodedFindings.filter(f => f.severity === 'fail');

const capitalSankeyFindings = existsSync(capitalSankeyJson) ? JSON.parse(readFileSync(capitalSankeyJson, 'utf8')) : [];
const capitalSankeyFails = capitalSankeyFindings.filter(f => f.severity === 'fail');

const currencyFormatFindings = existsSync(currencyFormatJson) ? JSON.parse(readFileSync(currencyFormatJson, 'utf8')) : [];
const currencyFormatFails = currencyFormatFindings.filter(f => f.severity === 'fail');

const narrativeFindings = existsSync(narrativeJson) ? JSON.parse(readFileSync(narrativeJson, 'utf8')) : [];
const narrativeFails = narrativeFindings.filter(f => f.severity === 'fail');

const periodAttrFindings = existsSync(periodAttrJson) ? JSON.parse(readFileSync(periodAttrJson, 'utf8')) : [];
const periodAttrFails = periodAttrFindings.filter(f => f.severity === 'fail');
const periodAttrAdvisories = periodAttrFindings.filter(f => f.severity === 'advisory');

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
| Consensus provenance (wq-048) | ${consensusFindings.length === 0 ? '✓' : ''} | 0 | ${consensusFails.length} |
| Sankey conservation (wq-055) | ${sankeyConsFindings.length === 0 ? '✓' : ''} | 0 | ${sankeyConsFails.length} |
| Cross-page consistency (wq-063) | ${crossPageFindings.length === 0 ? '✓' : ''} | 0 | ${crossPageFails.length} |
| Market-aggregates consistency (wq-067) | ${marketAggFindings.length === 0 ? '✓' : ''} | 0 | ${marketAggFails.length} |
| No-hardcoded-constants (wq-073) | ${noHardcodedFindings.length === 0 ? '✓' : ''} | 0 | ${noHardcodedFails.length} |
| Capital-sankey conservation (wq-074) | ${capitalSankeyFindings.length === 0 ? '✓' : ''} | 0 | ${capitalSankeyFails.length} |
| Currency-format (wq-076) | ${currencyFormatFindings.length === 0 ? '✓' : ''} | 0 | ${currencyFormatFails.length} |
| Narrative-hydration (wq-077) | ${narrativeFindings.length === 0 ? '✓' : ''} | 0 | ${narrativeFails.length} |
| Period-attribution (wq-054) | ${periodAttrFindings.length === 0 ? '✓' : ''} | ${periodAttrAdvisories.length} | ${periodAttrFails.length} |
| Playwright suite | ${pwSummary.tests - pwSummary.failures} | — | ${pwSummary.failures} |
| Editorial (§11.5) | — | via \`/release-check\` | — |

## Verdict

${verdict(provFails.length + consensusFails.length + sankeyConsFails.length + crossPageFails.length + marketAggFails.length + noHardcodedFails.length + capitalSankeyFails.length + currencyFormatFails.length + narrativeFails.length + periodAttrFails.length + pwSummary.failures, provAdvisories.length + periodAttrAdvisories.length)}

## Provenance findings

${renderFindings(provFindings)}

## Consensus-provenance findings (wq-048 §2 #10)

${renderFindings(consensusFindings)}

## Sankey-conservation findings (wq-055 §3.2)

${renderFindings(sankeyConsFindings)}

## Cross-page consistency findings (wq-063 §3 #6)

${renderFindings(crossPageFindings)}

## Market-aggregates consistency findings (wq-067 §3 #5)

${renderFindings(marketAggFindings)}

## No-hardcoded-constants findings (wq-073 §3 #5)

${renderFindings(noHardcodedFindings)}

## Capital-sankey conservation findings (wq-074 §3 #6)

${renderFindings(capitalSankeyFindings)}

## Currency-format findings (wq-076 §3 #6)

${renderFindings(currencyFormatFindings)}

## Narrative-hydration findings (wq-077 §3 #6)

${renderFindings(narrativeFindings)}

## Period-attribution findings (wq-054 §3 #6)

${renderFindings(periodAttrFindings)}

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
  consensus_provenance: consensusFindings,
  sankey_conservation: sankeyConsFindings,
  cross_page_consistency: crossPageFindings,
  market_aggregates: marketAggFindings,
  no_hardcoded_constants: noHardcodedFindings,
  capital_sankey: capitalSankeyFindings,
  currency_format: currencyFormatFindings,
  narrative_hydration: narrativeFindings,
  period_attribution: periodAttrFindings,
  playwright: pwSummary,
}, null, 2));

console.log(`\n=== Report written to ${join(reportDir, 'report.md')} ===`);
console.log(verdictLine(provFails.length + pwSummary.failures, provAdvisories.length));

if (MODE === 'strict') {
  process.exit(provFails.length + consensusFails.length + sankeyConsFails.length + crossPageFails.length + marketAggFails.length + noHardcodedFails.length + capitalSankeyFails.length + currencyFormatFails.length + narrativeFails.length + pwSummary.failures > 0 ? 1 : 0);
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
