// tests/release-check/compute.spec.ts
// wq-091 — DOM-level assertions on /compute.html.
// Per CLAUDE.md "Validate rendered output, not just engine reports": this spec
// visits the page in a browser, lets the canvas + JSON-driven JS render, and
// asserts on the rendered DOM (not just on site-data.json:compute internals).
//
// Acceptance ties to wq-091 brief §"Acceptance criteria":
//   - Hero strip has gross / net / Apps→Compute / YoY (no share-shift box)
//   - Frontier lab compute card present, with per-lab attribution rows
//   - Concentration headline leads on circular-financing framing
//   - Layer Stack visual present and labelled "lookback / sum-of-quarterlies"
//   - No "Bucket 1/2/3" or "B1/B2/B3" anywhere in rendered DOM (D8)

import { test, expect } from '@playwright/test';
import { loadSiteData } from './helpers';

// Single project — DOM-level assertions, no need to repeat across viewports.
test.describe.configure({ mode: 'parallel' });
test.beforeEach(({}, testInfo) => {
  test.skip(!testInfo.project.name.startsWith('desktop'), 'compute DOM checks run desktop only');
});

test.describe('compute.html — wq-091 DOM assertions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/compute.html', { waitUntil: 'networkidle' });
    // Allow chart-init and async fetch('site-data.json') to settle.
    await page.waitForFunction(() => {
      const lede = document.getElementById('concentration-lede');
      return lede && lede.textContent && !lede.textContent.includes('Loading');
    }, undefined, { timeout: 10_000 });
  });

  test('concentration headline leads on Frontier lab compute / circular-financing framing', async ({ page }) => {
    const lede = await page.locator('#concentration-lede').innerText();
    expect(lede.toLowerCase()).toContain('frontier model labs');
    expect(lede.toLowerCase()).toMatch(/compute providers?/);
    // The wq-089 lede must NOT lead on Mag3 share (that was the wq-087 framing).
    expect(lede.startsWith('Microsoft, Google, and Amazon capture')).toBe(false);
  });

  test('hero strip has 4 stats — net / pass-through / Apps→Compute / YoY (NOT share-shift)', async ({ page }) => {
    const heroStats = page.locator('#hero-stats .hero-stat');
    await expect(heroStats).toHaveCount(4);

    const labels = await heroStats.locator('.label').allInnerTexts();
    // Box 1 = Compute Revenue 2025 · net (post-edit: net leads instead of gross)
    expect(labels.some(l => /Compute Revenue 2025 · net/i.test(l))).toBe(true);
    // Box 2 = Total Model Pass-through Revenue 2025 (replaces gross box)
    expect(labels.some(l => /Total Model Pass-through Revenue/i.test(l))).toBe(true);
    expect(labels.some(l => /Apps Revenue → Compute/i.test(l))).toBe(true);
    expect(labels.some(l => /YoY growth/i.test(l))).toBe(true);
    expect(labels.some(l => /share shift/i.test(l))).toBe(false);
  });

  test('Frontier lab compute card is present with per-provider attribution rows', async ({ page }) => {
    const card = page.locator('#frontier-lab-compute-card');
    await expect(card).toBeVisible();

    const heading = card.locator('h2').first();
    await expect(heading).toContainText(/Frontier lab compute/i);
    // The wq-089 "Bucket 1" prefix must NOT appear in this heading.
    await expect(heading).not.toContainText(/Bucket 1/i);

    // Must show per-component attribution rows (Mag3 + Oracle + neoclouds).
    const rows = card.locator('[data-frontier-lab-compute-row]');
    expect(await rows.count()).toBeGreaterThanOrEqual(6);

    // OpenAI / Anthropic must appear somewhere in the attribution copy.
    const body = await card.innerText();
    expect(body).toMatch(/OpenAI/);
    expect(body).toMatch(/Anthropic/);
  });

  test('Layer Stack visual is on lookback 2025 sum-of-quarterlies basis', async ({ page }) => {
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
    // Box 1 is now Compute Revenue 2025 · net (post-edit, replaces previous gross-leading box).
    const netText = await page.locator('#hero-stats .hero-stat').nth(0).locator('.value').innerText();
    const m = netText.match(/\$([\d.]+)B/);
    expect(m).not.toBeNull();
    if (m) {
      const rendered = parseFloat(m[1]);
      expect(Math.abs(rendered - (c.compute_revenue_2025_net_usd_b ?? 0))).toBeLessThan(0.2);
    }
  });

  test('WWHBT panel exposes Frontier lab compute share signal', async ({ page }) => {
    const wwhbt = page.locator('#wwhbt-grid');
    await expect(wwhbt).toBeVisible();
    const text = await wwhbt.innerText();
    expect(text).toMatch(/Frontier lab compute share/i);
    // Pass-through is scoped to Hosted model APIs only.
    expect(text).toMatch(/Hosted model APIs/i);
  });

  // wq-091 D8 — plain-English naming everywhere; rendered DOM must contain
  // no "Bucket 1/2/3" or "B1/B2/B3" strings anywhere.
  test('rendered DOM contains no legacy "Bucket 1/2/3" or "B1/B2/B3" strings', async ({ page }) => {
    const bodyText = await page.locator('body').innerText();
    // Filename references in code blocks (e.g. dec-2026-05-06-compute-ledger-bucket-sizing.md)
    // are historical artifacts and intentionally retained; the spec checks for
    // the engineering shorthand strings used in copy, not filename substrings.
    expect(bodyText).not.toMatch(/\bBucket 1\b/);
    expect(bodyText).not.toMatch(/\bBucket 2\b/);
    expect(bodyText).not.toMatch(/\bBucket 3\b/);
    expect(bodyText).not.toMatch(/\bbucket-1\b/);
    expect(bodyText).not.toMatch(/\bbucket-2\b/);
    expect(bodyText).not.toMatch(/\bbucket-3\b/);
    expect(bodyText).not.toMatch(/\bB1\/B2\/B3\b/);
    expect(bodyText).not.toMatch(/\bB1\b/);
    expect(bodyText).not.toMatch(/\bB2\b/);
    expect(bodyText).not.toMatch(/\bB3\b/);
  });
});
