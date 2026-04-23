// playwright.config.ts
// Device matrix derived from GUIDELINES.md §7.5 + §11.4.
// Six projects: three desktop browsers (Chrome / Safari / Firefox) + tablet + two mobile bars.
// Advisory only: failing checks never exit non-zero at the suite level — the CLI wrapper rewrites the exit code.

import { defineConfig, devices } from '@playwright/test';

const BASE_URL = process.env.RELEASE_CHECK_BASE_URL ?? 'http://localhost:4173';

export default defineConfig({
  testDir: './tests/release-check',
  timeout: 60_000,
  expect: {
    toHaveScreenshot: {
      // §7.7 — 0.2% pixel tolerance for in-repo baselines
      threshold: 0.002,
      maxDiffPixelRatio: 0.002,
    },
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'tests/reports/html', open: 'never' }],
    ['json', { outputFile: 'tests/reports/playwright-results.json' }],
  ],
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'desktop-chrome',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
    },
    {
      name: 'desktop-safari',
      use: { ...devices['Desktop Safari'], viewport: { width: 1440, height: 900 } },
    },
    {
      name: 'desktop-firefox',
      use: { ...devices['Desktop Firefox'], viewport: { width: 1440, height: 900 } },
    },
    {
      name: 'tablet',
      use: { ...devices['iPad (gen 7)'], viewport: { width: 768, height: 1024 } },
    },
    {
      name: 'mobile-iphone',
      // iPhone 14/15 Safari per §7.5 — 390×844
      use: { ...devices['iPhone 14'], viewport: { width: 390, height: 844 } },
    },
    {
      name: 'mobile-android',
      // Android Chrome per §7.5 — 360×800
      use: { ...devices['Pixel 7'], viewport: { width: 360, height: 800 } },
    },
  ],
});
