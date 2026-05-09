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

  // wq-077 — narrative copy hydration. Resolves `[data-narrative="key"]` spans
  // against site-data.json values + formats with formatCurrency. Falls back to
  // inline default text when the path is missing (graceful degradation).
  //
  // Path keys map to dotted accessors on site-data; supports a small set of
  // common derivation patterns (cumulative.X, market.<year>.X, sankey.X,
  // capital_sankey.X). Add new keys here as narrative wiring expands.
  function resolveNarrativeValue(key, siteData) {
    if (!siteData || !key) return null;
    const PATHS = {
      // cumulative aggregator (wq-063)
      'cumulative_capex_total':           siteData.cumulative?.capex_total,
      'cumulative_customer_revenue_gross':siteData.cumulative?.customer_revenue_gross,
      'cumulative_customer_revenue_net':  siteData.cumulative?.customer_revenue_net,
      // sankey gross/net (wq-055/062/063)
      'sankey_total_customer_revenue_gross': siteData.sankey?.totalCustomerRevenue_gross,
      'sankey_total_customer_revenue_net':   siteData.sankey?.totalCustomerRevenue,
      'sankey_total_vc_subsidy':             siteData.sankey?.totalVCSubsidy,
      // market aggregates per year (wq-067)
      'market_2025_total_capex':          siteData.market?.['2025']?.total_capex,
      'market_2025_total_customer_revenue':siteData.market?.['2025']?.total_customer_revenue,
      'market_2025_total_customer_revenue_gross':siteData.market?.['2025']?.total_customer_revenue_gross,
      // capital sankey (wq-074)
      'capital_sankey_total':             siteData.capital_sankey?.total,
    };
    return PATHS[key] != null ? PATHS[key] : null;
  }

  function hydrateNarrative(siteData, formatter) {
    formatter = formatter || formatCurrency;
    const spans = (typeof document !== 'undefined') ? document.querySelectorAll('[data-narrative]') : [];
    let hydrated = 0;
    spans.forEach(span => {
      const key = span.dataset.narrative;
      const value = resolveNarrativeValue(key, siteData);
      if (value != null) {
        span.textContent = formatter(value);
        hydrated++;
      }
      // else: keep inline default text (graceful fallback)
    });
    return hydrated;
  }

  root.formatCurrency = formatCurrency;
  root.formatHelpersTests = formatHelpersTests;
  root.resolveNarrativeValue = resolveNarrativeValue;
  root.hydrateNarrative = hydrateNarrative;
})(typeof window !== 'undefined' ? window : globalThis);
