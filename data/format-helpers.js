// wq-076 — site-wide currency formatting helper.
// Pages include via <script src="data/format-helpers.js"></script>.
// Engine values stay full-precision; rounding is render-only.
//
// Magnitude-aware rounding rule (Simon-confirmed 2026-05-03):
//   ≥$10B   → "$176B" (nearest integer)
//   $1–10B  → "$4.7B" (one decimal)
//   <$1B    → "$800M" (millions, nearest integer)
//   null/NaN → "—"
//   0       → "$0"
//
// Test cases (assert in formatHelpersTests below for unit verification):
//   176.48 → "$176B"
//   132.46 → "$132B"
//   9.31   → "$9.3B"
//   4.71   → "$4.7B"
//   2.25   → "$2.3B"
//   0.80   → "$800M"
//   0.05   → "$50M"
//   0      → "$0"
//   null   → "—"
//
// Negatives: minus sign + abs (e.g. −$5B). Per brief §4.4.

(function (root) {
  function formatCurrency(value) {
    if (value == null || Number.isNaN(value)) return '—';
    if (value === 0) return '$0';
    const abs = Math.abs(value);
    const sign = value < 0 ? '−' : '';
    if (abs >= 10) return `${sign}$${Math.round(abs)}B`;
    if (abs >= 1)  return `${sign}$${abs.toFixed(1)}B`;
    return `${sign}$${Math.round(abs * 1000)}M`;
  }

  // Self-test in dev — only runs when explicitly invoked, not on every page load.
  function formatHelpersTests() {
    const cases = [
      [176.48, '$176B'], [132.46, '$132B'], [9.31, '$9.3B'], [4.71, '$4.7B'],
      [2.25, '$2.3B'],  [0.80, '$800M'],   [0.05, '$50M'],  [0, '$0'],
      [null, '—'],       [NaN, '—'],
      [-5, '−$5.0B'],    [-176.48, '−$176B'],
    ];
    const fails = [];
    for (const [input, expected] of cases) {
      const actual = formatCurrency(input);
      if (actual !== expected) fails.push({ input, expected, actual });
    }
    return { passed: cases.length - fails.length, total: cases.length, fails };
  }

  root.formatCurrency = formatCurrency;
  root.formatHelpersTests = formatHelpersTests;
})(typeof window !== 'undefined' ? window : globalThis);
