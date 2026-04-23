// tests/release-check/structure.spec.ts
// Enforces GUIDELINES.md §7.3 standard page order and §8 Hepburn brand treatment.
// Section order: hero → headline metric → benchmark cards → primary viz → supporting viz → methodology → open questions → last-updated footer.

import { test, expect } from '@playwright/test';
import { loadSiteData, pages } from './helpers';

const pageList = pages(loadSiteData());

// Project filter — structure is layout-level, check on desktop only to avoid six × pages redundancy.
test.describe.configure({ mode: 'parallel' });
test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'structure is checked on desktop only');
});

for (const p of pageList) {
  test.describe(`structure — ${p.key}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(p.path, { waitUntil: 'networkidle' });
    });

    test(`${p.key} has all §7.3 sections in order`, async ({ page }) => {
      const expected = [
        '[data-section="hero"]',
        '[data-section="headline-metric"]',
        '[data-section="benchmark-cards"]',
        '[data-section="primary-viz"]',
        '[data-section="methodology"]',
        '[data-section="open-questions"]',
        '[data-section="last-updated"]',
      ];
      const positions: number[] = [];
      for (const sel of expected) {
        const loc = page.locator(sel);
        await expect(loc, `missing section ${sel}`).toHaveCount(1);
        const box = await loc.boundingBox();
        positions.push(box?.y ?? Infinity);
      }
      for (let i = 1; i < positions.length; i++) {
        expect(positions[i], `§7.3 order: ${expected[i]} should come after ${expected[i - 1]}`).toBeGreaterThan(positions[i - 1]);
      }
    });

    test(`${p.key} methodology block is a functional collapsible (§2.4)`, async ({ page }) => {
      test.skip(!p.hasDerivedNumbers, `${p.key} does not carry derived numbers`);
      const trigger = page.locator('[data-section="methodology"] [data-collapsible-trigger]').first();
      await expect(trigger).toBeVisible();
      const panel = page.locator('[data-section="methodology"] [data-collapsible-panel]').first();
      // Expect collapsed on load
      await expect(panel).toBeHidden();
      await trigger.click();
      await expect(panel).toBeVisible();
    });

    test(`${p.key} Hepburn brand treatment per §8`, async ({ page }) => {
      // Footer wordmark
      await expect(page.locator('footer [data-hepburn-wordmark]')).toHaveCount(1);
      // Byline sits under methodology, not above the fold
      const byline = page.locator('[data-hepburn-byline]');
      await expect(byline).toHaveCount(1);
      const methodology = page.locator('[data-section="methodology"]');
      const byBox = await byline.boundingBox();
      const methBox = await methodology.boundingBox();
      expect(byBox?.y, 'byline must sit below methodology block').toBeGreaterThan(methBox?.y ?? 0);
      // Max one CTA below the fold
      const ctas = page.locator('[data-hepburn-cta]');
      expect(await ctas.count(), '§8: max one Hepburn CTA per page').toBeLessThanOrEqual(1);
    });
  });
}
