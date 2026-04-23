// tests/release-check/links.spec.ts
// Enforces GUIDELINES.md §11.4 link resolution.
// Validates every sourceUrl in site-data.json (and internal nav links) with HEAD → GET fallback.
// Skip with RELEASE_CHECK_LINKS=offline.

import { test, expect, request } from '@playwright/test';
import { loadSiteData, allDatapoints, pages } from './helpers';

const data = loadSiteData();
const offline = process.env.RELEASE_CHECK_LINKS === 'offline';

// Realistic UA — many source sites (IMF, SEC, S&P, Gartner, McKinsey, ILO) return 403 to
// default Playwright fetch. A browser-like UA clears most; for the ones that still
// bot-block, 401/403/429 are treated as "URL resolves, access-controlled" (the page exists,
// headless browser is just refused). Hard 404 or connection failure still fails.
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';
const ACCESS_CONTROLLED = new Set([401, 403, 429]);

test.beforeEach(({}, testInfo) => {
  test.skip(offline, 'RELEASE_CHECK_LINKS=offline');
  test.skip(testInfo.project.name !== 'desktop-chrome', 'link checker runs once, on desktop-chrome');
});

const urls = new Set<string>();
for (const { dp } of allDatapoints(data)) {
  if (dp.sourceUrl) urls.add(dp.sourceUrl);
  if ((dp as any).sources) {
    for (const s of (dp as any).sources) if (s.sourceUrl) urls.add(s.sourceUrl);
  }
}

test.describe('source URL checker (§11.4)', () => {
  for (const url of urls) {
    test(`resolves: ${url}`, async () => {
      const api = await request.newContext({ extraHTTPHeaders: { 'User-Agent': UA } });
      let res = await api.fetch(url, { method: 'HEAD', timeout: 15_000, failOnStatusCode: false }).catch(() => null);
      if (!res || res.status() === 405 || res.status() >= 400) {
        res = await api.fetch(url, { method: 'GET', timeout: 20_000, failOnStatusCode: false });
      }
      const status = res.status();
      const ok = status < 400 || ACCESS_CONTROLLED.has(status);
      expect(ok, `${url} returned ${status}${ACCESS_CONTROLLED.has(status) ? '' : ' (hard failure)'}`).toBeTruthy();
    });
  }
});

test.describe('internal nav links', () => {
  for (const p of pages(data)) {
    test(`${p.key} — no dead internal links`, async ({ page }) => {
      await page.goto(p.path, { waitUntil: 'networkidle' });
      const hrefs = await page.evaluate(() => {
        return [...document.querySelectorAll<HTMLAnchorElement>('a[href^="/"], a[href^="./"], a[href^="#"]')]
          .map(a => a.getAttribute('href')!)
          .filter(h => h && !h.startsWith('#'));
      });
      for (const href of hrefs) {
        const res = await page.context().request.fetch(new URL(href, page.url()).toString(), { method: 'HEAD', failOnStatusCode: false });
        expect(res.status(), `${href} returned ${res.status()}`).toBeLessThan(400);
      }
    });
  }
});
