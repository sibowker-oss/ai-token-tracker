#!/usr/bin/env node
// scripts/validate-capital-sankey.mjs
// wq-074 §3 #6 — per-node conservation for capital sankey.
//
// Asserts (within 0.5%):
//   1. sum(sources)      == total
//   2. sum(destinations) == total
//   3. sum(utilization)  == total
//   4. Per source node: sum of stage-1 outflows from that source == sources[name]
//   5. Per destination node: sum of stage-1 inflows == destinations[name]
//      AND sum of stage-2 outflows == destinations[name]
//   6. Per utilization node: sum of stage-2 inflows == utilization[name]
//
// Skipped when site-data.json:capital_sankey absent (engine not run yet).

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const sitePath = join(root, 'site-data.json');
const TOLERANCE_COL = 0.005;
const TOLERANCE_NODE = 0.02;  // looser per-node — flow values are rounded to cents
const findings = [];

function pctDelta(a, b) {
  const denom = Math.max(Math.abs(a), Math.abs(b));
  return denom === 0 ? 0 : Math.abs(a - b) / denom;
}

if (!existsSync(sitePath)) {
  findings.push({ severity: 'fail', ref: 'site-data.json', msg: 'site-data.json not found' });
} else {
  const site = JSON.parse(readFileSync(sitePath, 'utf8'));
  const cs = site.capital_sankey;
  if (!cs) {
    // Engine hasn't run; that's allowed (advisory only). Skip silently.
    console.log('· capital-sankey: site-data.json:capital_sankey absent (engine not run); skipping');
    process.exit(0);
  }

  const total = cs.total ?? 0;
  const sources = cs.sources || {};
  const destinations = cs.destinations || {};
  const utilization = cs.utilization || {};
  const flows = cs.flows || [];

  // Rule 1-3: column sums == total
  const sumSources = Object.values(sources).reduce((s, v) => s + v, 0);
  const sumDest = Object.values(destinations).reduce((s, v) => s + v, 0);
  const sumUtil = Object.values(utilization).reduce((s, v) => s + v, 0);
  for (const [name, sum] of [['sources', sumSources], ['destinations', sumDest], ['utilization', sumUtil]]) {
    if (pctDelta(sum, total) > TOLERANCE_COL) {
      findings.push({
        severity: 'fail',
        ref: `capital_sankey.${name}_total`,
        msg: `sum(${name})=${sum.toFixed(4)} vs total=${total.toFixed(4)} — Δ ${(pctDelta(sum, total) * 100).toFixed(2)}% > ${TOLERANCE_COL * 100}%`,
      });
    }
  }

  // Rule 4: per-source outflow sum == sources[src]
  const srcOutflow = {};
  for (const f of flows) {
    const [src, _dst, v] = f;
    if (src in sources) srcOutflow[src] = (srcOutflow[src] || 0) + v;
  }
  for (const [src, expected] of Object.entries(sources)) {
    const actual = srcOutflow[src] || 0;
    if (expected && pctDelta(actual, expected) > TOLERANCE_NODE) {
      findings.push({
        severity: 'fail',
        ref: `capital_sankey.source[${src}]`,
        msg: `outflow_sum=${actual.toFixed(4)} vs expected=${expected.toFixed(4)} — Δ ${(pctDelta(actual, expected) * 100).toFixed(2)}% > ${TOLERANCE_NODE * 100}%`,
      });
    }
  }

  // Rule 5: per-destination inflow sum (from sources) == destinations[dst]
  // AND outflow sum (to utilization) == destinations[dst]
  const destInflow = {};
  const destOutflow = {};
  for (const f of flows) {
    const [src, dst, v] = f;
    if (dst in destinations && src in sources) destInflow[dst] = (destInflow[dst] || 0) + v;
    if (src in destinations && dst in utilization) destOutflow[src] = (destOutflow[src] || 0) + v;
  }
  for (const [dst, expected] of Object.entries(destinations)) {
    const inflow = destInflow[dst] || 0;
    if (expected && pctDelta(inflow, expected) > TOLERANCE_NODE) {
      findings.push({
        severity: 'fail',
        ref: `capital_sankey.destination[${dst}].inflow`,
        msg: `inflow_sum=${inflow.toFixed(4)} vs expected=${expected.toFixed(4)} — Δ ${(pctDelta(inflow, expected) * 100).toFixed(2)}%`,
      });
    }
    const outflow = destOutflow[dst] || 0;
    if (expected && pctDelta(outflow, expected) > TOLERANCE_NODE) {
      findings.push({
        severity: 'fail',
        ref: `capital_sankey.destination[${dst}].outflow`,
        msg: `outflow_sum=${outflow.toFixed(4)} vs expected=${expected.toFixed(4)} — Δ ${(pctDelta(outflow, expected) * 100).toFixed(2)}%`,
      });
    }
  }

  // Rule 6: per-utilization inflow sum == utilization[util]
  const utilInflow = {};
  for (const f of flows) {
    const [src, dst, v] = f;
    if (dst in utilization && src in destinations) utilInflow[dst] = (utilInflow[dst] || 0) + v;
  }
  for (const [util, expected] of Object.entries(utilization)) {
    const inflow = utilInflow[util] || 0;
    if (expected && pctDelta(inflow, expected) > TOLERANCE_NODE) {
      findings.push({
        severity: 'fail',
        ref: `capital_sankey.utilization[${util}]`,
        msg: `inflow_sum=${inflow.toFixed(4)} vs expected=${expected.toFixed(4)} — Δ ${(pctDelta(inflow, expected) * 100).toFixed(2)}%`,
      });
    }
  }
}

const jsonOut = process.env.RELEASE_CHECK_CAPITAL_SANKEY_JSON_OUT;
if (jsonOut) {
  try { writeFileSync(jsonOut, JSON.stringify(findings, null, 2)); } catch {}
}

if (findings.length === 0) {
  console.log('✓ capital-sankey: per-column + per-node conservation hold within tolerance.');
  process.exit(0);
}
console.log(`capital-sankey: ${findings.length} fail`);
for (const f of findings) {
  console.log(`  [${f.severity.padEnd(4)}] ${f.ref} — ${f.msg}`);
}
process.exit(1);
