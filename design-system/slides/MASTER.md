# Slide Master Specification

The authoritative spec for the Hepburn Advisory 16:9 briefing deck. Use this document before opening the HTML.

---

## 1. Canvas

| | Value |
|---|---|
| Aspect | 16:9 |
| Size | 1920 × 1080 px |
| Safe area | 96px outer margin (top/bottom 80px on dense slides) |
| Grid | 12-column, 24px gutter |
| Host | `deck-stage.js` web component (auto-scales to viewport) |

---

## 2. Surfaces

Pick **one** per slide. Never mix.

| Class | Background | Type | When to use |
|---|---|---|---|
| `.ink` | `#0A0A0A` | White | Title, close, thank-you. Ink is ceremony. |
| `.dark` | `var(--bg-dark)` | Light | Ledger data, mega numbers, dense tables. |
| `.warm` | `var(--bg-light-alt)` | Ink | Section breaks, pull quotes, timelines. Rhythm. |
| `.light` | `var(--bg-light)` | Ink | Default analytical surface. 60% of the deck. |

**Rhythm rule:** no more than three consecutive `.light` slides. Break with a `.warm`, `.dark` or `.ink` moment.

---

## 3. Chrome (every slide)

| Element | Position | Spec |
|---|---|---|
| Brand corner | top-left, 40px/96px | Logo icon (32px) + wordmark, 15px/700 Inter |
| Meta corner | top-right, 40px/96px | 11px/500 JetBrains Mono, right-aligned, 2 lines max |
| Page number | bottom-right, 40px/96px | Format `NN / TT` in 12px mono |
| Confidential flag | bottom-left, 40px/96px | Optional, 11px mono, uppercase, `.08em` tracking |

---

## 4. Type scale

| Role | Size | Weight | Letter-spacing |
|---|---|---|---|
| `.mega` | 180px | 800 | -0.04em |
| `.display` | 96px | 700 | -0.035em |
| `.title` | 72px | 700 | -0.03em |
| `.h2` | 48px | 700 | -0.02em |
| `.h3` | 32px | 700 | -0.015em |
| `.lede` | 28px | 400 | 0 |
| `.body` | 22px | 400 | 0 |
| `.caption` | 18px | 400 | 0 |
| `.eyebrow` | 14px | 600 | +0.14em uppercase |
| `.mono meta` | 11–14px | 500 | 0 (JetBrains Mono) |

Minimum body size on any slide: **18px**. Anything smaller goes in the appendix or is cut.

Max **three** typographic weights per slide. Max **two** accent colours per slide.

---

## 5. Colour rules

- Accent set is fixed: blue (Capital), green (Revenue), violet (Usage), amber (Power), red (reality-check). Do not invent hues.
- On `.ink` / `.dark`, blue is the interactive / eyebrow colour. On `.warm`, use ink-800.
- Section breaks change surface colour from the slides around them — rhythm comes from background, not animation.

---

## 6. Data discipline

Every number ships with **tier + confidence**. No exceptions.

| Tier | Meaning | Colour key |
|---|---|---|
| Tier 1 | Sourced from a primary filing or disclosure. High confidence. | green |
| Tier 2 | Triangulated from ≥2 sources. Medium confidence. | amber |
| Tier 3 | Modeled. Method must appear on the slide. | violet |

Use `.tier-pill.t1/t2/t3` on tables; inline ` · Tier N · Conf` on mega numbers.

Numbers use tabular lining figures (`font-variant-numeric: tabular-nums`). Always.

---

## 7. Layout reference

See `README.md` for the canonical 20-layout list with intended use. Each layout has a dedicated CSS block in `index.html`; reuse the class names verbatim rather than respecifying.

---

## 8. Speaker notes

- Format: a single JSON array in `<script id="speaker-notes">`, one entry per slide, in slide order.
- Voice: conversational full script, not bullets. Written for the speaker to read or paraphrase aloud.
- Length: 40–90 words per slide. Title and close may be shorter.
- The `deck-stage.js` host forwards `{slideIndexChanged: N}` to the parent window so the notes drawer stays in sync.

---

## 9. House rules

1. No stock photography. Portraits are commissioned or omitted.
2. No emoji.
3. No bullet-list title slides.
4. No gradient backgrounds (gradient clip-text on mega numbers is allowed).
5. No dropshadows on cards on `.dark` — use borders.
6. Every claim slide is followed, within two slides, by its reconciliation.
7. The editorial layout appears **at most once** per deck.
8. The appendix is the last content slide before Close. It is not optional.

---

## 10. Export

The deck exports to `.pptx` via the editable PPTX skill with slide dimensions 1920×1080. Speaker notes carry over automatically. See `../SKILL.md §6`.
