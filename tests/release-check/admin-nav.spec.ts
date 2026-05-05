// tests/release-check/admin-nav.spec.ts
// wq-088 — admin nav refactor. Validates the *rendered* DOM (per the
// validate-rendered-output rule from feedback memory), not just the source
// files. Each admin URL must:
//   1. Load (200) after the password gate is bypassed via localStorage.
//   2. Inject the ds-header (mirrors index.html), brand href = "/index.html".
//   3. Inject the secondary nav with all 14 expected data-tab values.
//   4. Mark its own tab as is-active.
// Plus suite-level assertions:
//   - admin.html redirects to /review.html (or to /<tab>.html for known hashes).
//   - The inbox pending-pill appears when vault-inbox.json has items.
//   - No public page links to /in-development.html (D6).
//
// Runs on desktop-chrome only — this is a structural assertion suite, not a
// cross-browser smoke; the visual diff is covered separately by visual.spec.ts.

import { test, expect, type Page } from '@playwright/test';

test.describe.configure({ mode: 'parallel' });

const ADMIN_PAGES: Array<{ tab: string; path: string; title: string }> = [
  { tab: 'review',     path: '/review.html',              title: 'Daily Review' },
  { tab: 'claims',     path: '/claims.html',              title: 'Claim Review Queue' },
  { tab: 'add',        path: '/add.html',                 title: 'Add' },
  { tab: 'ask',        path: '/ask.html',                 title: 'Ask the Vault' },
  { tab: 'sources',    path: '/sources.html',             title: 'Source Ledger' },
  { tab: 'confidence', path: '/confidence.html',          title: 'Data Confidence' },
  { tab: 'vault',      path: '/vault.html',               title: 'Intel Vault' },
  { tab: 'anthropic',  path: '/anthropic-spotlight.html', title: 'Anthropic monthly review' },
  { tab: 'status',     path: '/status.html',              title: 'Run log' },
  { tab: 'telemetry',  path: '/telemetry.html',           title: 'Operational telemetry' },
  { tab: 'agents',     path: '/agents.html',              title: 'Agents' },
  { tab: 'briefs',     path: '/briefs.html',              title: 'Briefs' },
  { tab: 'dev',        path: '/in-development.html',      title: 'In Development' },
  { tab: 'archive',    path: '/archive.html',             title: 'Page Archive' },
  { tab: 'settings',   path: '/settings.html',            title: 'Settings' },
];

const EXPECTED_TABS = ADMIN_PAGES.map(p => p.tab).sort();

// Public pages that the brief D6 demands stay free of /in-development.html.
const D6_PUBLIC_PAGES = [
  '/index.html', '/capital.html', '/revenue.html', '/usage.html', '/power.html',
  '/methodology.html', '/about.html', '/timeline.html', '/openrouter.html',
  '/changelog.html', '/compute.html',
];

async function bypassAuth(page: Page) {
  // The per-page password-gate IIFE early-returns if localStorage[…auth…] === 'ok'.
  // addInitScript runs before any page script, so we set the key before the IIFE fires.
  await page.addInitScript(() => {
    try { localStorage.setItem('ai-ledger-admin-auth', 'ok'); } catch (_) {}
  });
}

test.describe('wq-088 admin nav — per-page rendered DOM', () => {
  for (const p of ADMIN_PAGES) {
    test(`${p.tab} (${p.path}) — ds-header + secondary nav render with active tab`, async ({ page }, testInfo) => {
      testInfo.skip(testInfo.project.name !== 'desktop-chrome', 'Structural spec runs on desktop-chrome only.');
      await bypassAuth(page);
      const res = await page.goto(p.path, { waitUntil: 'domcontentloaded' });
      expect(res?.status(), `${p.path} returned ${res?.status()}`).toBeLessThan(400);

      // The shared partial is fetched async — wait for the brand element.
      const brand = page.locator('#admin-nav-mount header.ds-header a.ds-header__brand').first();
      await expect(brand, `ds-header brand should render on ${p.path}`).toBeVisible({ timeout: 5000 });

      // Brand link goes direct to /index.html — verifies the dashboard.html hop is gone.
      const brandHref = await brand.getAttribute('href');
      expect(brandHref, `brand href on ${p.path}`).toBe('/index.html');

      // Primary-nav links (Capital / Revenue / Compute / Usage / Power / Methodology / About) match index.html.
      const primaryLinks = await page.locator('#admin-nav-mount nav.ds-header__nav a.ds-header__nav-link').all();
      const primaryHrefs = await Promise.all(primaryLinks.map(l => l.getAttribute('href')));
      expect(primaryHrefs, `primary nav links on ${p.path}`).toEqual([
        '/capital.html', '/revenue.html', '/compute.html', '/usage.html',
        '/power.html', '/methodology.html', '/about.html',
      ]);

      // Secondary nav exposes all 14 expected data-tab values across the four groups + Settings.
      const tabAttrs = await page.locator('#admin-nav-mount nav.admin-secondary-nav [data-tab]').evaluateAll(
        nodes => nodes.map(n => n.getAttribute('data-tab') ?? '')
      );
      expect(tabAttrs.sort(), `secondary nav data-tab values on ${p.path}`).toEqual(EXPECTED_TABS);

      // The current page's tab must carry is-active.
      const active = page.locator(`#admin-nav-mount [data-tab="${p.tab}"].is-active`);
      await expect(active, `expected tab "${p.tab}" active on ${p.path}`).toHaveCount(1);

      // No legacy iframe-per-tab structure on this admin URL. The brief AC targeted
      // the admin.html shell pattern; in-development.html and archive.html both use
      // iframes to embed *content* preview thumbnails (parked/* prototypes for dev,
      // archived page previews for archive) — those are page features, not the nav
      // wrapper wq-088 is killing.
      const PAGES_WITH_CONTENT_IFRAMES = new Set(['dev', 'archive']);
      if (!PAGES_WITH_CONTENT_IFRAMES.has(p.tab)) {
        const iframeCount = await page.locator('iframe').count();
        expect(iframeCount, `no iframes expected on ${p.path}`).toBe(0);
      }
    });
  }
});

test.describe('wq-088 admin redirect + edge behaviour', () => {
  test('admin.html redirects to /review.html (no hash)', async ({ page }, testInfo) => {
    testInfo.skip(testInfo.project.name !== 'desktop-chrome', 'desktop-chrome only.');
    await bypassAuth(page);
    await page.goto('/admin.html', { waitUntil: 'domcontentloaded' });
    await page.waitForURL('**/review.html', { timeout: 5000 });
    expect(new URL(page.url()).pathname).toBe('/review.html');
  });

  test('admin.html source contains no iframe (the iframe-per-tab pattern is gone)', async ({ request }) => {
    // Asserts the wq-088 AC9 target: the legacy admin.html iframe-per-tab shell.
    // Fetch the raw HTML directly so the redirect doesn't navigate us away.
    const res = await request.get('/admin.html');
    expect(res.status()).toBeLessThan(400);
    const html = await res.text();
    expect(html.toLowerCase()).not.toContain('<iframe');
  });

  test('admin.html#telemetry redirects to /telemetry.html', async ({ page }, testInfo) => {
    testInfo.skip(testInfo.project.name !== 'desktop-chrome', 'desktop-chrome only.');
    await bypassAuth(page);
    await page.goto('/admin.html#telemetry', { waitUntil: 'domcontentloaded' });
    await page.waitForURL('**/telemetry.html', { timeout: 5000 });
    expect(new URL(page.url()).pathname).toBe('/telemetry.html');
  });

  test('inbox pending-pill reflects vault-inbox.json item count', async ({ page }, testInfo) => {
    testInfo.skip(testInfo.project.name !== 'desktop-chrome', 'desktop-chrome only.');
    await bypassAuth(page);
    await page.goto('/review.html', { waitUntil: 'domcontentloaded' });
    await page.locator('#admin-nav-mount header.ds-header').first().waitFor({ state: 'visible', timeout: 5000 });

    const inbox: any = await (await page.request.get('/vault-inbox.json')).json();
    const expected = (inbox.items ?? []).filter((i: any) => i && i.status === 'pending').length;

    const pill = page.locator('#admin-nav-mount [data-tab="review"] [data-role="pending-pill"]');
    if (expected === 0) {
      await expect(pill).toBeHidden();
    } else {
      await expect(pill).toBeVisible({ timeout: 5000 });
      await expect(pill).toHaveText(String(expected));
    }
  });

  test('every secondary-nav link returns < 400 status', async ({ page }, testInfo) => {
    testInfo.skip(testInfo.project.name !== 'desktop-chrome', 'desktop-chrome only.');
    await bypassAuth(page);
    await page.goto('/review.html', { waitUntil: 'domcontentloaded' });
    await page.locator('#admin-nav-mount nav.admin-secondary-nav').waitFor({ timeout: 5000 });

    const hrefs = await page.locator('#admin-nav-mount nav.admin-secondary-nav a[data-tab]').evaluateAll(
      nodes => nodes.map(n => (n as HTMLAnchorElement).getAttribute('href') ?? '')
    );
    expect(hrefs.length).toBe(EXPECTED_TABS.length);

    for (const href of hrefs) {
      const res = await page.request.get(href);
      expect(res.status(), `${href} should resolve`).toBeLessThan(400);
    }
  });
});

test.describe('wq-088 D6 — public pages must not link to /in-development.html', () => {
  for (const path of D6_PUBLIC_PAGES) {
    test(`${path} contains no /in-development.html anchor`, async ({ page }, testInfo) => {
      testInfo.skip(testInfo.project.name !== 'desktop-chrome', 'desktop-chrome only.');
      const res = await page.goto(path, { waitUntil: 'domcontentloaded' });
      expect(res?.status(), `${path} loaded`).toBeLessThan(400);
      const links = await page.locator('a[href$="/in-development.html"], a[href$="in-development.html"]').count();
      expect(links, `${path} should have no /in-development.html links (D6)`).toBe(0);
    });
  }
});
