// tests/release-check/mobile.spec.ts
// Enforces GUIDELINES.md §7.5 mobile test bar.
// Only runs on mobile-iphone and mobile-android projects.

import { test, expect } from '@playwright/test';
import { loadSiteData, pages, hasHorizontalScroll, undersizedTapTargets } from './helpers';

const pageList = pages(loadSiteData());

test.skip(({}, testInfo) => !testInfo.project.name.startsWith('mobile'), 'mobile gate runs on mobile projects only');

for (const p of pageList) {
  test.describe(`mobile — ${p.key}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(p.path, { waitUntil: 'networkidle' });
    });

    test(`${p.key} — no horizontal scroll (§7.5)`, async ({ page }) => {
      expect(await hasHorizontalScroll(page), 'page has horizontal scroll on mobile').toBeFalsy();
    });

    test(`${p.key} — tap targets ≥ 44px (§7.5)`, async ({ page }) => {
      const offenders = await undersizedTapTargets(page, 44);
      expect(
        offenders,
        `tap targets under 44px:\n${offenders.map(o => `  ${o.selector} ${o.w}×${o.h}`).join('\n')}`,
      ).toHaveLength(0);
    });

    test(`${p.key} — hero + headline metric visible within two viewport heights at 390×844 (§7.5)`, async ({ page, viewport }) => {
      test.skip(viewport?.width !== 390, 'iPhone viewport only');
      const headline = page.locator('[data-section="headline-metric"]').first();
      await expect(headline).toBeVisible();
      const box = await headline.boundingBox();
      expect(box?.y, 'headline metric must be within two viewport heights').toBeLessThan((viewport?.height ?? 844) * 2);
    });

    test(`${p.key} — body copy ≥ 16px (§7.5)`, async ({ page }) => {
      const tooSmall = await page.evaluate(() => {
        const offenders: string[] = [];
        document.querySelectorAll('p, li, td, span').forEach((el) => {
          const size = parseFloat(getComputedStyle(el).fontSize);
          if (size > 0 && size < 16 && (el as HTMLElement).innerText.trim().length > 0) {
            offenders.push(`${el.tagName.toLowerCase()} (${Math.round(size)}px): "${(el as HTMLElement).innerText.slice(0, 40)}"`);
          }
        });
        return offenders.slice(0, 10);
      });
      expect(tooSmall, `body copy under 16px on mobile:\n${tooSmall.join('\n')}`).toHaveLength(0);
    });

    test(`${p.key} — freshness dots, confidence badges, source links still visible on mobile (§7.5)`, async ({ page }) => {
      // Credibility signals must remain visible on mobile.
      await expect(page.locator('[data-freshness-dot]').first()).toBeVisible();
      await expect(page.locator('[data-confidence-badge]').first()).toBeVisible();
      await expect(page.locator('[data-source-link]').first()).toBeVisible();
    });
  });
}
