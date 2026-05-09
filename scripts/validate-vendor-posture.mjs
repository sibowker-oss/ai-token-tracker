// validate-vendor-posture.mjs — wq-101 §2/§3 Validators.
//
// Asserts:
//   1. site-data.json has dashboard.vendorPostureMethodology with 5 axes.
//   2. exactly 12 dashboard.enterpriseReality entries carry postureScores.
//   3. each cohort entry has all required posture fields:
//      product, parent, archetype, arrShare{value,denominator,denominatorType},
//      postureScores{disclosure,bundling,pricing,cost,acceleration,
//                    _prototype,_lastVerified}, watchSignals.
//   4. private companies (ticker == "private") carry gmUnavailable: true and
//      cost: 0; non-private must have cost in [1..5] with no gmUnavailable.
//   5. each scored axis (disclosure/bundling/pricing/acceleration) is in
//      [1..5]; cost in [0..5]; integer-valued.
//   6. usage.html still embeds the section heading "SaaS AI Transition Map"
//      and contains the renderPostureRadar()/renderPostureSection() symbols
//      used by the page (catches accidental rename).
//
// Output schema (matches sibling validators):
//   [ { name: 'vendor-posture-methodology', severity: 'fail' | 'pass',
//       detail: '...' }, ... ]

import { readFileSync, existsSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(__dirname);

const findings = [];
function add(name, severity, detail) {
  findings.push({ name, severity, detail });
}

const REQUIRED_AXES = ['disclosure', 'bundling', 'pricing', 'cost', 'acceleration'];

const sitePath = join(ROOT, 'site-data.json');
if (!existsSync(sitePath)) {
  add('site-data-present', 'fail', 'site-data.json not found');
} else {
  let data;
  try {
    data = JSON.parse(readFileSync(sitePath, 'utf8'));
  } catch (e) {
    add('site-data-parse', 'fail', `site-data.json parse error: ${e.message}`);
  }

  if (data) {
    const dash = data.dashboard || {};
    const m = dash.vendorPostureMethodology;
    if (!m) {
      add('vendor-posture-methodology', 'fail',
        'dashboard.vendorPostureMethodology block missing');
    } else {
      const axesOk = Array.isArray(m.axes)
        && m.axes.length === 5
        && REQUIRED_AXES.every(a => m.axes.includes(a));
      if (!axesOk) {
        add('vendor-posture-methodology', 'fail',
          `vendorPostureMethodology.axes must be exactly ${JSON.stringify(REQUIRED_AXES)}, got ${JSON.stringify(m.axes)}`);
      } else {
        add('vendor-posture-methodology', 'pass',
          `vendorPostureMethodology v${m.version || '?'} present with 5 axes`);
      }
    }

    const er = Array.isArray(dash.enterpriseReality) ? dash.enterpriseReality : [];
    const cohort = er.filter(c => c && c.postureScores);
    if (cohort.length !== 12) {
      add('vendor-posture-cohort-size', 'fail',
        `expected exactly 12 enterpriseReality entries with postureScores; found ${cohort.length}`);
    } else {
      add('vendor-posture-cohort-size', 'pass',
        `12 cohort entries with postureScores`);
    }

    cohort.forEach(c => {
      const id = c.id || '(no-id)';
      const requiredTop = ['product', 'parent', 'archetype', 'arrShare', 'watchSignals'];
      const missingTop = requiredTop.filter(f => !c[f]);
      if (missingTop.length) {
        add('vendor-posture-fields', 'fail',
          `${id}: missing top-level fields ${JSON.stringify(missingTop)}`);
      }
      const share = c.arrShare || {};
      const shareMissing = ['value', 'denominator', 'denominatorType'].filter(f => !share[f]);
      if (shareMissing.length) {
        add('vendor-posture-share', 'fail',
          `${id}: arrShare missing ${JSON.stringify(shareMissing)}`);
      }
      if (share.denominatorType && !['business_unit', 'parent_total'].includes(share.denominatorType)) {
        add('vendor-posture-share', 'fail',
          `${id}: arrShare.denominatorType must be business_unit | parent_total, got ${share.denominatorType}`);
      }

      const ps = c.postureScores || {};
      const isPrivate = (c.ticker || '').toLowerCase() === 'private';
      REQUIRED_AXES.forEach(axis => {
        const v = ps[axis];
        if (typeof v !== 'number' || !Number.isInteger(v)) {
          add('vendor-posture-scores', 'fail',
            `${id}: postureScores.${axis} must be integer, got ${JSON.stringify(v)}`);
          return;
        }
        if (axis === 'cost') {
          if (v < 0 || v > 5) {
            add('vendor-posture-scores', 'fail',
              `${id}: postureScores.cost must be 0..5, got ${v}`);
          }
        } else if (v < 1 || v > 5) {
          add('vendor-posture-scores', 'fail',
            `${id}: postureScores.${axis} must be 1..5, got ${v}`);
        }
      });
      if (typeof ps._prototype !== 'boolean') {
        add('vendor-posture-scores', 'fail',
          `${id}: postureScores._prototype must be boolean`);
      }
      if (typeof ps._lastVerified !== 'string' || !/^\d{4}-Q[1-4]$/.test(ps._lastVerified)) {
        add('vendor-posture-scores', 'fail',
          `${id}: postureScores._lastVerified must be like '2026-Q1', got ${JSON.stringify(ps._lastVerified)}`);
      }

      // Private vs public: gmUnavailable + cost==0 enforcement.
      if (isPrivate) {
        if (c.gmUnavailable !== true) {
          add('vendor-posture-private-gm', 'fail',
            `${id} (private): expected gmUnavailable: true`);
        }
        if (ps.cost !== 0) {
          add('vendor-posture-private-gm', 'fail',
            `${id} (private): cost must be 0 (NA), got ${ps.cost}`);
        }
      } else {
        if (c.gmUnavailable) {
          add('vendor-posture-private-gm', 'fail',
            `${id} (public): gmUnavailable should be absent for non-private cohort entries`);
        }
        if (ps.cost === 0) {
          add('vendor-posture-private-gm', 'fail',
            `${id} (public): cost == 0 reserved for gmUnavailable private cohort entries`);
        }
      }

      // D4 path-b: Bundling and Cost editorial scores must carry a citation
      // until _prototype clears (post staging review).
      if (ps._prototype === true) {
        const cit = ps._citations || {};
        if (!cit.bundling || !cit.cost) {
          add('vendor-posture-citations', 'fail',
            `${id}: prototype scores require both bundling + cost citations (_citations.{bundling,cost})`);
        }
      }
    });
  }
}

// 6. usage.html sanity — section heading + JS symbol both present.
const usagePath = join(ROOT, 'usage.html');
if (!existsSync(usagePath)) {
  add('usage-html-present', 'fail', 'usage.html not found');
} else {
  const src = readFileSync(usagePath, 'utf8');
  if (!src.includes('SaaS AI Transition Map')) {
    add('vendor-posture-section-heading', 'fail',
      'usage.html is missing the "SaaS AI Transition Map" section heading');
  } else {
    add('vendor-posture-section-heading', 'pass',
      'usage.html carries the "SaaS AI Transition Map" heading');
  }
  const symbols = ['renderPostureRadar', 'renderPostureSection', 'POSTURE_AXIS_ORDER'];
  const missing = symbols.filter(s => !src.includes(s));
  if (missing.length) {
    add('vendor-posture-symbols', 'fail',
      `usage.html missing renderer symbols: ${JSON.stringify(missing)}`);
  } else {
    add('vendor-posture-symbols', 'pass',
      'usage.html carries renderPostureRadar/renderPostureSection symbols');
  }
}

const failCount = findings.filter(f => f.severity === 'fail').length;
const passCount = findings.filter(f => f.severity === 'pass').length;

const out = process.env.RELEASE_CHECK_VENDOR_POSTURE_JSON_OUT;
if (out) writeFileSync(out, JSON.stringify(findings, null, 2));

if (failCount === 0) {
  console.log(`vendor-posture: ${passCount} pass, 0 fail`);
  process.exit(0);
}
for (const f of findings.filter(f => f.severity === 'fail')) {
  console.log(`  FAIL  ${f.name}  ${f.detail}`);
}
console.log(`vendor-posture: ${passCount} pass, ${failCount} fail`);
process.exit(failCount === 0 ? 0 : 1);
