// tests/release-check/freshness.spec.ts
// Enforces GUIDELINES.md §7.2 freshness dot colouring.
// Green ≤30 days, Yellow 31–90 days, Grey >90 days — driven by retrievedAt.

import { test, expect } from '@playwright/test';
import { loadSiteData, pages } from './helpers';

const pageList = pages(loadSiteData());

test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'freshness audit runs on desktop only');
});

for (const p of pageList) {
  test(`${p.key} — freshness dots match retrievedAt (§7.2)`, async ({ page }) => {
    await page.goto(p.path, { waitUntil: 'networkidle' });
    const today = Date.now();
    const mismatches = await page.evaluate((nowMs) => {
      const out: Array<{ retrievedAt: string; colour: string; expected: string }> = [];
      document.querySelectorAll('[data-freshness-dot][data-retrieved-at]').forEach((el) => {
        const iso = el.getAttribute('data-retrieved-at')!;
        const colour = getComputedStyle(el).backgroundColor;
        const ageDays = (nowMs - Date.parse(iso)) / (1000 * 60 * 60 * 24);
        let expected: 'green' | 'yellow' | 'grey';
        if (ageDays <= 30) expected = 'green';
        else if (ageDays <= 90) expected = 'yellow';
        else expected = 'grey';
        // Rough RGB match — the site's CSS is the source of truth, we just verify the bucket.
        const bucket = colour.includes('34, 197') || colour.includes('green') ? 'green'
          : colour.includes('250, 204') || colour.includes('yellow') || colour.includes('245, 158') ? 'yellow'
          : 'grey';
        if (bucket !== expected) out.push({ retrievedAt: iso, colour, expected });
      });
      return out;
    }, today);
    expect(mismatches, `freshness dot colour mismatches:\n${mismatches.map(m => `  ${m.retrievedAt}: expected ${m.expected}, got ${m.colour}`).join('\n')}`).toHaveLength(0);
  });
}
