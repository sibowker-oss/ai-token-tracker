# wq-033 — HA references + design system alignment

**Status:** **SHIPPED 2026-04-29** — Phases 0b–5 complete on `apac-ai-intel/main`. Final commits: 02c19c8 (P1), 4288da8 (P2), b82da8e (P2 cleanup), c0ce68e/e800c52/8dac011/f35ac0b (P2 footer iteration), ced9ca8 (P3), 0fc6e70 (P4), Phase 5 audit at [audits/2026-04-29-numbers-reconciliation.md](../../audits/2026-04-29-numbers-reconciliation.md). Two launch-blocking findings (F1 Revenue, F2 Anthropic methodology lock) routed to cross-project decision per the Phase 5 audit. Frozen 2026-04-27 per GUIDELINES §9.3.
**Working name:** HA design alignment + cross-link parity
**Placement:** Cross-cutting — affects every public Ledger page (header, footer, type, colour, tier badges) and `/methodology` specifically.
**Date drafted:** 2026-04-27
**Owner candidate:** Claude Code
**Target:** V2 launch parallel with HA site, this week.
**Related items:** wq-005 (Claims Ledger graduation — uses same design tokens), wq-016 (dataReferences cleanup — must include the 5 HA-advertised numbers), wq-034 (subscription integration), wq-035 (cross-launch contract).

---

## 1. Working name, placement, status

HA design alignment + cross-link parity. Touches every public Ledger page.

## 2. Purpose (one paragraph, single question)

When a visitor crosses from the new HA site to the AI Ledger and back, do the two surfaces feel like one practice with two products, or like two unrelated sites? Today they don't share fonts, category colours, tier badges, or footer attribution. The HA site already links 7+ times to the Ledger from its homepage alone. The Ledger needs to (a) accept that referral traffic gracefully, (b) reciprocate the linking, and (c) carry visible Hepburn Advisory attribution per GUIDELINES §8. This brief codifies the alignment.

## 3. Editorial positioning

The brand presence rules are already set in GUIDELINES §8: "The brand is present via credibility, not copy." Header/footer wordmark + link, per-page byline under methodology, advisory CTAs in one location below primary content. This brief implements §8, it does not redefine it.

Key implication: aligning visual tokens with HA does NOT mean importing HA's commercial messaging onto Ledger pages. The Ledger stays numbers-first; HA's voice stays on hepburnadvisory.com.au. Visual coherence, editorial separation.

## 4. Core deliverables

### 4.1 Domain confirmation

Confirm `ai-index.hepburnadvisory.com.au` is live and serves the current Ledger build. If not yet deployed, that's a blocker for everything else and goes in front of this brief. Per Simon 2026-04-27 — domain migration happens AT LAUNCH, not now. Implementation work below assumes that scheduling.

### 4.2 Design tokens — adopt the canonical HA design system

**SOURCE OF TRUTH:** `Claude Design - Design System/Hepburn Advisory Design System/colors_and_type.css` plus the rest of that folder. This is the canonical token set for both surfaces. Do NOT reverse-engineer from the deployed Astro CSS for the contract version — read this file directly.

**Two surfaces, one palette:**

| Surface | Where | Theme |
|---|---|---|
| Hepburn Advisory | `hepburnadvisory.com.au` | **Light** — `--bg-light: #FBFBF9` page, `--surface-light: #FFFFFF` cards, `--border-light: #E7E5DC` |
| AI Ledger | `ai-index.hepburnadvisory.com.au` | **Dark** — `--bg-dark: #0A0E1A` page, `--surface-dark: #111827` cards, `--border-dark: #1E293B` |

Apply via `body.surface-light` or `body.surface-dark`. The Ledger is dark; the HA homepage is light. They share fonts, palette, type scale, motion, and component patterns. They differ in surface and voice.

**Typography** (per design system §3 — fonts already self-hosted in `Claude Design - Design System/Hepburn Advisory Design System/fonts/`)
- `--font-sans: "Inter", …` — UI, body, headlines.
- `--font-serif: "Source Serif 4", …` — long-form editorial only (Insights, About, print). Never UI.
- `--font-mono: "JetBrains Mono", …` — methodology, provenance meta, code.
- Tabular numerals required on every number: `font-variant-numeric: tabular-nums`.

**Category colours (semantic, fixed)**
- `--capital: #3B82F6` blue → primary, links, Capital Ledger
- `--revenue: #10B981` green → Revenue Ledger, positive, tier-1 styling
- `--usage: #8B5CF6` violet → Usage Ledger, tier-3 styling
- `--power: #F59E0B` amber → Power Ledger, emphasis, tier-2 styling
- `--cyan: #06B6D4` → tertiary series only
- `--red: #EF4444` → reality-check, sparingly

Don't introduce new hues. Don't reuse blue for non-capital data. See SKILL.md hard rules.

**Tier and confidence — two axes, sometimes conflated**

The design system defines them as separate axes:
- **Tier** (provenance type): `tier-1` Sourced (green) · `tier-2` Derived (amber) · `tier-3` Modeled (violet)
- **Confidence**: High · Med · Low

`site-data.json` today carries only `confidence` (8×High, 4×Med, 0×Low across globalBenchmarks; no tier field exists). For V2 launch this means:

- **Single-axis render mapping (V1, in scope):** `confidence: "High" → .pill.tier-1` (green), `"Med" → .pill.tier-2` (amber), `"Low" → .pill.tier-3` (violet). The pill text reads "T1 High" / "T2 Med" / "T3 Low" — same as HA homepage.
- **Two-axis model (V1.1, OUT OF SCOPE for V2):** add a `tier` field (Sourced/Derived/Modeled) to `site-data.json` schema, populate, and render tier and confidence as separate visual signals. Defer.

This single-axis interpretation is the launch convention. Document it in `/methodology` so the public render is honest about what the pill encodes.

### 4.2a Reference the canonical design system, do not duplicate

- **`colors_and_type.css`** is read directly into Ledger CSS at build time (or copied wholesale, as long as the source path is documented). Don't hand-type hex codes.
- **`SKILL.md`** in the design-system folder is structured as a Claude Code skill. Install it at `apac-ai-intel/.claude/skills/hepburn-design/SKILL.md` so any subsequent design work in that repo auto-loads the rules. Symlink or copy.
- **`ui_kits/ledger/index.html`** is the canonical visual reference for the Ledger surface — nav, hero, four-tile row, Sankey, claims card, filter bar, table, methodology strip. Implementation should match this kit's grammar; Claude Code copies patterns from it rather than inventing.
- **`assets/logo-icon.svg`** + `logo-icon-inverse.svg` are the canonical brand mark. Copy into the Ledger's static assets — don't link by absolute path.

### 4.2b Hard rules from SKILL.md (binding for V2 work)

These come from the design system, not this brief — listed here for visibility:

- Never write the word **"Fractional"** anywhere. Hard veto.
- Never imply Hepburn is more than one person. Singular practice.
- No emoji anywhere. The sparkle mark is a logo, not an emoji.
- Sentence case for headlines, buttons, slide titles, nav. UPPERCASE only for eyebrows.
- Tabular numerals on every number.
- No gradient backgrounds. Gradients only on (a) the Ledger wordmark clip-text, (b) Sankey/flow diagrams.
- Every number carries tier + confidence. If data doesn't support it, don't put a number on the page.
- ARR vs booked revenue always labelled — never interchangeable.

**Component patterns** (port shape, not necessarily 1:1 markup)
- `.tile` — bordered card, 22px×24px padding, hover lifts 2px, category-coloured kicker.
- `.fresh-dot` / `.fresh` — recency indicator. Green if updated <30d, amber 30-90d, grey >90d.
- `.pill` and `.pill-mini` — tier or category badges, pill-shaped, uppercase.
- `.ticker` — top-of-page ticker for the Ledger landing page (currently HA homepage has one; the Ledger could reciprocate — V1.1).

### 4.3 Header / nav reciprocity

HA's top nav has `"The AI Ledger ↗"` opening in a new tab. The Ledger should reciprocate with `"Hepburn Advisory ↗"` in its top nav. Per GUIDELINES §8, the wordmark + link is required on every page header anyway.

Suggested Ledger nav order: `Capital · Revenue · Usage · Power · Methodology · About · Hepburn Advisory ↗`.

Mark: same compass-rose mark as HA, "AI Ledger" wordmark. Reads as "two products of one practice."

### 4.4 Footer alignment

Match HA footer structure conceptually (not pixel-for-pixel — Ledger is data-first dark theme, HA is advisory-first light theme):

- Logo + "Hepburn Advisory · Independent advisory · Melbourne · working globally" desc.
- Columns: Ledger pages · Methodology + provenance · Hepburn Advisory ↗ · Disclosure (privacy, conflicts).
- Base line: `© 2026 Hepburn Advisory Pty Ltd · ACN 694 313 641 · ABN 21 694 313 641 · Last updated YYYY-MM-DD · Methodology at /methodology`.

The current Ledger footer (per `index.html`) is minimal — needs a rebuild on dark surface.

### 4.5 Number reconciliation — the 5 HA-advertised numbers

HA homepage advertises these as Ledger numbers:

| Number | HA value | Ledger source |
|---|---|---|
| Capital committed | $745B | `site-data.json` → ? |
| Revenue booked | $22B | `site-data.json` → `sankey.totalCustomerRevenue`? |
| Ratio capital:revenue | 33.7:1 (≈$34:$1) | derived |
| Usage | ~650T tok/day | `site-data.json` → ? |
| Power contracted | 92 GW | `site-data.json` → ? |

Action: trace each value in `site-data.json` and confirm they're (a) present, (b) labelled, (c) sourced. If any of these are absent or different, decide whether to update HA or update the Ledger — but the two MUST match before launch. Any divergence is a public credibility hit.

This overlaps with **wq-016** (dataReferences cleanup). Specifically, the $34T literal flagged in follow-the-trillion.html and any other large-number literals on `index.html` / `methodology.html` should be in scope of wq-016 cleanup before V2 launch.

### 4.6 /methodology page polish

HA homepage links directly to `/methodology` from the footer base line. This is the *single most-linked* deep page on the Ledger from HA. Must be:

- Compliant with GUIDELINES §2.4 methodology caveat template.
- All numbers cited trace to `site-data.json` (no hardcoded large-number literals).
- Tier convention explained — "T1 High, T2 Med, T3 Low" wording matches HA.
- "Prepared by Hepburn Advisory" byline at the bottom per §8.

### 4.7 UTM convention

Cross-traffic measurement. Two directions:

- **HA → Ledger:** every link from HA appends `?utm_source=hepburn&utm_medium=site&utm_campaign=v2-launch&utm_content=<slot>` where `<slot>` is `nav | hero | ledger-strip | live-numbers | footer`. HA is owner of this — needs to be added on the HA build.
- **Ledger → HA:** every link from Ledger appends `?utm_source=ledger&utm_medium=site&utm_campaign=v2-launch&utm_content=<slot>` where `<slot>` is `header-cta | footer-attribution | byline | sub-cta`.

Documented in `briefs/active/2026-04-27-cross-launch-spec.md` (wq-035) §4.4.

### 4.8 Per-page byline

Standard byline component, drops in below the methodology block on every public Ledger page:

```html
<aside class="byline">
  <span>Prepared by</span>
  <a href="https://hepburnadvisory.com.au/?utm_source=ledger&utm_medium=site&utm_campaign=v2-launch&utm_content=byline">Hepburn Advisory</a>
  <span class="meta">Independent advisory · Melbourne · grounded in Ledger data</span>
</aside>
```

## 5. Data audit

What exists:
- GUIDELINES §8 specifies what brand presence should look like (not yet implemented across all pages).
- `site-data.json` has provenance fields per §4.2.
- HA design system staged at `Claude Design - Design System/Hepburn Advisory Design System/`.

What needs collecting:
- Confirmation each of the 5 HA-advertised numbers is present and matches in `site-data.json`.
- Confirmation `ai-index.hepburnadvisory.com.au` is live (Phase 0a).

## 6. Schema extension

None — this is a CSS / HTML / cross-link change. No `site-data.json` schema changes.

## 7. Visualisation plan

V1 (must-have for launch):
- Design tokens adopted from canonical source.
- body.surface-dark applied to all live Ledger pages.
- Header nav with HA reciprocal link.
- Footer rebuilt to match §4.4 on dark surface.
- 5 HA-advertised numbers confirmed identical.
- Per-page byline applied to all public pages.
- UTM scheme on all cross-links.
- /methodology page polish complete.

V1.1 (post-launch):
- Ticker on Ledger landing (mirroring HA homepage ticker).
- "Fresh dot" recency indicators on every datapoint cell.
- Confidence-field migration to two-axis tier+confidence per design system.

V2 (later):
- Ledger landing rebuilt to use HA component patterns (tile / kicker / lede / answer).

## 8. Source tracking & agent log requirements

No new sources or agents. This is presentation-layer.

## 9. Implementation phases (post-decisions, day estimates)

- **Phase 0a — domain deployment.** Provision `ai-index.hepburnadvisory.com.au`, deploy current Ledger build, verify all links. ~0.5 day. **PRECURSOR BLOCKER. OWNER=SIMON.**
- **Phase 0b — design system reference.** Read SKILL.md, README.md, colors_and_type.css from the staged folder. Install SKILL.md as `.claude/skills/hepburn-design/`. Asynchronous; can run in parallel with Phase 0a.
- **Phase 1 — tokens, type, tier mapping.** Per §4.2 + §4.2a. ~1 day.
- **Phase 2 — nav, footer, byline.** Per §4.3, §4.4, §4.8. ~1 day.
- **Phase 3 — methodology polish.** Per §4.6. ~0.5 day.
- **Phase 4 — UTM scheme.** Per §4.7. ~0.5 day.
- **Phase 5 — number reconciliation.** Per §4.5. ~0.5-1 day.

Total ~4-4.5 days excluding Phase 0a (which is owner=Simon DNS work). Realistic for a Friday-Saturday launch if Phase 0b starts today.

## 10. Decisions log (closed at handoff time)

- **Domain migration:** in scope. Migrates ai-index.hepburnadvisory.com.au at launch.
- **Token source:** canonical HA design-token folder added by Simon to `Claude Design - Design System/`.
- **Theme:** Ledger is dark surface (body.surface-dark).
- **Tier mapping (V2):** single-axis. confidence:High→tier-1, Med→tier-2, Low→tier-3.
- **Two-axis model:** V1.1, deferred.
- **Mark:** same compass-rose mark as HA, different wordmark.
- **Ticker:** V1.1, not V1.
- **Cross-launch coordination doc:** wq-035, drafted.

## 11. Change-log

| Date | Change | Reason |
|---|---|---|
| 2026-04-27 | Created. Frozen. | Drafted in Cowork session per V2-launch planning. |
| 2026-04-27 | Copied to apac-ai-intel/briefs/active/. | Cowork session staged the contract per GUIDELINES §9.3. |
| 2026-04-28 | Phase 0b shipped. | Design system folder copied to `/design-system/`; SKILL.md installed at `.claude/skills/hepburn-design/`. Asset inventory + SVG-naming inversion flagged for post-launch cleanup. |
| 2026-04-28 | Phase 1 shipped (commit 02c19c8). | Adopted `colors_and_type.css` tokens; `body.surface-dark` applied to all 11 live pages; `.pill.tier-1/2/3` production rules in `ledger-overlays.css`. EXCLUDED_DIRS validator fix bundled. |
| 2026-04-28 | Phase 2 shipped (commit 4288da8). | Shared `.ds-header` + `.byline` + `.ds-footer` partials applied to all 11 live pages with active-state per page. UTM scheme on header-cta / byline / footer-attribution slots. |
| 2026-04-28 | Phase 2 cleanup (commit b82da8e). | Stripped legacy `<nav class="nav-bar">` + `<footer>` blocks from all 11 pages. Functional scenario toggle preserved as `.ds-toolbar` sub-bar on the 7 pages with `setScenario()` JS. −355 lines net. |
| 2026-04-28 | Phase 2 footer-brand polish (commits c0ce68e → e800c52 → 8dac011 → f35ac0b). | Brand block reflowed from grid to flex+lockup wrapper; logo/name lockup gap tightened. |
| 2026-04-29 | Phase 3 shipped (commit ced9ca8). | /methodology page: GUIDELINES §2.4 collapsible caveat added; new "How confidence is rendered (V2)" section documents single-axis pill mapping; tier legend wording updated to "T1 High / T2 Med / T3 Low"; hardcoded large-number literals removed from per-Ledger cards (resolves the build-lint methodology.html dataReferences warning). |
| 2026-04-29 | Phase 4 shipped (commit 0fc6e70). | UTM sweep complete — 34 tagged Ledger→HA links across 11 pages, 0 untagged. Added `about-contact` slot to wq-035 §4.4 enum (recorded in cross-launch-spec §10). |
| 2026-04-29 | Phase 5 shipped — 5-numbers audit produced. | See [audits/2026-04-29-numbers-reconciliation.md](../../audits/2026-04-29-numbers-reconciliation.md). Findings F3–F6 routed to follow-up tickets (wq-016, wq-012). **Findings F1 (Revenue $4.53B gap) and F2 (Anthropic methodology-lock breach) are launch-blocking** and require cross-project decision before V2 ships. wq-033 implementation complete; resolution of F1+F2 is out of brief scope. |

## 12. Last-updated

2026-04-29 — Phases 0b–5 shipped to main; Phase 5 audit reports two launch-blocking findings awaiting cross-project decision.
