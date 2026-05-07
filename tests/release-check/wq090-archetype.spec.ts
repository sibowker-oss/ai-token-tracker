// tests/release-check/wq090-archetype.spec.ts
// wq-090 — Verifies the per-archetype channel routing landed correctly:
//   1. Revenue Ledger Sankey buyer labels relabel to AI Natives / Enterprises & Govs
//      (SME / Enterprise are gone)
//   2. Hyperscalers channel value is in the $1.5–2.0B target band per D4
//   3. /revenue.html exposes the new methodology callout linking to the
//      archetype-taxonomy section on /methodology.html
//
// The spec walks the data files (site-data.json, data/sankey-projections.json)
// for value assertions and visits /revenue.html for the rendered-output assertion.

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { test, expect } from '@playwright/test';

const ROOT = process.cwd();

function loadJson(rel: string): any {
  return JSON.parse(readFileSync(join(ROOT, rel), 'utf8'));
}

test.describe('wq-090 — per-archetype channel routing', () => {
  test('site-data.json:sankey.buyers uses AI Natives / Enterprises & Govs labels', () => {
    const sd = loadJson('site-data.json');
    const labels = (sd.sankey?.buyers ?? []).map((b: any) => b.label);
    expect(labels, 'sankey.buyers labels').toEqual([
      'Consumer',
      'AI Natives',
      'Enterprises & Govs',
      'VC/Investors',
    ]);
    // SME and Enterprise must NOT be present anywhere in the buyers list
    expect(labels).not.toContain('SME');
    expect(labels).not.toContain('Enterprise');
  });

  test('site-data.json:sankey.channels Hyperscalers in $1.5–2.0B target band (D4)', () => {
    const sd = loadJson('site-data.json');
    const hyper = (sd.sankey?.channels ?? []).find((c: any) => c.label === 'Hyperscalers');
    expect(hyper, 'Hyperscalers channel').toBeTruthy();
    expect(hyper.value, 'Hyperscalers value').toBeGreaterThanOrEqual(1.5);
    expect(hyper.value, 'Hyperscalers value').toBeLessThanOrEqual(2.0);
  });

  test('AI Natives buyer segment has non-trivial value', () => {
    const sd = loadJson('site-data.json');
    const aiNatives = (sd.sankey?.buyers ?? []).find((b: any) => b.label === 'AI Natives');
    expect(aiNatives, 'AI Natives buyer').toBeTruthy();
    expect(aiNatives.value, 'AI Natives value').toBeGreaterThan(1.0);
  });

  test('sankey-projections.json 2025 buyers use the new labels', () => {
    const sp = loadJson('data/sankey-projections.json');
    const labels = (sp['2025']?.buyers ?? []).map((b: any) => b.label);
    expect(labels).toContain('AI Natives');
    expect(labels).toContain('Enterprises & Govs');
    expect(labels).not.toContain('SME');
  });

  test('site-data.json:sankey.buyerProviderRouting AI Natives split is 45/45/10', () => {
    const sd = loadJson('site-data.json');
    const an = sd.sankey?.buyerProviderRouting?.['AI Natives'] ?? {};
    const total = (an.openai || 0) + (an.anthropic || 0) + (an.google || 0);
    expect(total, 'AI Natives → OAI/Anth/Goog total').toBeGreaterThan(4.5);
    // Allow ±2pp tolerance to absorb engine drift between buyer_net and the 45/45/10 spec
    expect(an.openai / total, 'OpenAI share').toBeGreaterThan(0.43);
    expect(an.openai / total, 'OpenAI share').toBeLessThan(0.47);
    expect(an.anthropic / total, 'Anthropic share').toBeGreaterThan(0.43);
    expect(an.anthropic / total, 'Anthropic share').toBeLessThan(0.47);
    expect(an.google / total, 'Google share').toBeGreaterThan(0.08);
    expect(an.google / total, 'Google share').toBeLessThan(0.12);
    // Other / IaaS get ~$0 from AI Natives per editorial split
    expect(an._other_model_providers || 0).toBeLessThan(0.01);
    expect(an.iaas || 0).toBeLessThan(0.01);
  });

  test('/revenue.html renders the per-archetype methodology callout', async ({ page }, testInfo) => {
    test.skip(!testInfo.project.name.startsWith('desktop'), 'callout copy check on desktop only');
    await page.goto('/revenue.html', { waitUntil: 'networkidle' });
    // Callout text references the new buyer labels and links to methodology section
    const callout = page.locator('a[href="/methodology.html#revenue-archetype-taxonomy"]');
    // ≥1 because the buyer-provider panel (wq-090) adds a second link to the same anchor
    expect(await callout.count(), 'methodology archetype-taxonomy link').toBeGreaterThanOrEqual(1);
    const body = await page.locator('body').innerText();
    expect(body).toContain('AI Natives');
    expect(body).toContain('Enterprises & Govs');
  });
});
