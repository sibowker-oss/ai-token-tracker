# wq-035 — Cross-launch coordination spec (HA + AI Ledger)

**Status:** **FROZEN 2026-04-27** — copied here from `The AI Ledger/briefings/wq-035-cross-launch-spec.md` per GUIDELINES §9.3. This is the immutable contract version. Material edits add a change-log row at §10.
**Working name:** Cross-launch spec (HA ↔ Ledger)
**Date drafted:** 2026-04-27
**Owner:** Simon (cross-project) with Claude Code as implementer on each side.
**Target:** V2 launch Sunday 2026-05-03 (per §5 launch sequence T-0).
**Related items:** wq-033 (HA design alignment, Ledger side), wq-034 (subscription integration).

---

## 1. Working name, placement, status

Cross-launch coordination doc. The single canonical reference for what links where, what UTM each side uses, what numbers must match, and what the launch sequence is.

## 2. Purpose (one paragraph, single question)

Two parallel cowork projects (HA new site + AI Ledger V2) launching together this week. Without a shared spec, the two will drift — HA links to a Ledger URL that doesn't exist, the Ledger references HA copy that's been changed, the 5 advertised numbers diverge between sites. This spec is the contract between the two sides so each Claude Code session can implement against a stable target.

## 3. Editorial positioning

This document is operational, not editorial. No voice rules. Lives alongside GUIDELINES.md but does not replace it.

## 4. The contract

### 4.1 Domain map

| Surface | Domain | Status as of 2026-04-27 |
|---|---|---|
| HA production | `hepburnadvisory.com.au` | Live (or going live at launch — Simon to confirm) |
| HA preview | `ae09def0-hepburn-advisory-site.sibowker.workers.dev` | Live |
| Ledger production | `ai-index.hepburnadvisory.com.au` | Domain reserved per GUIDELINES §1; deployment goes live AT LAUNCH (per Simon). |
| Ledger legacy | `sibowker-oss.github.io/ai-token-tracker/dashboard.html` | Live today; sunset at launch (with redirect TBD). |

### 4.2 URL contract — what HA links to on the Ledger

These URLs MUST exist and respond 200 at launch. If any get renamed during implementation, both sides update together via a change-log entry at the bottom of this doc.

| HA → Ledger destination | Notes |
|---|---|
| `ai-index.hepburnadvisory.com.au/` | Ledger home. Top nav, hero CTA, footer "Research" column. |
| `ai-index.hepburnadvisory.com.au/methodology` | Footer base line. Critical deep link. |
| `ai-index.hepburnadvisory.com.au/capital` | (referenced via "Open in Ledger" cards if scoped) |
| `ai-index.hepburnadvisory.com.au/revenue` | (referenced via "Open in Ledger" cards if scoped) |
| `ai-index.hepburnadvisory.com.au/usage` | (referenced via "Open in Ledger" cards if scoped) |
| `ai-index.hepburnadvisory.com.au/power` | (referenced via "Open in Ledger" cards if scoped) |

Note: HA homepage `Live Numbers` section currently uses three `Open in Ledger →` links pointing at the home page. **DECIDED 2026-04-27: deep-link** — each card links to its corresponding `/capital`, `/revenue`, or `/power` page. HA-side responsibility (see §6).

### 4.3 URL contract — what the Ledger links to on HA

| Ledger → HA destination | Slot |
|---|---|
| `hepburnadvisory.com.au/` | Header CTA (`Hepburn Advisory ↗`) |
| `hepburnadvisory.com.au/contact/?subscribe=ledger&...` | Subscribe CTA on Ledger home |
| `hepburnadvisory.com.au/contact/` | Footer contact link |
| `hepburnadvisory.com.au/about` | (optional) Byline destination |

### 4.4 UTM scheme

**HA → Ledger:**
```
?utm_source=hepburn&utm_medium=site&utm_campaign=v2-launch&utm_content=<slot>
```
Where `<slot>` ∈ `nav | hero | ledger-strip | live-numbers | footer | thought-leadership-link`.

**Ledger → HA:**
```
?utm_source=ledger&utm_medium=site&utm_campaign=v2-launch&utm_content=<slot>
```
Where `<slot>` ∈ `header-cta | byline | footer-attribution | sub-cta | methodology-mention | about-contact`.

**Subscription pre-fill (one extra param on top of UTM):**
```
hepburnadvisory.com.au/contact/?subscribe=ledger&utm_source=ledger&utm_medium=site&utm_campaign=v2-launch&utm_content=sub-cta
```
HA `/contact/` form pre-checks the "Subscribe to news + AI Ledger updates" checkbox when `subscribe=ledger` is present.

### 4.5 Numbers contract

The 5 numbers HA advertises on its homepage MUST match what the Ledger publishes in `site-data.json`. As of HA's current build:

| Metric | HA value | Ledger source field (per GUIDELINES §5.3.1) |
|---|---|---|
| Capital committed | $745B | TBD — confirm in Phase 5 of wq-033 |
| Revenue booked | $22B | `sankey.totalCustomerRevenue` (Phase 5 to verify field path) |
| Ratio capital:revenue | 33.7:1 (≈$34:$1) | derived |
| Usage | ~650T tok/day | TBD |
| Power contracted | 92 GW | TBD |

**Methodology lock — DECIDED 2026-04-27:** "Revenue booked" uses **Ledger collected-revenue methodology**, NOT exit-ARR or run-rated revenue. Specifically: Anthropic figure uses the court-derived collected revenue (~$4.5B), not Dario's stated ~$9-10B (which is likely exit-ARR). This is binding on both sides. Per SKILL.md hard rule #6: ARR and booked revenue are never interchangeable. If HA's current $22B aggregate bakes in any exit-ARR component, HA fixes its number to align with Ledger's collected aggregate. Phase 5 of wq-033 verifies the cross-Ledger aggregate produces a value within ±$2B of HA's $22B; if not, HA updates to match.

If a number divergence is found during the Phase 5 audit:
- If HA value is wrong → fix HA build.
- If Ledger value is wrong → fix `site-data.json` + provenance update.
- If both are right but use different methodologies → reconcile language and pick one canonical.

### 4.6 Confidence-tier rendering (single-axis V2, two-axis V1.1)

Both sites render the same string values from `site-data.json`. For V2 launch (single-axis):

| `confidence` value | Pill rendered as | Colour |
|---|---|---|
| `"High"` | T1 High | green (`--green`) |
| `"Med"` | T2 Med | amber (`--amber`) |
| `"Low"` | T3 Low | violet (`--violet`) |

CSS class names: `pill tier-1`, `pill tier-2`, `pill tier-3`. Implementation per HA design system.

The two-axis model in SKILL.md (tier = Sourced/Derived/Modeled, separate from confidence) is V1.1 work.

### 4.7 Freshness expectations

HA homepage shows "Ledger updated 24 Apr 2026" (the "fresh-dot" element). This pulls from a single source of truth — Ledger `site-data.json` `meta.generatedAt` (or equivalent). HA build either:

- (a) reads `site-data.json` at build time and hardcodes the date, OR
- (b) fetches `site-data.json` at runtime via fetch/CDN with a daily cache.

**DECIDED 2026-04-27: option (a) build-time.** HA reads `site-data.json` at build, hardcodes the date in the rendered HTML. Runtime fetch deferred to V1.1 if/when HA's build cadence diverges from Ledger's.

If Ledger goes >7 days without an update, HA's "fresh-dot" should turn amber. >30 days → grey. CSS classes `.fresh`, `.fresh.amber`, `.fresh.grey` exist on HA.

## 5. Launch sequence

Order of operations for going live. **Do not deviate** without recording in §10.

```
T-7  ─── 2026-04-27 ────────────────────────────────────────────
        Briefs frozen: wq-033, wq-034, wq-035
        Decisions logged
        Claude Code handoff prompts issued

T-5  ─── Wednesday 2026-04-29 ──────────────────────────────────
        Ledger Phase 0a: ai-index.hepburnadvisory.com.au DNS + deploy
        HA Phase 2: /contact/ checkbox + ?subscribe=ledger pre-fill
        Inbox cleared (wq-018) — Simon
        Bug fixes shipped: wq-029 (encoding), wq-028 (metricKey), wq-032 (downstream)

T-3  ─── Friday 2026-05-01 ─────────────────────────────────────
        Ledger Phases 1-4: tokens, nav, footer, byline, UTM applied
        Ledger Phase 5: 5-numbers audit + reconciliation
        wq-016 dataReferences cleanup — at minimum index.html, methodology.html

T-1  ─── Saturday 2026-05-02 ───────────────────────────────────
        Pre-flight: build-lint clean, all 11 live pages render, all HA links 200
        HA: final copy review
        Smoke test: each link in HA → Ledger → HA returns 200, UTMs land in analytics

T-0  ─── Sunday 2026-05-03 ─────────────────────────────────────
        HA goes live on hepburnadvisory.com.au
        Ledger goes live on ai-index.hepburnadvisory.com.au
        Old Ledger URL redirects to new domain
        Subscription migration (2 emails) — manual, post-launch
```

Adjust dates if launch slips. Lock the sequence; the sequence is the discipline.

## 6. Per-side responsibilities

### Ledger side (Simon + Claude Code in apac-ai-intel)
- Domain deployment (Phase 0a in wq-033).
- All visual + structural work in wq-033.
- Strip Formspree, add CTA in wq-034.
- All numbers in `site-data.json` reconciled to HA-advertised values.
- `/methodology` page polished per wq-033 §4.6.
- All cross-links carry the Ledger→HA UTM scheme.

### HA side (Simon + Claude Code in HA cowork project)
- `/contact/` checkbox + `?subscribe=ledger` pre-fill (wq-034 Q3).
- Confirm or update the 5 advertised numbers if Ledger reconciliation surfaces a different canonical.
- **Update Live Numbers cards to deep-link** — each of the three cards points to its corresponding `/capital`, `/revenue`, `/power` Ledger page (decided 2026-04-27).
- **Build-time read of `site-data.json`** for the freshness label (decided 2026-04-27 — see §4.7).
- **If HA's $22B aggregate bakes in any exit-ARR component (e.g. Anthropic ~$9-10B Dario figure), HA updates to use Ledger collected-revenue methodology** (decided 2026-04-27 — see §4.5).
- Each HA→Ledger link carries the HA→Ledger UTM scheme.
- Smoke-test inbound traffic from Ledger lands correctly.

### Cross
- Both sides watch this doc. If a URL changes, dependency is updated on the other side BEFORE the change ships.

## 7. Visualisation plan

Not applicable — operational doc.

## 8. Source tracking

Not applicable — no new sources.

## 9. Implementation phases

This brief itself has no implementation phases. It is a contract that wq-033 and wq-034 (and the parallel HA work) implement against.

## 10. Change-log

| Date | Edit | Reason |
|---|---|---|
| 2026-04-27 | Created. Frozen. | Initial draft from V2-launch planning conversation. |
| 2026-04-27 | Copied to apac-ai-intel/briefs/active/. | Cowork session staged the contract version per GUIDELINES §9.3. |
| 2026-04-27 | §Target line corrected to Sunday 2026-05-03. | Track A Claude Code flagged date drift between header and §5 launch sequence; Sunday is the locked T-0. |
| 2026-04-27 | §4.2 deep-link decision logged. | Simon confirmed: HA Live Numbers cards deep-link to /capital, /revenue, /power. HA-side work. |
| 2026-04-27 | §4.5 methodology lock added. | Simon decided: Revenue uses Ledger collected-revenue methodology (Anthropic ~$4.5B court-derived, NOT Dario's ~$9-10B exit-ARR). Per SKILL.md hard rule #6. HA aligns if needed. |
| 2026-04-27 | §4.7 freshness mode locked: option (a) build-time. | Simon confirmed. Runtime fetch deferred to V1.1. |
| 2026-04-27 | §6 HA responsibilities updated to reflect §4.2, §4.5, §4.7 decisions. | Cross-reference. |
| 2026-04-29 | §4.4 added `about-contact` to Ledger→HA slot enum. | Track A wq-033 Phase 4 sweep — only legacy Ledger→HA hyperlink in repo (about.html Contact section, "hepburnadvisory.com.au" anchor) didn't fit any existing slot. New slot scopes "body-copy contact-section attribution from /about" so analytics can distinguish from the global footer attribution. |

Append a row whenever:
- A URL on either side is renamed.
- A number in §4.5 changes on either side.
- The launch sequence shifts.
- A UTM slot is added or removed.

## 11. Last-updated

2026-04-27 — drafted by Claude (Cowork session); copied here for Claude Code reference.
