# Playbook — Vendor AI Posture quarterly review

> Source brief: [wq-101 — Vendor AI Posture Radar](../briefs/wq-101-vendor-ai-posture-radar.md)
> D5 resolved 2026-05-09: manual editorial review per earnings cycle, documented prompt + visible "last reviewed" date.
> This playbook is the prompt. Run it (yourself or by handing it to Claude in editorial mode) once per major earnings cycle for the cohort, or when a cohort vendor publishes material new disclosure that may change a score.

---

## When to run

- After each cohort earnings season closes (typically a 4–6 week window per quarter).
- Out-of-cycle if a cohort vendor:
  - Publishes a new AI ARR / share figure.
  - Changes the pricing model (introduces or retires a per-action / per-agent / outcome SKU; absorbs a premium tier into a base SKU).
  - Reports gross-margin movement explicitly attributed to AI inference.
  - Has a clear top-line growth inflection (acceleration or deceleration).

---

## What you're updating

For each of the 12 cohort entries in `site-data.json:dashboard.enterpriseReality` (filtered by presence of `postureScores`):

| Field | What to refresh |
|---|---|
| `postureScores.disclosure` | Reapply rubric §6 against current `provenance` and `arrShare.value`. |
| `postureScores.bundling` | Reapply rubric against current pricing-page state. |
| `postureScores.pricing` | Reapply rubric against the company's commercial-model posture. |
| `postureScores.cost` | Reapply rubric against latest GM commentary; `0` if private (`gmUnavailable: true`). |
| `postureScores.acceleration` | Reapply rubric against current vs prior parent top-line growth. |
| `postureScores._citations.bundling` | Update if the underlying source moved (new pricing page, new earnings transcript). |
| `postureScores._citations.cost` | Same. |
| `postureScores._lastVerified` | Bump to the current quarter — e.g., `"2026-Q2"`. |
| `postureScores._prototype` | Set to `false` once the citation has been verified against a primary source you have actually opened in this review. |
| `archetype` | Refresh only if the posture has materially changed. |
| `arrShare.value` / `arrShare.denominator` | Update if the share or the denominator BU revenue moved. |
| `watchSignals` | Replace with the new narrative paragraph. |

Then bump the **methodology block** at `site-data.json:dashboard.vendorPostureMethodology`:

- `lastEditorialReview`: today's date (`YYYY-MM-DD`).
- `lastUpdated`: same.

The visible "Last editorial review" stamp on the SaaS AI Transition Map section reads from `lastEditorialReview` — bumping it is what tells readers the radars have been refreshed.

---

## Step-by-step

### 0. Set up

- Confirm the live site is at the head of `main` and a clean working tree on a fresh branch (`wq-NNN-posture-review-YYYY-Qn`).
- Open the brief (§6 has the canonical rubric).
- Open this playbook in a second pane.

### 1. Per company — pull the primary sources

For each of the 12 cohort entries, gather the three sources before scoring anything:

| Axis | Source you must open |
|---|---|
| Disclosure | Latest earnings call transcript / 10-K / 10-Q / press release that names the AI ARR figure (or confirms the absence of one). |
| Bundling | Vendor pricing page (today). Also note any pricing-tier renames or AI-SKU consolidations announced in the last quarter. |
| Pricing model | Same pricing page + sales-motion commentary in the latest earnings call. |
| Cost realisation | Latest GM disclosure (10-Q segment or non-GAAP) plus any explicit AI-attribution commentary in the earnings call. For the Microsoft trio, the parent Cloud GM line is the canonical source — they share. |
| Acceleration | Latest two reported top-line growth rates for the parent (or business unit if D7 BU denominator is in play). |

Don't score from memory. If you don't have a primary source open, the score change is editorial drift, not a review.

### 2. Apply the rubric

Verbatim from brief §6:

**Disclosure (DISC)**
- 5 = directly disclosed in earnings (tier 1b) AND material share of host business (>5%)
- 4 = tier_1b + 1–5% share, OR tier_2a + >5% share
- 3 = tier_2a + 1–5% share, OR tier_1b + <1% share
- 2 = tier_2b + 1–5% share, OR tier_2a + <1% share
- 1 = tier_2b + <1% share

**Bundling (BNDL)**
- 5 = aggressive separate pricing (premium add-on)
- 3 = mixed (some bundled, some premium)
- 1 = baked into existing SKUs at no upcharge

**Pricing Model (PRICE)**
- 5 = new commercial model (per-action, per-agent, outcome-based) is the only way they sell
- 3 = credit / consumption layer added on top of seat pricing, OR usage option exists alongside seat pricing
- 2 = AI premium SKU added on existing pricing model (tier upgrade)
- 1 = no change, AI absorbed into existing SKUs

**AI Cost Realisation (COST)** — counter-intuitive: a higher score means margin compression you can attribute to AI workload (proof of real workload).
- 5 = clear AI-attributable margin compression
- 4 = some AI-attributable compression visible
- 3 = some movement, ambiguous attribution
- 2 = minimal observable signal
- 1 = no observable AI cost in margins
- 0 = NA (private company, no public GM)

**Acceleration (ACCEL)**
- 5 = materially accelerated since AI product GA
- 3 = no inflection (flat)
- 1 = decelerated since AI launches

### 3. Score discipline

- Don't move a score by 1 just because the company has been "in the news." Move it because the rubric says it should move given current sources.
- D7 stands: use the business-unit denominator for `arrShare` where one cleanly exists (GitHub for Copilot, Workspace for Workspace AI, Dynamics for Dynamics Copilot, ORCL Cloud Apps for Fusion AI). Use parent-total only as a fallback.
- The Microsoft trio (M365 / GitHub / Dynamics Copilot) shares one parent GM. They can have different DISC / BNDL / PRICE / ACCEL scores but the COST score should move together because the underlying margin signal is one company.
- Private vendors (Databricks, Notion) keep `gmUnavailable: true` and `cost: 0`. Don't score Cost from press estimates.
- If a score changes by 2+ in a single review cycle, write a short note in the watch-signals paragraph explaining what moved and why. Big jumps without an explanation are usually a sign the editor is re-tuning rather than reviewing.

### 4. Update the data

Edit `scripts/wq101_extend_posture.py`:

- Update each company's `postureScores` integers, `scoreCitations.{bundling,cost}` strings, `archetype` (only if changed), `arrShare`, `watchSignals`.
- Bump `LAST_VERIFIED` to the new quarter (e.g., `"2026-Q2"`).
- For each company whose citations now trace to primary sources you opened in step 1, drop the `_prototype: True` flag in the script's update logic for that entry (i.e., set it conditionally — see the existing extend logic for the pattern).
- Bump `VENDOR_POSTURE_METHODOLOGY.lastEditorialReview` and `lastUpdated` to today's date.

Run the script:

```bash
python3 scripts/wq101_extend_posture.py
```

It rewrites the affected fields in `site-data.json` idempotently.

### 5. Regenerate watch-note ARR cells if needed

The Reported AI ARR / Real / Share cells under each radar are pipeline-fed (claims → vault → entities → site-data.json). If a relevant claim was applied since the last review, those cells already reflect it. If a new disclosure landed during this review and you want it to show before the next claim cycle:

- File the claim through the normal review path (claims.html).
- After applying, re-run the extension script so the manually-set fields don't clobber the pipeline-set ones.

### 6. Validate

```bash
node scripts/validate-vendor-posture.mjs
```

Must report 0 fail. The validator checks: cohort size = 12, axis ranges, private GM-NA treatment, `_lastVerified` format, `lastEditorialReview` presence on the methodology block.

### 7. Stage + ship

Per the publishing gate (CLAUDE.md):

1. Push to `beta` branch.
2. Wait for the deploy-beta workflow (typically <15s) and the Pages deploy (~2 min).
3. Visit `https://ai-index.hepburnadvisory.com.au/beta/usage.html`. Confirm the "Last editorial review" stamp under the section heading shows today's date.
4. Walk the 12 radars and the watch notes. Spot-check 2–3 score changes against the citations you wrote.
5. Share the staging URL with Simon. Wait for `approved` / `ship it` in chat.
6. Promote to `main`.
7. Write a deployment record at `docs/deployments/deploy-YYYY-MM-DD-vendor-posture-review-YYYY-Qn.md` summarising which scores moved and why. The record is the diff between this review and the previous one.

---

## Editorial drift checklist

If you can't honestly answer "yes" to all of these, don't ship the review:

- [ ] Did I open a primary source for every score change?
- [ ] Did I avoid moving scores I had no new evidence for?
- [ ] Are the bundling / cost citations strings I updated traceable to a URL or a transcript line — not paraphrase from memory?
- [ ] Does each company's watch-note paragraph match the new score profile?
- [ ] Did I bump `lastEditorialReview` so the surface reads honestly about how fresh this is?

---

## Why this is manual

The four non-Disclosure axes depend on signals that don't extract reliably from claim text:

- Bundling lives in a vendor pricing page that may not generate a structured claim each quarter.
- Pricing Model needs a sales-motion read (is per-agent the *only* way they sell, or just an option?).
- Cost Realisation requires GM attribution that's often hedged in management commentary — a parser can't reliably tell "GM down 1pp due to AI" apart from "GM down 1pp due to mix shift."
- Acceleration needs a year-over-year inflection comparison the claims pipeline doesn't currently emit.

Disclosure alone could be auto-derived from `provenance × arrShare%` (rubric §6 is mechanical), but mixing one auto axis with four editorial axes makes the readout harder to interpret, not easier. Per D5: keep all five editorial, surface the review date instead.
