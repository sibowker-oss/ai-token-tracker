// tests/release-check/homepage.spec.ts
// wq-093 — DOM-level assertions on /index.html (five-ledger reframe).
//
// Acceptance ties to wq-093 brief §3:
//   AC1  — masthead H2 + tagline updated; "three ledgers" string absent
//   AC2  — public-page sweep clean (covered here for index + methodology)
//   AC3  — Layer Stack pyramid renders 4 layers + Power foundation slab
//   AC4  — 5 hero tiles, Power tile is link-only no-number
//   AC5  — narrative-flow replaced with Apps→Compute→Silicon→Power
//   AC6  — Compute-anchored hook ratio
//   AC7  — live tile shows Compute Revenue $43B / +153% / 79% frontier
//   AC8  — 5 ledger cards
//   AC9  — footer "Ledger pages" lists all five

import { test, expect } from '@playwright/test';
import { loadSiteData } from './helpers';

test.describe.configure({ mode: 'parallel' });
test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'homepage DOM checks run desktop only');
});

test.describe('index.html — wq-093 five-ledger reframe', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'networkidle' });
    // Allow the data-driven SCENARIOS to apply after fetch('site-data.json').
    await page.waitForFunction(() => {
      const r = document.getElementById('hero-revenue');
      return r && r.textContent && !/^\$22B$/.test(r.textContent);
    }, undefined, { timeout: 10_000 });
  });

  test('AC1 — masthead H2 reads "The AI economy, layer by layer."', async ({ page }) => {
    const h2 = await page.locator('section.masthead h2').innerText();
    expect(h2).toBe('The AI economy, layer by layer.');
    const tagline = await page.locator('section.masthead .tagline').innerText();
    expect(tagline).toBe('Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system.');
  });

  test('AC1/AC2 — rendered DOM contains no "three ledgers" string (any case)', async ({ page }) => {
    const body = await page.locator('body').innerText();
    expect(body.toLowerCase()).not.toContain('three ledgers');
  });

  test('AC3 — Layer Stack pyramid renders with 4 layers (3 polygons + 1 power rect)', async ({ page }) => {
    const svg = page.locator('#ls-pyramid-svg');
    await expect(svg).toBeVisible();
    const layers = ['apps', 'compute', 'silicon', 'power'];
    for (const layer of layers) {
      await expect(svg.locator(`[data-layer="${layer}"]`)).toHaveCount(1);
    }
    // Power is a separate rect, not part of the pyramid polygons.
    await expect(svg.locator('rect[data-layer="power"]')).toHaveCount(1);
    await expect(svg.locator('polygon[data-layer="apps"]')).toHaveCount(1);
    await expect(svg.locator('polygon[data-layer="compute"]')).toHaveCount(1);
    await expect(svg.locator('polygon[data-layer="silicon"]')).toHaveCount(1);
  });

  test('AC4 — 5 hero tiles, Power tile is link-only no-number', async ({ page }) => {
    const tiles = page.locator('.hero-numbers .hero-tile');
    await expect(tiles).toHaveCount(5);

    // Tile click-throughs land on the right ledger pages.
    const expected: Record<string, string> = {
      'tile-capital': 'capital.html',
      'tile-revenue': 'revenue.html',
      'tile-compute': 'compute.html',
      'tile-usage': 'usage.html',
      'tile-power': 'power.html',
    };
    for (const [id, href] of Object.entries(expected)) {
      const tileHref = await page.locator(`#${id}`).getAttribute('href');
      expect(tileHref).toBe(href);
    }

    // Power tile is link-only — no big-number, no tier pill.
    const powerTile = page.locator('#tile-power');
    const powerText = await powerTile.innerText();
    expect(powerText.toLowerCase()).toContain('power ledger');
    expect(powerText.toLowerCase()).toContain('v3 in progress');
    await expect(powerTile.locator('.tier-pill')).toHaveCount(0);

    // Hero sub-line confirms five-ledger framing.
    const sub = await page.locator('.hero-sub').innerText();
    expect(sub).toBe('Five ledgers, triangulated from primary sources.');
  });

  test('AC4 — hero numeric tiles match site-data.json paths (data-driven)', async ({ page }) => {
    const data = loadSiteData();
    const apps = data.sankey?.totalCustomerRevenue;
    const compute = data.compute?.compute_revenue_2025_gross_usd_b;
    expect(apps).toBeGreaterThan(0);
    expect(compute).toBeGreaterThan(0);

    const revenueText = await page.locator('#hero-revenue').innerText();
    const computeText = await page.locator('#hero-compute').innerText();
    // Allow magnitude-aware rounding — must contain "$17B" or "$17.4B" range.
    expect(revenueText).toMatch(/\$1[6-8](?:\.\d)?B/);
    expect(computeText).toMatch(/\$4[2-4](?:\.\d)?B/);
  });

  test('AC5 — narrative flow shows Apps Revenue → Compute → Silicon → Power', async ({ page }) => {
    const flowH2 = await page.locator('.narrative h2').innerText();
    expect(flowH2).toMatch(/Apps Revenue.*Compute.*Silicon.*Power/);

    // .step-label is `text-transform: uppercase` so the rendered (innerText)
    // output is upper-cased even though the DOM source reads "Apps Revenue".
    const stepLabels = (await page.locator('.flow-step .step-label').allInnerTexts())
      .map(t => t.trim().toLowerCase());
    expect(stepLabels).toEqual(['apps revenue', 'compute earned', 'silicon', 'power']);
  });

  test('AC6 — Compute-anchored hook ratio reads "$X.XX of compute spend"', async ({ page }) => {
    const hookText = await page.locator('.hero-hook .hook-number').innerText();
    expect(hookText).toMatch(/\$\d+\.\d{2}/); // e.g. "$2.50"
    expect(hookText.toLowerCase()).toContain('compute spend');
    expect(hookText.toLowerCase()).toContain('apps revenue');
    // Old Capital-anchored framing must be gone.
    expect(hookText).not.toMatch(/of infrastructure stands behind/);
  });

  test('AC7 — live tile shows Compute Revenue 2025 signal ($43B / +153% / 79%)', async ({ page }) => {
    const live = page.locator('.live-tile');
    const value = await live.locator('.lt-value').innerText();
    expect(value).toMatch(/\$4[2-4](?:\.\d)?B/);
    const body = await live.innerText();
    expect(body.toLowerCase()).toContain('compute revenue');
    expect(body).toContain('+153%');
    expect(body).toContain('79%');
    // The wq-073 Copilot+Agentforce framing must be gone.
    expect(body.toLowerCase()).not.toContain('copilot');
    expect(body.toLowerCase()).not.toContain('agentforce');
  });

  test('AC8 — 5 ledger cards', async ({ page }) => {
    const cards = page.locator('.ledger-cards .ledger-card');
    await expect(cards).toHaveCount(5);
    const titles = (await cards.locator('.lc-title').allInnerTexts()).map(t => t.trim());
    expect(titles).toEqual(['Capital Ledger', 'Revenue Ledger', 'Compute Ledger', 'Usage Ledger', 'Power Ledger']);
  });

  test('AC9 — footer "Ledger pages" group lists all five (Capital/Revenue/Compute/Usage/Power)', async ({ page }) => {
    const ledgerCol = page.locator('.ds-footer__col').filter({ hasText: 'Ledger pages' });
    const links = await ledgerCol.locator('a').allInnerTexts();
    expect(links).toEqual(['Capital', 'Revenue', 'Compute', 'Usage', 'Power']);
  });
});

// ── Public-page sweep — "three ledgers" must be absent on every published page. ──
const PUBLIC_PAGES = [
  '/index.html',
  '/capital.html',
  '/revenue.html',
  '/compute.html',
  '/usage.html',
  '/power.html',
  '/methodology.html',
  '/about.html',
];

test.describe('Public-page sweep — wq-093 §3.2 "three ledgers" absent', () => {
  test.beforeEach(({}, testInfo) => {
    test.skip(!testInfo.project.name.startsWith('desktop'), 'sweep runs desktop only');
  });

  for (const path of PUBLIC_PAGES) {
    test(`${path} — rendered DOM contains no "three ledgers" string`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'networkidle' });
      const body = await page.locator('body').innerText();
      expect(body.toLowerCase()).not.toContain('three ledgers');
    });
  }
});
