// tests/release-check/homepage.spec.ts
// wq-093 — DOM-level assertions on /index.html and a public-page sweep.
// Per CLAUDE.md "Validate rendered output, not just engine reports": this spec
// visits the homepage in a browser, lets the SCENARIOS init + site-data fetch
// settle, and asserts on the rendered DOM. Acceptance ties to brief §3 and §11.

import { test, expect } from '@playwright/test';
import { loadSiteData } from './helpers';

test.describe.configure({ mode: 'parallel' });
test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'homepage DOM checks run desktop only');
});

test.describe('index.html — wq-093 five-ledger reframe', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'networkidle' });
    // Allow the SCENARIOS init + site-data.json fetch to settle so dynamic
    // figures (Layer Stack Apps/Compute, hook ratio) reflect engine values.
    await page.waitForFunction(() => {
      const apps = document.getElementById('ls-apps');
      return apps && /\$\d/.test(apps.textContent || '');
    }, undefined, { timeout: 10_000 });
  });

  test('AC1 — masthead H2 + tagline carry the five-ledger framing; "three ledgers" absent', async ({ page }) => {
    await expect(page.locator('.masthead h2')).toHaveText('The AI economy, layer by layer.');
    await expect(page.locator('.masthead .tagline')).toContainText('Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system.');
    const body = (await page.locator('body').innerText()).toLowerCase();
    expect(body).not.toContain('three ledgers');
  });

  test('AC3 — Layer Stack hero renders 4 type-led rows with sparkbars (no SVG, no pyramid)', async ({ page }) => {
    const rows = page.locator('.layerstack-row');
    await expect(rows).toHaveCount(4);

    // Each row has eyebrow + figure + sparkbar.
    for (const layer of ['apps', 'compute', 'silicon', 'power']) {
      const row = page.locator(`.layerstack-row[data-layer="${layer}"]`);
      await expect(row).toBeVisible();
      await expect(row.locator('.ls-eyebrow')).toBeVisible();
      await expect(row.locator('.ls-figure')).toBeVisible();
      await expect(row.locator('.ls-bar')).toBeVisible();
    }

    // Click-throughs land on the right pages.
    expect(await page.locator('.layerstack-row[data-layer="apps"]').getAttribute('href')).toBe('revenue.html');
    expect(await page.locator('.layerstack-row[data-layer="compute"]').getAttribute('href')).toBe('compute.html');
    expect(await page.locator('.layerstack-row[data-layer="silicon"]').getAttribute('href')).toBe('capital.html');
    expect(await page.locator('.layerstack-row[data-layer="power"]').getAttribute('href')).toBe('power.html');

    // Editorial form: no SVG inside the layerstack hero, no pyramid term.
    const heroSvg = await page.locator('.layerstack-hero svg').count();
    expect(heroSvg).toBe(0);
    const heroText = (await page.locator('.layerstack-hero').innerText()).toLowerCase();
    expect(heroText).not.toContain('pyramid');
  });

  test('AC4 — hero strip has 5 tiles (Capital · Revenue · Compute · Usage · Power); Power is link-only', async ({ page }) => {
    const tiles = page.locator('#hero-numbers .hero-tile');
    await expect(tiles).toHaveCount(5);

    // Click-through hrefs.
    expect(await page.locator('#tile-capital').getAttribute('href')).toBe('capital.html');
    expect(await page.locator('#tile-revenue').getAttribute('href')).toBe('revenue.html');
    expect(await page.locator('#tile-compute').getAttribute('href')).toBe('compute.html');
    expect(await page.locator('#tile-usage').getAttribute('href')).toBe('usage.html');
    expect(await page.locator('#tile-power').getAttribute('href')).toBe('power.html');

    // Power tile is link-only: no .tier pill inside it.
    const powerTier = await page.locator('#tile-power .tier').count();
    expect(powerTier).toBe(0);

    // Hero sub-line copy.
    await expect(page.locator('.hero-sub')).toContainText('Five ledgers, triangulated from primary sources.');
  });

  test('AC4-data — Compute hero tile reads $43B; Revenue hero tile reads $17B (matches site-data.json)', async ({ page }) => {
    const data = loadSiteData();
    const apps = data.sankey?.totalCustomerRevenue;
    const compute = data.compute?.compute_revenue_2025_gross_usd_b;
    expect(apps).toBeGreaterThan(15);
    expect(apps).toBeLessThan(20);
    expect(compute).toBeGreaterThan(40);
    expect(compute).toBeLessThan(50);
    // Format we use: round to nearest $B with format-helpers.formatCurrency.
    await expect(page.locator('#hero-revenue')).toHaveText(/^\$1[67]B$/);
    await expect(page.locator('#hero-compute')).toHaveText(/^\$4[23]B$/);
  });

  test('AC5 — narrative flow is Apps → Compute → Silicon → Power (no Capital In / Assets Built)', async ({ page }) => {
    const h2 = await page.locator('.narrative h2').innerText();
    expect(h2).toContain('Apps Revenue');
    expect(h2).toContain('Compute');
    expect(h2).toContain('Silicon');
    expect(h2).toContain('Power');

    // .step-label has text-transform:uppercase via CSS; compare case-insensitive.
    const labels = (await page.locator('.flow-step .step-label').allInnerTexts()).map(s => s.toLowerCase());
    expect(labels).toEqual(['apps revenue', 'compute earned', 'silicon', 'power']);
  });

  test('AC6 — hook one-liner is Compute-anchored ($X.XX of compute spend / $1 Apps Revenue)', async ({ page }) => {
    const ratio = await page.locator('#hook-ratio').innerText();
    expect(ratio).toMatch(/^\$\d+\.\d{2}$/);
    const sentence = (await page.locator('.hero-hook .hook-number').innerText()).toLowerCase();
    expect(sentence).toContain('compute spend');
    expect(sentence).toContain('apps revenue');
    // Old hook is gone.
    expect(sentence).not.toContain('infrastructure stands behind');
  });

  test('AC7 — live tile is the Compute Revenue 2025 signal ($43B / +153% / 79%); Copilot/Agentforce gone', async ({ page }) => {
    await expect(page.locator('#lt-value')).toHaveText(/^\$4[23]B$/);
    const subline = (await page.locator('#lt-subline').innerText()).toLowerCase();
    expect(subline).toContain('ai compute revenue');
    expect(subline).toContain('+153%');
    expect(subline).toContain('79%');
    const wrap = (await page.locator('.live-tile').innerText()).toLowerCase();
    expect(wrap).not.toContain('copilot');
    expect(wrap).not.toContain('agentforce');
  });

  test('AC8 — ledger cards = 5 (Capital, Revenue, Compute, Usage, Power); Power card is link-only', async ({ page }) => {
    const cards = page.locator('.ledger-cards .ledger-card');
    await expect(cards).toHaveCount(5);

    const titles = await cards.locator('.lc-title').allInnerTexts();
    expect(titles).toEqual(['Capital Ledger', 'Revenue Ledger', 'Compute Ledger', 'Usage Ledger', 'Power Ledger']);

    // Power card carries .is-link-only (no tier pills, no big number).
    const powerCard = cards.nth(4);
    await expect(powerCard).toHaveClass(/is-link-only/);
    const powerTierPills = await powerCard.locator('.tier-pill').count();
    expect(powerTierPills).toBe(0);
  });

  test('AC9 — footer "Ledger pages" lists all five (Capital, Revenue, Compute, Usage, Power)', async ({ page }) => {
    const footerLinks = await page.locator('.ds-footer__col').first().locator('a').allInnerTexts();
    expect(footerLinks).toEqual(expect.arrayContaining(['Capital', 'Revenue', 'Compute', 'Usage', 'Power']));
  });
});

test.describe('Public-page sweep — wq-093 §3.2 "three ledgers" absent', () => {
  for (const path of ['/index.html', '/capital.html', '/revenue.html', '/compute.html', '/usage.html', '/power.html', '/methodology.html', '/about.html']) {
    test(`${path} contains no "three ledgers" string`, async ({ page }) => {
      await page.goto(path, { waitUntil: 'domcontentloaded' });
      const body = (await page.locator('body').innerText()).toLowerCase();
      expect(body).not.toContain('three ledgers');
    });
  }
});
