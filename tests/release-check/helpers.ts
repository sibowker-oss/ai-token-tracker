// tests/release-check/helpers.ts
// Shared helpers for release-check Playwright specs.
// Keep thin — page-shape assumptions live in each spec so they fail loudly when the site structure changes.

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Page } from '@playwright/test';

export type Datapoint = {
  value?: number;
  label: string;
  unit: string;
  year: number;
  source: string;
  sourceUrl: string;
  retrievedAt: string;  // ISO
  nextReview: string;   // ISO
  confidence: 'High' | 'Med' | 'Low';
  note?: string;
  revenueType?: 'booked_ttm' | 'run_rate';
};

export type SiteData = {
  meta?: {
    dataReferences?: Record<string, string[]>;
    labels?: Record<string, Record<string, string>>;
  };
  pages?: Record<string, { path: string; title: string; hasDerivedNumbers?: boolean }>;
  [key: string]: any;
};

export function loadSiteData(): SiteData {
  const path = process.env.RELEASE_CHECK_DATA ?? join(process.cwd(), 'site-data.json');
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function pages(data: SiteData): Array<{ key: string; path: string; title: string; hasDerivedNumbers: boolean }> {
  const entries = Object.entries(data.pages ?? {});
  return entries.map(([key, p]) => ({
    key,
    path: p.path,
    title: p.title,
    hasDerivedNumbers: p.hasDerivedNumbers ?? true,
  }));
}

/** Walk every datapoint and yield (canonicalKey, datapoint) pairs. */
export function* allDatapoints(root: any, path: string[] = []): Generator<{ ref: string; dp: Datapoint }> {
  if (root === null || typeof root !== 'object') return;
  if (Array.isArray(root)) {
    for (let i = 0; i < root.length; i++) yield* allDatapoints(root[i], [...path, String(i)]);
    return;
  }
  if (isDatapoint(root)) {
    yield { ref: path.join('.'), dp: root as Datapoint };
    return;
  }
  for (const [k, v] of Object.entries(root)) yield* allDatapoints(v, [...path, k]);
}

function isDatapoint(node: any) {
  if (!node || typeof node !== 'object') return false;
  return ('value' in node || ('minMonths' in node && 'maxMonths' in node)) && ('source' in node || 'sources' in node);
}

/** True if the DOM contains any substring that looks like a raw internal key. */
export async function findRawKeys(page: Page, keys: string[]): Promise<string[]> {
  const text = await page.locator('body').innerText();
  return keys.filter(k => text.includes(k));
}

/** Returns the full scroll width vs client width — used for §7.5 no-horizontal-scroll rule. */
export async function hasHorizontalScroll(page: Page): Promise<boolean> {
  return page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
}

/** Returns all interactive elements smaller than the given tap-target size. */
export async function undersizedTapTargets(page: Page, minPx = 44): Promise<Array<{ selector: string; w: number; h: number }>> {
  return page.evaluate((min) => {
    const selectors = 'button, a, [role="button"], input[type="button"], input[type="submit"], input[type="checkbox"], input[type="radio"], select, [tabindex]:not([tabindex="-1"])';
    const offenders: Array<{ selector: string; w: number; h: number }> = [];
    document.querySelectorAll(selectors).forEach((el) => {
      const r = (el as HTMLElement).getBoundingClientRect();
      if (r.width > 0 && r.height > 0 && (r.width < min || r.height < min)) {
        offenders.push({
          selector: (el as HTMLElement).id || (el as HTMLElement).className || el.tagName.toLowerCase(),
          w: Math.round(r.width),
          h: Math.round(r.height),
        });
      }
    });
    return offenders;
  }, minPx);
}
