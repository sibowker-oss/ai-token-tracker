#!/usr/bin/env node
/**
 * wq-102 Stage 2 — Release-gate validator.
 *
 * Walks the six priority pages and rejects any visible numeric literal
 * that is NOT either:
 *   1. Inside an element with a `data-num="<id>"` attribute, OR
 *   2. Inside the `<meta property="og:description">` content attr
 *      (handled by render_numbers.py via per-token map), OR
 *   3. Inside a JS data array currently wired in JS_ARRAY_WIRING (LAG_RAW)
 *      — covered by the manifest at `js:NAME[idx].col`, OR
 *   4. On the explicit allowlist for non-data numerics (years, ABN/ACN,
 *      copyright, ratio markers in JS, SVG/style attrs).
 *
 * Advisory by default (writes report). With CHECK_MODE=strict, exits non-zero
 * on any violation.
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';

const ROOT = process.cwd();
const BETA = join(ROOT, 'beta');
const PRIORITY = [
  'index.html',
  'capital.html',
  'revenue.html',
  'compute.html',
  'usage.html',
  'power.html',
];

const NUMERIC_PATTERNS = [
  // dollar with magnitude:  $745B, $43.07B, $1.2T, ~$5B
  /~?\$\s*\d+(?:\.\d+)?\s*[BMTKbmtk]\b/g,
  // bare magnitude (no $): 360T, 1.9T/day, 95 GW
  /~?\d+(?:\.\d+)?\s*[BMTK](?:\/day|\/d|\/s|\b)/g,
  // plain dollar: $34, $0.50
  /\$\s*\d+(?:\.\d+)?\b(?![BMTKbmtk])/g,
  // percentages
  /[+\-]?\d+(?:\.\d+)?\s*%/g,
  // ratio multiplier
  /\d+(?:\.\d+)?\s*[×x]\b/g,
  // power units
  /\d+(?:\.\d+)?\s*(?:GW|MW|kW|TWh|GWh)\b/g,
];

// Block-strip patterns: chunks of HTML where numeric literals are not
// "visible numbers" (style/SVG/script/comments).
function stripIgnoredBlocks(html) {
  let out = html;
  // Strip <style>...</style>
  out = out.replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '');
  // Strip <svg>...</svg>
  out = out.replace(/<svg\b[^>]*>[\s\S]*?<\/svg>/gi, '');
  // Strip <script>...</script>  (LAG_RAW etc. are catalogued at the
  // manifest level via `js:NAME[idx].col`; this validator covers visible
  // DOM text only)
  out = out.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '');
  // HTML comments
  out = out.replace(/<!--[\s\S]*?-->/g, '');
  // Strip a handful of attribute payloads where layout numbers leak
  out = out.replace(/\bstyle\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bclass\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bid\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bdata-(?:bar-w|w|line|ratio|narrative|ledger|num)\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bhref\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bsrc\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\baria-label\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\baria-describedby\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\btitle\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bwidth\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bheight\s*=\s*"[^"]*"/g, '');
  out = out.replace(/\bviewBox\s*=\s*"[^"]*"/g, '');
  // Strip og:description content attr (handled by render_numbers.py)
  out = out.replace(/<meta\s+property\s*=\s*["']og:description["']\s+content\s*=\s*"[^"]*"\s*\/?>/gi, '');
  return out;
}

// True if `pos` (0-indexed offset in `html`) is inside any element that
// carries a `data-num="..."` attribute. We walk forward looking for the
// nearest opening tag and check.
function isInsideAnchoredElement(html, pos) {
  // Find the nearest `<` to the left of pos, then check whether the
  // enclosing element open tag carries data-num.
  // Quick heuristic: scan backwards for the most recent `<tag ...>` that
  // hasn't been closed yet.
  const before = html.slice(0, pos);
  // Find opens and closes; track depth-1 stack. For perf, only match within
  // 4 KB before pos.
  const window = before.slice(Math.max(0, before.length - 4000));
  const re = /<(\/?)([a-zA-Z][\w-]*)\b([^>]*)>/g;
  const stack = [];
  let m;
  while ((m = re.exec(window))) {
    const closing = m[1] === '/';
    const tag = m[2].toLowerCase();
    const attrs = m[3];
    if (closing) {
      // pop the most recent matching open
      for (let i = stack.length - 1; i >= 0; i--) {
        if (stack[i].tag === tag) {
          stack.splice(i, 1);
          break;
        }
      }
    } else if (!attrs.endsWith('/') && tag !== 'meta' && tag !== 'br' && tag !== 'img' && tag !== 'input' && tag !== 'link') {
      stack.push({ tag, attrs });
    }
  }
  return stack.some(({ attrs }) => /\bdata-num\s*=/.test(attrs));
}

// Tokens we always allow even outside an anchor.
function isAllowedNonData(tok, surroundingLine) {
  // 4-digit years
  if (/^(?:19|20)\d{2}$/.test(tok)) return true;
  // Confidence-tier letter labels: "1B", "2B", "3B" in tier cells.
  // The provenance tier system uses 1A/1B/2A/2B/3A/3B/3C as classification
  // codes — they LOOK like "$1B" / "$2B" / etc. but are letter labels, not
  // billions. Allowed when:
  //   - The token is exactly 1B/2B/3B (single digit + B), AND
  //   - The surrounding line contains either "tier" or the slash-paired
  //     form "<digit><letter>/<digit>B" (e.g. "1A/1B", "3A/3B/3C").
  if (/^[123]B$/.test(tok)) {
    if (
      /\btier\b/i.test(surroundingLine)
      || /\d[ABC]\s*\/\s*\d[ABC]/.test(surroundingLine)
      || /<t[hd][^>]*>\s*[123]B\s*<\/t[hd]>/.test(surroundingLine)
    ) {
      return true;
    }
  }
  return false;
}

function check(file) {
  const html = readFileSync(join(BETA, file), 'utf8');
  const stripped = stripIgnoredBlocks(html);
  const violations = [];
  // Track positions on the stripped string. We need to map back to the
  // original for line numbers; cheaper is to scan the original directly
  // and rely on stripIgnoredBlocks to whitespace out blocks. Instead, do
  // it differently: re-run on original HTML BUT after replacing each
  // block-to-strip with whitespace OF THE SAME LENGTH so offsets stay valid.
  // Implementation below.
  let masked = html;
  const masks = [
    /<style\b[^>]*>[\s\S]*?<\/style>/gi,
    /<svg\b[^>]*>[\s\S]*?<\/svg>/gi,
    /<script\b[^>]*>[\s\S]*?<\/script>/gi,
    /<!--[\s\S]*?-->/g,
    /\bstyle\s*=\s*"[^"]*"/g,
    /\bclass\s*=\s*"[^"]*"/g,
    /\bid\s*=\s*"[^"]*"/g,
    /\bhref\s*=\s*"[^"]*"/g,
    /\bsrc\s*=\s*"[^"]*"/g,
    /\baria-label\s*=\s*"[^"]*"/g,
    /\baria-describedby\s*=\s*"[^"]*"/g,
    /\btitle\s*=\s*"[^"]*"/g,
    /\bwidth\s*=\s*"[^"]*"/g,
    /\bheight\s*=\s*"[^"]*"/g,
    /\bviewBox\s*=\s*"[^"]*"/g,
    /\bdata-(?:bar-w|w|line|ratio|narrative|ledger|num)\s*=\s*"[^"]*"/g,
    /<meta\s+property\s*=\s*["']og:description["']\s+content\s*=\s*"[^"]*"\s*\/?>/gi,
  ];
  for (const re of masks) {
    masked = masked.replace(re, (m) => ' '.repeat(m.length));
  }

  for (const re of NUMERIC_PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(masked)) !== null) {
      const tok = m[0];
      const pos = m.index;
      const line = html.slice(0, pos).split('\n').length;
      const lineText = html.split('\n')[line - 1].trim().slice(0, 200);
      if (isAllowedNonData(tok, lineText)) continue;
      if (isInsideAnchoredElement(html, pos)) continue;
      violations.push({ file, line, token: tok, line_text: lineText.slice(0, 160) });
    }
  }
  return violations;
}

const allViolations = [];
for (const file of PRIORITY) {
  try {
    const v = check(file);
    allViolations.push(...v);
    console.log(`  ${file.padStart(14)}: ${v.length} violations`);
  } catch (err) {
    console.error(`  ${file}: ERROR ${err.message}`);
  }
}

const reportDir = join(ROOT, 'tests', 'reports');
mkdirSync(reportDir, { recursive: true });
const reportPath = join(reportDir, 'wq-102-anchored.json');
writeFileSync(
  reportPath,
  JSON.stringify(
    {
      generated_at: new Date().toISOString(),
      total_violations: allViolations.length,
      violations: allViolations,
    },
    null,
    2,
  ),
);

if (allViolations.length === 0) {
  console.log('\n✓ All visible numeric literals on priority pages are anchored.');
  process.exit(0);
}

console.log(`\n✗ ${allViolations.length} unanchored numeric literal(s) on priority pages.`);
console.log(`  Report: ${reportPath}`);

// Print first 10 for visibility
for (const v of allViolations.slice(0, 10)) {
  console.log(`    ${v.file}:${v.line}  ${v.token}  — ${v.line_text}`);
}
if (allViolations.length > 10) {
  console.log(`    ... +${allViolations.length - 10} more (see report).`);
}

if (process.env.CHECK_MODE === 'strict') {
  process.exit(1);
}
process.exit(0);
