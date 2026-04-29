# wq-034 — Subscription page → HA Contact integration

**Status:** **LEDGER-SIDE SHIPPED 2026-04-29** — Phase 0 + Phase 1 + Phase 4 complete on `apac-ai-intel/main`. Phase 2 (HA `/contact/` checkbox + `?subscribe=ledger` pre-fill) and Phase 3 (manual migration of 2 subscribers) remain owned by HA cowork session and Simon respectively. Frozen 2026-04-27 per GUIDELINES §9.3.
**Working name:** Single-list subscription via HA Contact form
**Placement:** `index.html` `.subscribe-wrap` section, plus any other Ledger surfaces with email capture (currently `predictions.html`, `vault.html`, `parked/feed.html` per grep).
**Date drafted:** 2026-04-27
**Owner candidate:** Claude Code (Ledger side) + parallel work on HA Contact form (HA cowork project)
**Target:** V2 launch parallel with HA site, this week.
**Related items:** wq-033 (design alignment — sub box uses HA component patterns), wq-035 (cross-launch contract).

---

## 1. Working name, placement, status

Single-list subscription via HA Contact form. Replaces the current Formspree-backed Ledger subscribe form with a link-out to HA `/contact/` carrying a "subscribe to AI Ledger updates" checkbox.

Current state per `apac-ai-intel/index.html`:
```
<form action="https://formspree.io/f/mqegqzny" method="POST" class="subscribe-form">
  <input type="email" name="email" placeholder="your@email.com" required>
  <input type="hidden" name="_subject" value="AI Ledger Newsletter Signup">
  <input type="hidden" name="_next" value="https://ai-index.hepburnadvisory.com.au/?subscribed=true">
  <button type="submit">Subscribe</button>
</form>
```

Goal state: form replaced with a CTA card that links to `https://hepburnadvisory.com.au/contact/?subscribe=ledger&utm_source=ledger&utm_medium=site&utm_campaign=v2-launch&utm_content=sub-cta`.

## 2. Purpose (one paragraph, single question)

Per Simon: one capture mechanism, one list. The HA `/contact/` form is the canonical lead-capture surface — it carries an optional checkbox for "subscribe to news + AI Ledger updates" (which are the same list). The Ledger sub box becomes a marketing surface that links back to HA.

## 3. Editorial positioning

Sub-CTA copy stays Ledger-voice — numbers-first, factual. Examples that fit GUIDELINES §2:

- *"Updates when the Ledger shifts — new filings, revenue moves, structural signals."*
- *"Hepburn Advisory publishes the Ledger and a short brief when the numbers move. Subscribe via the contact form."*

Avoid: *"Don't miss out", "Join thousands", "Get exclusive insights"* — see §2.2.

## 4. Core deliverables

### 4.1 Strip Formspree from Ledger pages

Remove the `<form>` element from `index.html` and any other Ledger surface with email capture. Specifically:
- `index.html` lines ~320-332 (the `.subscribe-wrap` section).
- `predictions.html`, `vault.html`, `parked/feed.html` — confirm whether these have similar forms or just reference the word; if forms, replace with the new pattern.

### 4.2 Replace with link-out CTA card

New component, design tokens per wq-033:

```html
<section class="subscribe-wrap">
  <div class="subscribe-box">
    <span class="eyebrow">Stay informed</span>
    <h3>The Ledger updates as the data lands.</h3>
    <p>Hepburn Advisory publishes a short brief when the numbers move. One list, both Hepburn news and AI Ledger updates.</p>
    <a href="https://hepburnadvisory.com.au/contact/?subscribe=ledger&utm_source=ledger&utm_medium=site&utm_campaign=v2-launch&utm_content=sub-cta"
       class="btn-primary">
      Subscribe via Hepburn Advisory <span aria-hidden="true">↗</span>
    </a>
  </div>
</section>
```

Box uses dark surface tokens per wq-033 §4.2, button uses `.btn-primary`, eyebrow + h3 + p + CTA stack — matches the visual language a referrer arriving from HA already knows.

### 4.3 HA Contact form changes (parallel work in HA cowork project)

This brief flags the HA-side dependency but doesn't own the implementation:

- HA `/contact/` form gains an optional checkbox: `[ ] Subscribe to Hepburn Advisory news and AI Ledger updates`.
- When the URL query param `?subscribe=ledger` is present, the checkbox is pre-checked on page load.
- Submission writes to a single subscribers list (or tags subscribers as `source=ledger` if subscribe=ledger param was present, for attribution).
- Form retains UTM params on submit so HA can attribute to launch campaigns.

Per Simon 2026-04-27: HA `/contact/` does NOT yet have this checkbox. New HA-side work.

### 4.4 Migration path for existing Formspree subscribers

Per Simon 2026-04-27: 2 existing subscribers. Manual forward post-launch. Not a Claude Code task.

### 4.5 Decommission Formspree at the right moment

After migration completes, the Formspree endpoint stops being referenced. Make sure no Ledger page references `formspree.io/f/mqegqzny` at launch.

### 4.6 Privacy / consent copy

The HA `/contact/` page already references `/privacy`. Ensure the AI Ledger subscription pathway is covered by that policy — specifically, that "subscribers via the AI Ledger" are noted as a category.

## 5. Data audit

What exists:
- Formspree endpoint `/f/mqegqzny` with 2 subscribers.
- HA `/contact/` form (does NOT yet have the optional-subscription checkbox).
- `/privacy` page on HA (referenced from footer).

What Claude Code resolves in Phase 0:
- Whether `predictions.html`, `vault.html`, `parked/feed.html` actually capture emails or just contain the word.

## 6. Schema extension

None on the Ledger side. Possibly minor on HA side (subscribers gain a `source` tag).

## 7. Visualisation plan

V1 (must-have for launch):
- Formspree forms removed from all Ledger pages.
- Replacement CTA card live on `index.html`.
- HA `/contact/` form has subscribe checkbox + query-param pre-fill.

V1.1 (post-launch):
- Manual migration of 2 existing subscribers (~5 min by Simon).
- Subscriber attribution dashboard on HA side (how many came via Ledger vs direct).

## 8. Source tracking & agent log requirements

No new sources or agents.

## 9. Implementation phases (post-decisions)

- **Phase 0 — Ledger-side audit.** Confirm which Ledger pages actually have capture forms vs just word matches. ~0.25 day.
- **Phase 1 — Ledger-side strip + replace.** Remove Formspree forms, add CTA card with UTM-laden link to HA `/contact/?subscribe=ledger`. ~0.5 day.
- **Phase 2 — HA-side checkbox + pre-fill.** Owned by HA cowork project. Out of Ledger scope but blocking for V2 launch. ~0.5 day.
- **Phase 3 — manual subscriber migration.** Simon forwards 2 existing subscribers post-launch. Not a Claude Code task. ~5 minutes.
- **Phase 4 — privacy + decommission.** Update `/privacy` reference if needed; ensure no Ledger page references `formspree.io/f/mqegqzny` after launch. ~0.25 day.

Total Ledger-side: ~1 day. HA-side: ~0.5 day (parallel). Migration: ~5 min manual.

## 10. Decisions log (closed at handoff time)

- **Subscribers:** 2. Migration trivial.
- **HA mailing-list provider:** deferred to HA cowork project.
- **HA checkbox status:** new HA-side work.
- **Migration timing:** post-launch manual, ~5 min.
- **UTM scheme:** confirmed per wq-035 §4.4.
- **Ledger-page audit (predictions/vault/parked-feed):** Phase 0 of implementation.

## 11. Change-log

| Date | Change | Reason |
|---|---|---|
| 2026-04-27 | Created. Frozen. | Drafted in Cowork session. |
| 2026-04-27 | Copied to apac-ai-intel/briefs/active/. | Cowork session staged the contract per GUIDELINES §9.3. |
| 2026-04-29 | Phase 0 audit complete. | Real Formspree forms = exactly 1 (index.html:335). Brief candidates predictions.html / vault.html / parked/feed.html investigated: predictions has no forms (word "subscriber" is body-copy noun); vault has the admin "Add Data Point" form, not email capture; parked/feed is out of audit scope. |
| 2026-04-29 | Phase 1 + Phase 4 shipped (Ledger-side). | Stripped Formspree form from index.html, replaced with link-out CTA per §4.2 markup template. UTM `utm_content=sub-cta` per wq-035 §4.4. Subscribe-box gradient background removed (was SKILL.md hard-rule-#10 violation). New `.btn-primary` class added to design-system/ledger-overlays.css §2a. ARCHITECTURE.md and data/page-registry.json updated to note Formspree decommission. memory/reference_email_subscriptions.md updated to reflect new state. 0 references to formspree.io/f/mqegqzny remain in *.html / *.md / *.js / *.json across active Ledger surfaces (excluding this brief and parked/feed.html — both intentional per §4.5). |

## 12. Last-updated

2026-04-27 — Cowork drafting; ready for Claude Code execution.
