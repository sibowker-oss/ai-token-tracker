// tests/release-check/compute.spec.ts
// wq-089 — DOM-level assertions on /compute.html.
// Per CLAUDE.md "Validate rendered output, not just engine reports": this spec
// visits the page in a browser, lets the canvas + JSON-driven JS render, and
// asserts on the rendered DOM (not just on site-data.json:compute internals).
//
// Acceptance ties to wq-089 brief §"Acceptance criteria":
//   - Hero strip has gross / net / Apps→Compute / YoY (no share-shift box)
//   - Bucket 1 card present, with per-lab attribution rows
//   - Concentration headline leads on bucket-1 framing (D5 lede)
//   - Layer Stack visual present and labelled "lookback / sum-of-quarterlies"

import { test, expect } from '@playwright/test';
import { loadSiteData } from './helpers';

// Single project — DOM-level assertions, no need to repeat across viewports.
test.describe.configure({ mode: 'parallel' });
test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'compute DOM checks run desktop only');
});

test.describe('compute.html — wq-089 DOM assertions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/compute.html', { waitUntil: 'networkidle' });
    // Allow chart-init and async fetch('site-data.json') to settle.
    await page.waitForFunction(() => {
      const lede = document.getElementById('concentration-lede');
      return lede && lede.textContent && !lede.textContent.includes('Loading');
    }, undefined, { timeout: 10_000 });
  });

  test('concentration headline leads on bucket-1 / circular-financing framing (D5)', async ({ page }) => {
    const lede = await page.locator('#concentration-lede').innerText();
    expect(lede.toLowerCase()).toContain('frontier model labs');
    expect(lede.toLowerCase()).toMatch(/compute providers?/);
    // The wq-089 lede must NOT lead on Mag3 share (that was the wq-087 framing).
    expect(lede.startsWith('Microsoft, Google, and Amazon capture')).toBe(false);
  });

  test('hero strip has 4 stats — gross / net / Apps→Compute / YoY (NOT share-shift)', async ({ page }) => {
    const heroStats = page.locator('#hero-stats .hero-stat');
    await expect(heroStats).toHaveCount(4);

    const labels = await heroStats.locator('.label').allInnerTexts();
    // Every box must be present.
    expect(labels.some(l => /Compute Revenue 2025 · gross/i.test(l))).toBe(true);
    expect(labels.some(l => /Compute Revenue 2025 · net/i.test(l))).toBe(true);
    expect(labels.some(l => /Apps Revenue → Compute/i.test(l))).toBe(true);
    expect(labels.some(l => /YoY growth/i.test(l))).toBe(true);
    // The wq-087 share-shift box is gone (D4).
    expect(labels.some(l => /share shift/i.test(l))).toBe(false);
  });

  test('Bucket 1 card is present with per-lab attribution rows', async ({ page }) => {
    const card = page.locator('#bucket-1-card');
    await expect(card).toBeVisible();

    const heading = card.locator('h2').first();
    await expect(heading).toContainText(/Bucket 1/i);
    await expect(heading).toContainText(/Frontier-lab compute/i);

    // Must show per-component attribution rows (Mag3 + Oracle + neoclouds).
    const rows = card.locator('[data-bucket-1-row]');
    expect(await rows.count()).toBeGreaterThanOrEqual(6);

    // OpenAI / Anthropic must appear somewhere in the attribution copy.
    const body = await card.innerText();
    expect(body).toMatch(/OpenAI/);
    expect(body).toMatch(/Anthropic/);
  });

  test('Layer Stack visual is on lookback 2025 sum-of-quarterlies basis (D3)', async ({ page }) => {
    const ls = page.locator('.layer-stack');
    await expect(ls).toBeVisible();
    const title = await ls.locator('.layer-stack-title').innerText();
    expect(title).toMatch(/lookback/i);
    expect(title).toMatch(/sum-of-quarterlies/i);
    // Editorial extension to ecosystem ($100B 5x multiplier) is gone.
    expect(title).not.toMatch(/100B/);
  });

  test('headline values match site-data.json:compute (renderer-data agreement)', async ({ page }) => {
    const data = loadSiteData();
    const c = data.compute;
    expect(c).toBeDefined();
    // The renderer formats $XYZ.YB; sanity-check that the gross box contains
    // the 2025 gross figure as displayed.
    const grossText = await page.locator('#hero-stats .hero-stat').nth(0).locator('.value').innerText();
    // grossText looks like "$65.5B" — extract the number and confirm within
    // 0.1 (rounding) of compute_revenue_2025_gross_usd_b.
    const m = grossText.match(/\$([\d.]+)B/);
    expect(m).not.toBeNull();
    if (m) {
      const rendered = parseFloat(m[1]);
      expect(Math.abs(rendered - (c.compute_revenue_2025_gross_usd_b ?? 0))).toBeLessThan(0.2);
    }
  });

  test('WWHBT panel exposes Bucket-1-share signal (new in wq-089)', async ({ page }) => {
    const wwhbt = page.locator('#wwhbt-grid');
    await expect(wwhbt).toBeVisible();
    const text = await wwhbt.innerText();
    expect(text).toMatch(/Bucket 1 share/i);
    // The wq-087 pass-through threshold of >15% is gone (was overstated).
    expect(text).toMatch(/Pass-through gap.*bucket 3/i);
  });
});
