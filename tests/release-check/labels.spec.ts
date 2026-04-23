// tests/release-check/labels.spec.ts
// Enforces GUIDELINES.md §5.6 — no raw JSON keys or internal slugs on screen.

import { test, expect } from '@playwright/test';
import { loadSiteData, pages, findRawKeys } from './helpers';

const data = loadSiteData();
const pageList = pages(data);

// Collect candidate raw keys from site-data.json (top-level keys, controlled vocab keys, known identifier patterns)
const suspectKeys = collectSuspectKeys(data);

function collectSuspectKeys(root: any): string[] {
  const out = new Set<string>();
  function walk(node: any) {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) { node.forEach(walk); return; }
    for (const [k, v] of Object.entries(node)) {
      // Keys in snake_case, kebab-case, or lowercase slugs are suspect if they would ever be rendered.
      if (/^[a-z][a-z0-9_-]{2,}$/.test(k)) out.add(k);
      walk(v);
    }
  }
  walk(root);
  // Filter out structural keys that we expect not to appear on screen anyway
  const structural = new Set(['meta', 'pages', 'data', 'value', 'label', 'unit', 'year', 'source', 'sourceUrl', 'retrievedAt', 'nextReview', 'confidence', 'note', 'sources', 'revenueType', 'hasDerivedNumbers', 'title', 'path', 'dataReferences', 'labels', 'minMonths', 'maxMonths', 'medianMonths']);
  return [...out].filter(k => !structural.has(k));
}

test.skip(({ browserName }, testInfo) => !testInfo.project.name.startsWith('desktop'), 'label audit runs on desktop only');

for (const p of pageList) {
  test(`no raw keys visible on ${p.key} (§5.6)`, async ({ page }) => {
    await page.goto(p.path, { waitUntil: 'networkidle' });
    const visible = await findRawKeys(page, suspectKeys);
    expect(visible, `raw keys leaked to UI on ${p.path}:\n${visible.join(', ')}`).toHaveLength(0);
  });
}
