// tests/release-check/reconciliation.spec.ts
// Enforces GUIDELINES.md §5.3.1 — cross-page reconciliation.
// For every canonical field listed in meta.dataReferences, verify that the displayed value
// on each consuming page matches the canonical value from site-data.json.

import { test, expect } from '@playwright/test';
import { loadSiteData } from './helpers';

const data = loadSiteData();
const refs = data.meta?.dataReferences ?? {};

test.skip(({}, testInfo) => testInfo.project.name !== 'desktop-chrome', 'reconciliation runs once, on desktop-chrome');
test.skip(Object.keys(refs).length === 0, 'no dataReferences map — skipping. Add one per §5.3.1 once cross-page consumption exists.');

for (const [canonicalKey, consumers] of Object.entries(refs)) {
  const canonical = resolveByDottedKey(data, canonicalKey);
  if (canonical === undefined) continue;

  for (const consumerPath of consumers as string[]) {
    test(`${canonicalKey} matches on ${consumerPath}`, async ({ page }) => {
      await page.goto(consumerPath, { waitUntil: 'networkidle' });
      const selector = `[data-canonical-ref="${canonicalKey}"]`;
      const loc = page.locator(selector);
      await expect(loc, `consumer ${consumerPath} does not expose [data-canonical-ref="${canonicalKey}"]`).toHaveCount(1);
      const displayed = await loc.getAttribute('data-canonical-value');
      const expected = String((canonical as any).value ?? canonical);
      expect(displayed, `drift on ${canonicalKey} — canonical ${expected} vs displayed ${displayed}`).toBe(expected);
    });
  }
}

function resolveByDottedKey(root: any, key: string): any {
  return key.split('.').reduce((n, p) => (n == null ? undefined : n[p]), root);
}
