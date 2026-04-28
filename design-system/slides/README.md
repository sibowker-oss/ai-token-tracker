# Slides — 16:9 briefing templates

Twenty canonical slide layouts for board briefings and external decks. Run on `deck_stage.js`. Arrow keys to navigate. Speaker notes included. See `MASTER.md` for the full spec.

## The template set

### Foundational (mirrors the original .potx master)
1. **Title** — ink, wordmark top-left, three-part meta footer (prepared by / for / date).
2. **Agenda** — light, numbered two-column outline with per-item descriptions.
3. **Section break** — warm, `§ NN — label` marker, title + lede. Use between sections.
4. **Content** — light, single narrative column with pull-quote sidecar.
5. **Two-column** — light, balanced issuer-narrative vs. Hepburn-reconciliation.
6. **Three focus areas** — light, numbered tile cards. Use for services or scope.
7. **Four tiles** — dark, Ledger books (Capital/Revenue/Usage/Power) with semantic colour keys.
8. **Metrics** — light, 4-up headline stats with top-border treatment.
9. **Mega number** — dark, one number at 180px, gradient-clip emphasis, provenance mandatory.
10. **Claim vs reconciliation** — light, italic pull-quote beside an amber reconciliation block.
11. **Pull quote** — warm, centred editorial quote with attribution.
12. **Recommendations** — light, check-bullet list of 3–5 moves.
13. **Roadmap** — light, 4-phase horizontal track with week-window durations.

### Extended briefing
14. **Editorial** — light, Source Serif long-form, drop-cap opening. Max one per deck.
15. **Comparison** — light, green/red two-up with tick/cross bullets.
16. **Ledger table** — dark, dense tabular data with tier pills and totals row.
17. **Timeline** — warm, vertical rail with dated milestones.
18. **Appendix** — light, sources + provenance-tier legend + known-gaps list. Last content slide.
19. **Close** — ink, three-action footer with monospace scope annotations.
20. **Thank you** — ink, contact block with labelled channels.

## Structure rules
- Always 1920×1080. Top-left = brand lockup. Top-right = meta (date, tier, audience). Bottom-right = page number `NN / TT`.
- Max three typographic weights per slide. Max two accent colours per slide.
- Every number ships with tier + confidence. No exceptions.
- No stock photography. No emoji. No bullet-list title slides.
- Section breaks use a different background from the slides around them (rhythm through colour, not animation).

## Speaker notes
The `#speaker-notes` JSON array at the bottom of `index.html` is read by the deck-stage host and surfaced in the speaker-notes drawer. Each entry is a full script, not a bullet list.
