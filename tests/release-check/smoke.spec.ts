// tests/release-check/smoke.spec.ts
// Enforces GUIDELINES.md §11.4 smoke test.
// Runs on desktop-chrome / desktop-safari / desktop-firefox projects (all three browsers per §11.4).

import { test, expect } from '@playwright/test';
import { loadSiteData, pages } from './helpers';

const data = loadSiteData();
const pageList = pages(data);

for (const p of pageList) {
  test.describe(`smoke — ${p.key}`, () => {
    test(`${p.key} loads without console errors`, async ({ page }) => {
      const errors: string[] = [];
      page.on('pageerror', (err) => errors.push(err.message));
      page.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text());
      });

      const res = await page.goto(p.path, { waitUntil: 'networkidle' });
      expect(res?.status(), `${p.path} returned ${res?.status()}`).toBeLessThan(400);
      expect(errors, `console errors on ${p.path}:\n${errors.join('\n')}`).toHaveLength(0);
    });

    test(`${p.key} — shareable URL params round-trip (§7.4)`, async ({ page }) => {
      // Open with a known param; navigate to a state that should rewrite the URL; confirm the param survives.
      await page.goto(`${p.path}?share=1`, { waitUntil: 'domcontentloaded' });
      const interactive = await page.locator('[data-share-state]').first();
      const count = await interactive.count();
      test.skip(count === 0, `${p.key} has no elements with [data-share-state] — no shareable state to test`);
      await interactive.click();
      const url = new URL(page.url());
      expect(url.searchParams.has('share'), 'share param was dropped after interaction').toBeTruthy();
    });
  });
}
