# SKILL — Hepburn Advisory Design System

A portable instruction set for any agent producing design artefacts for **Hepburn Advisory** (the advisory firm) or **The AI Ledger** (its data publication). Copy this file into `.claude/skills/hepburn-design/SKILL.md` for Claude Code, or keep it at repo root — it is self-contained and expects `colors_and_type.css` + `assets/` to sit alongside it.

---

## When to use this skill

Invoke when the task is any of:
- A page, section, or component on `hepburnadvisory.com.au` (light, executive)
- A page, chart, or module on `ai-index.hepburnadvisory.com.au` (dark, data-first)
- A slide deck, PDF briefing, or one-pager for client delivery
- Social/LinkedIn cards that carry either brand
- Any artefact that reads "by Hepburn Advisory" in its corner

Do **not** invoke for Simon's personal correspondence, ad-hoc tooling, or draft copy with no visual output.

---

## The two surfaces

| | Advisory | Ledger |
|---|---|---|
| URL | hepburnadvisory.com.au | ai-index.hepburnadvisory.com.au |
| Theme | Light (`#FBFBF9` page, `#FFFFFF` cards) | Dark (`#0A0E1A` page, `#111827` cards) |
| Voice | First-person singular ("I advise…") | Third-person data ("The Ledger shows…") |
| Max width | 1200px | 1400px |
| Primary accent | Ink black + blue (`#3B82F6`) for links | Fixed accent set (blue/green/violet/amber) semantically keyed |
| Imagery | None (portrait on About only) | Data viz only |
| Density | Executive, generous whitespace | Dense, every pixel paying rent |

Both share one palette and one type system. Never mix voices (no "I" on the Ledger, no first-person data on Advisory).

---

## Hard rules — do not negotiate these

1. **Never write the word "Fractional"** in output from this system. Not "Fractional CXO", not "fractional engagement", not "fractional" in any context. This is the first non-negotiable in `workflow.md`.
2. **Never imply Hepburn is more than one person.** No "we", no "our team". Singular practice, singular Simon Bowker.
3. **No fake testimonials, no invented client logos.** If a design needs a logo strip, ask the user — do not populate it with placeholder brand marks.
4. **No emoji.** Anywhere. The sparkle mark in `assets/logo-icon.svg` is not an emoji — it is a logo.
5. **Every number carries tier + confidence** (Tier 1 Sourced / Tier 2 Derived / Tier 3 Modeled; High / Med / Low). If the data doesn't support tiering, don't put a number on the page.
6. **ARR and booked revenue are never interchangeable.** Always label which.
7. **Banned verbs + framings:** revolutionary, transformative, unlock, leverage, seamless, end-to-end, AI bubble, AI winter, hits the wall, the reckoning. Also: "AI is" sentences that could be said about any software.
8. **Sentence case** for headlines, buttons, slide titles, nav items. UPPERCASE only for eyebrows (tracking `+0.08em`). Title Case for proper nouns and the `[Noun] Ledger` pattern.
9. **Tabular numerals** on every number: `font-variant-numeric: tabular-nums`.
10. **No gradient backgrounds**, ever. Gradients appear only on (a) the Ledger wordmark clip-text `linear-gradient(135deg, #3B82F6, #8B5CF6)` and (b) Sankey/flow diagrams.

---

## The workflow

1. **Read `README.md` and `colors_and_type.css`** before writing anything. The tokens are authoritative — do not hand-type hex codes.
2. **Pick the surface** (light Advisory or dark Ledger) and apply `body.surface-light` or `body.surface-dark` accordingly. This sets defaults for type, colour, and semantic classes.
3. **Use the semantic type slots** (`--type-h1`, `--type-mega`, `--type-editorial`, etc.) via the `.h1 / .mega / .editorial` classes — never raw `font-size` declarations.
4. **Check against the appropriate UI kit** — `ui_kits/advisory/index.html` or `ui_kits/ledger/index.html` — before inventing a new component. The kits cover nav, hero, tiles, cards, tables, filter bar, claim cards, charts, and methodology strips.
5. **For slides**, start from `slides/index.html`. Eight templates cover title, section break, mega number, claim+reconciliation, four tiles, editorial long-form, two-up comparison, and close.
6. **Copy required assets** from `assets/` into the artefact's folder — do not reference by absolute path. The sparkle mark has four canonical renditions: `logo-icon.svg` (black on white), `logo-icon-inverse.svg` (white on black), `logo-horizontal.png`, `logo-vertical.png`.

---

## Voice cheat sheet

**Advisory (first-person singular):**
- ✓ "I advise AI founders on commercial scale and enterprise executives on AI strategy."
- ✓ "Typical engagement: one quarter, one question."
- ✗ "We partner with leading enterprises to deliver transformative AI outcomes."

**Ledger (third-person data):**
- ✓ "The Ledger shows ~$745B committed against ~$22B booked — ~$34 per $1."
- ✓ "Issuer claim reconciles to $11.2B booked · gap 78% · Tier 2 Med."
- ✗ "This chart reveals the AI bubble about to burst."

**Editorial (Simon's long-form, in Insights):**
- First person, Source Serif 4, long paragraphs, argumentative but each claim sourced or labelled opinion ("Hepburn view:").
- Signature move: push an idea a notch past where the conventional framing stops, with a concrete number attached.

---

## Data viz rules (Ledger only)

- **Colour is semantic, not decorative.** Blue = Capital, green = Revenue, violet = Usage, amber = Power. If a chart needs a 5th series, use cyan. Do not introduce red except for reality-check annotations.
- **Chart titles state what is measured**, not what it means. Interpretation goes in tooltips, methodology, or marked "Hepburn view:" callouts.
- **Provenance tier pill + freshness dot** on every data module. Dot colours: green ≤30d, amber 31–90d, grey >90d.
- **Grid lines hairline, low-contrast** (`var(--border-dark)`, 1px). Axis text 10–11px, `--fg-dark-3`.
- **No animated counters.** Numbers are quotable — they do not tick up on scroll.
- **Tooltips are dense:** value + tier + confidence + method one-liner + "see source →" link.

---

## Component quick reference

```
Button (light, primary) → ink-1000 bg, #fff text, 8px radius, 10/18 pad
Button (dark, primary)  → blue bg, #fff text
Tile (metric)           → 16px radius, 24px pad, coloured label (eyebrow), 44px num, 11px meta
Card (default)          → 12px radius, 1px border, 20–28px pad, no shadow on dark
Pill (provenance)       → green/amber/violet tinted bg at 16% opacity + solid text colour
Freshness dot           → 8px circle, absolute-positioned on data label
Nav (light)             → white bg, hairline border, active link = blue text
Nav (dark)              → #0F172A sticky bg + blur, active link = blue-tinted chip
Table (Ledger)          → uppercase 10px headers, right-aligned tabular nums, hover tint
```

Every one of these exists fully realised in the UI kits. Copy, don't rebuild.

---

## When stuck

- If the design calls for something the system doesn't cover, **ask before inventing**. "Should this section use a warm section-breaker band or stay on page bg?" is a better question than guessing wrong.
- If a number's tier is unclear, **don't publish the number**. A missing metric is better than a falsely-precise one.
- If the user requests a look that breaks a hard rule (banned word, fractional, fake logo), **push back once**. If they insist, comply but flag the deviation in the commit/notes so Simon can catch it on review.
