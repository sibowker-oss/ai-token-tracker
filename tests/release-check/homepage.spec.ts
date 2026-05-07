// tests/release-check/homepage.spec.ts
// wq-093 — DOM-level assertions on /index.html and a public-page sweep.
// Per CLAUDE.md "Validate rendered output, not just engine reports": this spec
// visits the homepage in a browser, lets the SCENARIOS init + site-data fetch
// settle, and asserts on the rendered DOM. Acceptance ties to brief §3 and §11.
//
// Layout reference: D1 Option I — five horizontal pill bars (AI Infrastructure
// Stack) replaces the prior Option F type-led editorial layout, AND the 5-tile
// hero reconciliation strip (D3: dropped), AND the 4-step narrative-flow loop
// (D4: dropped). The bars carry all three jobs in a single hero section.

import { test, expect } from '@playwright/test';
import { loadSiteData } from './helpers';

test.describe.configure({ mode: 'parallel' });
test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'homepage DOM checks run desktop only');
});

test.describe('index.html — wq-093 five-ledger reframe (Option I)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index.html', { waitUntil: 'networkidle' });
    // Allow the SCENARIOS init + site-data.json fetch to settle so the dynamically
    // computed hook ratio reflects engine values.
    await page.waitForFunction(() => {
      const ratio = document.getElementById('hook-ratio');
      return ratio && /\$\d+\.\d{2}/.test(ratio.textContent || '');
    }, undefined, { timeout: 10_000 });
  });

  test('AC1 — masthead H2 + tagline carry the five-ledger framing; "three ledgers" absent', async ({ page }) => {
    await expect(page.locator('.masthead h2')).toHaveText('The AI economy, layer by layer.');
    await expect(page.locator('.masthead .tagline')).toContainText('Capital in. Compute spent. Power drawn. Tokens out. Revenue back. Five ledgers, one system.');
    const body = (await page.locator('body').innerText()).toLowerCase();
    expect(body).not.toContain('three ledgers');
  });

  test('AC3 — AI Infrastructure Stack renders 5 pill bars (Capex → Usage → Compute → Power → Revenue) with correct hrefs', async ({ page }) => {
    const section = page.locator('section.ai-infra-stack');
    await expect(section).toBeVisible();
    await expect(section.locator('.ais-title')).toHaveText('AI Infrastructure Stack');

    const bars = page.locator('.ais-bars .ais-bar');
    await expect(bars).toHaveCount(5);

    // Click-through hrefs match the brief's per-bar links (§5 Interactivity).
    const expectations: Array<[string, string]> = [
      ['capex',   'capital.html'],
      ['usage',   'usage.html'],
      ['compute', 'compute.html'],
      ['power',   'power.html'],
      ['revenue', 'revenue.html'],
    ];
    for (const [ledger, href] of expectations) {
      const bar = page.locator(`.ais-bar[data-ledger="${ledger}"]`);
      await expect(bar).toBeVisible();
      expect(await bar.getAttribute('href')).toBe(href);
      await expect(bar.locator('.ais-icon')).toBeVisible();
      await expect(bar.locator('.ais-label')).toBeVisible();
    }

    // Native HTML+CSS — no SVG, no canvas inside the section.
    expect(await section.locator('svg').count()).toBe(0);
    expect(await section.locator('canvas').count()).toBe(0);
  });

  test('AC3 — bar widths follow the locked descending profile (100/50/30/22/17 %)', async ({ page }) => {
    const widthOf = async (ledger: string) =>
      page.locator(`.ais-bar[data-ledger="${ledger}"]`).evaluate((el: HTMLElement) =>
        el.style.getPropertyValue('--bar-w').trim()
      );
    expect(await widthOf('capex')).toBe('100%');
    expect(await widthOf('usage')).toBe('50%');
    expect(await widthOf('compute')).toBe('30%');
    expect(await widthOf('power')).toBe('22%');
    expect(await widthOf('revenue')).toBe('17%');
  });

  test('AC3 — Power bar carries an inline tier-3 pill (TIER 3 · v3 PENDING) per brief §5 Tier disclosure', async ({ page }) => {
    const powerBar = page.locator('.ais-bar[data-ledger="power"]');
    const pill = powerBar.locator('.pill-mini.tier-3');
    await expect(pill).toBeVisible();
    expect((await pill.innerText()).toUpperCase()).toContain('TIER 3');
    expect((await pill.innerText()).toUpperCase()).toContain('v3 PENDING'.toUpperCase());
  });

  test('AC3 — footer stat cards removed (Simon 2026-05-07: redundant with the ledger cards + hook line below)', async ({ page }) => {
    expect(await page.locator('.ais-footer-stats').count()).toBe(0);
    expect(await page.locator('.ais-stat-card').count()).toBe(0);
  });

  test('AC3 — caption carries the §6.2 lock copy ("Read this stack this way")', async ({ page }) => {
    const cap = (await page.locator('.ais-caption').innerText()).toLowerCase();
    expect(cap).toContain('read this stack this way');
    expect(cap).toContain('every $1');
    expect(cap).toContain('hyperscaler equity');
    // Per-ratio anchors in the editorial sentence:
    expect(cap).toContain('$19');
    expect(cap).toContain('$2.50');
    expect(cap).toContain('$1.40');
  });

  test('AC3-data — Compute and Revenue bar figures match site-data.json (within the engine band)', async ({ page }) => {
    const data = loadSiteData();
    const apps = data.sankey?.totalCustomerRevenue;
    const compute = data.compute?.compute_revenue_2025_gross_usd_b;
    expect(apps).toBeGreaterThan(15);
    expect(apps).toBeLessThan(20);
    expect(compute).toBeGreaterThan(40);
    expect(compute).toBeLessThan(50);
    // Revenue bar reads the cohort total ($17.x B → "$17B"); Compute bar reads
    // the gross sum-of-Q ($43.x B → keep as "$43.1B" literal per brief §5).
    await expect(page.locator('#ais-revenue-figure')).toContainText(/\$1[67]/);
    await expect(page.locator('#ais-compute-figure')).toContainText(/\$4[23]/);
  });

  test('AC4 — hero reconciliation tile strip is removed (no .hero-numbers anywhere on the page)', async ({ page }) => {
    expect(await page.locator('.hero-numbers').count()).toBe(0);
    expect(await page.locator('.hero-tile').count()).toBe(0);
  });

  test('AC5 — narrative-flow section is removed (no .flow-steps anywhere on the page)', async ({ page }) => {
    expect(await page.locator('.flow-steps').count()).toBe(0);
    expect(await page.locator('.flow-step').count()).toBe(0);
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
