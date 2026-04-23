// tests/release-check/visual.spec.ts
// Screenshot baselines per page × project. Catches unintended visual regressions.
// Intentional visual changes: `npm run release-check:update-baselines`.
// Tolerance: 0.2% pixel diff (configured in playwright.config.ts).

import { test, expect } from '@playwright/test';
import { loadSiteData, pages } from './helpers';

const pageList = pages(loadSiteData());

for (const p of pageList) {
  test(`${p.key} — visual baseline`, async ({ page }, testInfo) => {
    await page.goto(p.path, { waitUntil: 'networkidle' });
    // Let web fonts + chart animations settle.
    await page.evaluate(() => document.fonts?.ready);
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot(`${p.key}.png`, {
      fullPage: true,
      animations: 'disabled',
      caret: 'hide',
    });
  });
}
