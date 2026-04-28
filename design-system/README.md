# Hepburn Advisory — Design System

Design system for **Hepburn Advisory**, an independent advisory firm at the intersection of AI commercialisation and AI economics. The practice ships into two surfaces that share one visual language:

1. **Hepburn Advisory** — the advisory firm site (`hepburnadvisory.com.au`). Light, executive, Webflow-rendered. First-person singular voice ("I advise…"). Two service tracks only: Founder Advisory and Executive Advisory.
2. **The AI Ledger** — the flagship data publication (`ai-index.hepburnadvisory.com.au`). Dark, numerate, quotable. Triangulates capital / revenue / usage into three interlocking views. Published without editorial lean.

The same designer, same palette, same type — two tonally distinct skins.

---

## Sources read to build this

Everything below is derived from, and should stay consistent with, these primary artefacts:

| Source | Where | Why it matters |
|---|---|---|
| Live AI Ledger dashboard | `Claude/Code/apac-ai-intel/beta/index.html` + `dashboard.html`, `sankey.html`, `capital.html`, `revenue.html`, `usage.html`, `timeline.html`, `openrouter.html` | Dark-theme visual foundation, palette tokens, nav pattern, card grammar, chart style. The canonical implementation. |
| Ledger guidelines | `Claude/Projects/The AI Ledger/GUIDELINES.md` | Editorial voice rules, banned framings, hero-hook pattern, palette lock, freshness dots, mobile rules, page structure. Section §2 and §7 here are lifted straight from it. |
| Site rebuild plan | `Claude/Projects/Hepburn Advisory Web Site Content & Management/site-rebuild-plan.md` | Positioning, two-track service model, voice rules, homepage/advisory copy. Defines what Hepburn is *not*. |
| Site management workflow | `…/workflow.md` | Non-negotiables (no "Fractional", first-person singular, no fake testimonials). |
| Article draft | `Claude/Projects/Hepburn Advisory Thought Leadership/handoff_ai_saas_problem.md` | Long-form editorial voice, actual finished writing, Simon's rhetorical signature. |
| Logo assets | `uploads/Logo-*.png` | Black rounded-square mark + "Hepburn Advisory" wordmark. Re-captured as SVG in `assets/logo-icon.svg`. |
| PPT template | `uploads/PPT-Template.potx` | **Not accessible at build time** — flagged below. Slide templates here are a first pass; user to review and correct. |
| GitHub repo | `sibowker-oss/ai-token-tracker` | Public mirror of the Ledger code; not imported (local codebase is the same source). |

All paths are read-only references. The design system is fully self-contained — assets have been copied into `assets/`.

---

## Index — what's in this folder

```
/
├── README.md                    ← you are here
├── SKILL.md                     ← Agent-Skill spec, portable to Claude Code
├── colors_and_type.css          ← CSS variables (color + type + spacing + motion)
├── assets/                      ← logos, SVG mark, brand imagery
│   ├── logo-icon.svg            ← the sparkle mark, black on white, 100×100
│   ├── logo-icon-inverse.svg    ← inverse (white mark on black)
│   ├── logo-icon-black.png
│   ├── logo-horizontal.png
│   ├── logo-vertical.png
│   ├── logo-vertical-transparent.png
│   ├── logo-opaque.png
│   └── brand-lockup-draft.png   ← reference only, exploration lockup
├── preview/                     ← design-system card previews (for the Design System tab)
├── ui_kits/
│   ├── ledger/                  ← dark, data-first dashboard kit (AI Ledger)
│   │   ├── README.md
│   │   ├── index.html
│   │   └── *.jsx
│   └── advisory/                ← light, executive firm-site kit (Hepburn Advisory)
│       ├── README.md
│       ├── index.html
│       └── *.jsx
└── slides/                      ← 16:9 slide templates (briefing decks)
    ├── index.html
    └── *.jsx
```

---

## Content fundamentals

Voice is load-bearing for this brand. The numbers are the story — copy is the frame.

### Overall tone

- **Operator, not consultant.** "I advise founders on commercial scale" — never "we deliver strategic value for our clients."
- **No hype, no doom.** Banned: *revolutionary, transformative, unlock, leverage, seamless, end-to-end, AI bubble, AI winter, hits the wall, the reckoning*. Banned on the advisory site: the word *Fractional*, ever.
- **Short sentences. Plain words. Numerate.** Every claim either sourced, derived with method shown, or clearly labelled as opinion ("Hepburn view:" / "Analyst note:").
- **Transparently approximate.** Say "~$17B", "directional", "Med confidence" — never pretend to precision the data doesn't have.
- **Interpretive verbs tied to arithmetic.** Prefer *implies, requires, reconciles to*. Avoid *shows, proves, reveals*.

### Voice splits by surface

| Surface | Pronoun | Register | Example |
|---|---|---|---|
| Advisory site | "I" (first-person singular, singular Simon-led practice) | Direct, operator-to-operator, executive | *"I advise AI founders on commercial scale and enterprise executives on AI strategy. Operator experience. No slideware."* |
| AI Ledger | Third-person data voice | Neutral, numerate, declarative | *"The Ledger shows ~$745B in AI capex against ~$22B in customer revenue — roughly $34 spent for every $1 earned."* |
| Editorial (Insights, LinkedIn) | "I" + analytical | Long-form, argumentative but sourced | *"I want to push that thought further… this is the SaaS implementation tax, re-skinned."* |

### Casing

- **Sentence case** for all headlines, buttons, nav items, slide titles. *"Claims Ledger"* — not *"CLAIMS LEDGER"*, not *"Claims ledger"*.
- **UPPERCASE** used only for eyebrows / meta labels (tracking `0.08em`), never for body content.
- **Title Case** only on proper nouns, products, and the two-word page pattern `[Noun] Ledger` (Capital Ledger, Revenue Ledger, Usage Ledger, Claims Ledger).

### "I" vs "you"

- "I" when Simon speaks (advisory site, editorial).
- "You" is used sparingly and only in a direct reader address ("If you're selling AI into the enterprise, you're not competing on model quality anymore"). Never marketing-"you".
- No "we" unless quoting a third party. Hepburn Advisory is solo.

### Hero-hook pattern (Ledger)

Every substantive Ledger page opens with a provocative, numerate framing that forces a denominator into view. Declarative form, reader supplies the answer:

> **"For AI to hit $X by 20YY, it needs to equal Z% of global IT spend, W% of global payroll, or replace Q of today's SaaS market. Pick one."**

### Chart and table titles

State what is measured. Not what it means.

- Good: *"US data-centre interconnection queue, by ISO (GW, 2025)"*
- Bad: *"The AI grid crunch in one chart"*

Interpretation belongs in methodology blocks, tooltips, or clearly-marked "Hepburn view:" callouts — never the title.

### Methodology caveat (required on data pages)

Every page with derived numbers carries a collapsible methodology block:

> *Projections are directional arithmetic, not forecasts. Benchmarks are dated and sourced. [Derived metric] defaults to [method]; every assumption is editable.*

### Emoji

**Not used.** No emoji in Ledger copy, no emoji in advisory copy, no emoji in slide decks. The one exception is the sparkle mark itself — which is a logo, not an emoji. Use glyphs like `→`, `·`, `—` for rhythm instead.

### Numbers

- Tabular numerals always (`font-variant-numeric: tabular-nums`). Columns of numbers must line up.
- Rounding is honest: `~$745B`, `~650T tokens/day`, `42%`. Over-precision looks unserious.
- Dollar figures use `$` (not `USD`), TB/GB/GW/TWh with no space, dates in ISO-like long form: `21 Apr 2026`.
- Confidence on every number: High / Med / Low, set honestly. Downgrade when in doubt.
- ARR vs booked revenue is **always** labelled — they are not interchangeable.

---

## Visual foundations

### The mark

A 4-point sparkle/compass-rose glyph, all concave sides meeting at a single center, inside a rounded-square container. Reads as *a pole star* and *a precision tool* — which fits the brand (triangulation, numerate authority).

- **Container:** rounded square, corner radius `18px` on a 100-unit viewBox (so `18%`).
- **Default:** black mark on white, **or** white mark on black. Both are primary.
- **Never:** colourise the mark (no gradients, no accent-blue fill), no glow, no drop shadow, no rotation.
- **Minimum size:** 24px for favicon, 32px for UI chrome, 56px for marketing.
- **Clearspace:** one-quarter of the mark's width on all sides.
- **With wordmark:** icon + "Hepburn Advisory" in Inter 700, optical sizing matched (see `assets/logo-horizontal.png`).

### Colour

The palette is **small, fixed, and shared** between light (Advisory) and dark (Ledger) surfaces. Do not introduce new hues.

**Ink (neutrals):** `#0A0A0A` brand black, plus a slate neutral ramp (`#111827 → #F8FAFC`) taken directly from the Ledger implementation.

**Accents (fixed):**
- `#3B82F6` Blue — primary, links, Capital Ledger
- `#10B981` Green — Revenue Ledger, positive, Tier 1 sourced
- `#8B5CF6` Violet — Usage Ledger, Tier 3 modeled
- `#06B6D4` Cyan — tertiary series
- `#F59E0B` Amber — Power Ledger, emphasis, Tier 2 derived
- `#EF4444` Red — reality-check, warnings (used sparingly; the Ledger is not a panic site)

Semantic use is consistent: **blue = capital / primary**, **green = revenue / sourced**, **violet = usage / modeled**, **amber = power / derived**. When in doubt, borrow from the live Ledger.

### Type

- **Primary:** Inter (400, 500, 600, 700, 800). UI, body, headlines. Required feature: tabular numerals for any numeric rendering.
- **Editorial:** Source Serif 4 — long-form only (Insights essays, print briefings). Never in UI.
- **Mono:** JetBrains Mono — code, methodology snippets, provenance meta.

Headlines carry `letter-spacing: -0.02em` (heads) to `-0.035em` (mega display). Body is tracked at 0. Eyebrows are UPPERCASE at `+0.08em`.

Scale is tight and information-dense: see `colors_and_type.css` §5. Don't guess — use the `--type-*` slots.

### Backgrounds

- **Advisory (light):** warm off-white `#FBFBF9` at page level, crisp white cards, a slightly warmer secondary band `#F4F3EE` used sparingly for section breakers. No full-bleed photography. No gradients at the page level. No patterns or textures.
- **Ledger (dark):** `#0A0E1A` page, `#111827` cards, `#0F172A` nav. Gradients are **allowed only** on the wordmark/brand lockup (`linear-gradient(135deg, #3B82F6, #8B5CF6)` clipped to text) and on Sankey/flow diagrams. No glassmorphism. No animated gradient backgrounds. No mesh gradients.
- **Hand-drawn illustrations:** none. The brand doesn't use them.
- **Repeating patterns / textures:** none. The one accepted "pattern" is tabular data itself — let the grid do the work.

### Imagery

- Generally **no imagery** beyond the mark and data visualisations. The Ledger is pure data viz.
- Portraits: Simon's headshot on About only. No stock photography implying a team that doesn't exist (this is an explicit brand non-negotiable — see `workflow.md`).
- Any decorative imagery is cool-biased, desaturated, and never warm/grainy. The brand is precise, not editorial-magazine.

### Motion

- **Restrained.** 120ms for UI nudges (hover), 180ms for state changes, 280ms for appearance transitions. Easing: `cubic-bezier(0.22, 1, 0.36, 1)` (ease-out) for entries, `cubic-bezier(0.65, 0, 0.35, 1)` for state swaps.
- No bounces, no springs, no attention-grabbing wiggle. No animated number counters (they undermine the "quotable number" contract).
- Scroll-triggered animation is acceptable only for charts populating from left-to-right on first view.

### Interactive states

| State | Light surface | Dark surface |
|---|---|---|
| Default | `var(--surface-light)` white / border `#E7E5DC` | `var(--surface-dark)` `#111827` / border `#1E293B` |
| Hover (cards, tiles) | border → `var(--blue)`, `transform: translateY(-2px)`, shadow lifts one step | border → `var(--blue)`, `transform: translateY(-2px)` |
| Hover (buttons, links) | background darken ~8% | background → `#334155` |
| Press | transform none, reduced shadow (no shrink) | transform none, slightly darker background |
| Focus | `box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35)` (both surfaces) | same |
| Active nav | blue `#3B82F6` fill on dark / blue text on light | on dark: `#1E3A5F` bg + blue border + white text |

**Press state does not shrink.** Scale-down on press feels consumer-app-y and undermines the executive register.

### Borders

- **1px, hairline, low-saturation.** Light: `#E7E5DC`. Dark: `#1E293B`. The 2px variant exists only for nav bottom-borders.
- Cards rely on **border + subtle shadow** (light) or **border only** (dark). Never border + heavy shadow + inner glow stack.
- Left-accent borders are **not** a Hepburn pattern — do not add coloured vertical borders on cards. (Looks generic; Ledger doesn't use them.)

### Shadows

- Light surface: `0 1px 2px` default, `0 8px 24px` on elevation. No coloured shadows. No inner shadows.
- Dark surface: shadows are mostly invisible; use border contrast instead. Exception: Sankey nodes and chart tooltips can carry a `0 4px 16px rgba(0,0,0,0.4)` lift.

### Corner radii

- **4px** — badges, tier pills.
- **6–8px** — buttons, nav links, inputs.
- **12px** — standard card (this is the default; used everywhere on the Ledger).
- **16px** — hero tiles (the big number cards on home).
- **18px** — the brand mark's container corner (matched on any "logo-shaped" treatment).
- **999px** — pills, filter chips.

### Cards

A Hepburn card is: **1px border, 12px radius, 20–28px padding, no gradient, no heavy shadow.** On dark, the only "elevation" comes from the border + the card background being one step lighter than the page. On light, add the smallest shadow in the ramp and a slightly warm border.

Nested cards are rare. If one appears, it drops the border and uses a tinted background (`rgba(colour, 0.06)`) instead.

### Transparency + blur

- Sticky filter bars use `rgba(17, 24, 39, 0.95)` + `backdrop-filter: blur(12px)` on dark. Matches the live Ledger exactly.
- Outside of sticky chrome, **no glassmorphism.** Do not use translucent "floating" cards on gradients.

### Layout rules

- Max content width **1320–1400px** (Ledger dashboards use 1400; advisory uses 1200). Don't push wider.
- Mobile is a first-class render target (see GUIDELINES §7.5). No horizontal scroll ever. Tap targets ≥44×44. Body copy ≥16px on mobile.
- Nav: fixed at top, `#0F172A` on dark / white with hairline border on light, never collapses to a hamburger above 768px.
- Slide aspect is 16:9 (1920×1080), using `deck_stage.js`.

---

## Iconography

Hepburn's approach to iconography is **minimal and functional**. The brand is numerate, so the visual weight is carried by numbers, not icons. When icons are needed:

### What's used in production

- **Unicode glyphs and arrows** — the Ledger uses them constantly:
  - `→` navigation, next step
  - `·` separator (Hepburn view: mid-dot, not bullet)
  - `—` em-dash for meta separators
  - `✓` inline confirm
  - `↗` external link (both on nav links to other properties and inline in copy)
  - Geometric markers: `△ ▣ ● ↻` — used on the home page to tag Capital / Assets Built / Tokens / Revenue (see live `index.html`).
- **The sparkle mark** — used as the brand anchor, occasionally as a "built by Hepburn" micro-badge in data viz corners. See `assets/logo-icon.svg`.
- **Freshness dots** — `8px` solid circles coloured by data age (green ≤30d, yellow 31–90d, grey >90d).
- **Tier pills** — not icons, but functionally iconic: small rounded rects coloured by provenance tier (Tier 1 green, Tier 2 amber, Tier 3 violet).

### No standard icon set is in use

The live codebase contains **zero SVG icon imports**. There is no Lucide, Heroicons, Feather, or Phosphor dependency. This is a deliberate aesthetic choice — "icons everywhere" undermines the numerate voice.

### Substitution policy

If a design needs something genuinely iconographic (e.g. UI controls beyond Unicode), substitute **Lucide** (`lucide.dev`) with stroke width **1.5px** loaded from CDN. It's the closest match to the brand's restraint. **Flag the substitution to the user** — the pattern isn't established in production, so any usage should be approved.

**Do not:**
- Use emoji anywhere. Ever.
- Hand-roll bespoke SVG icons when the built-in Unicode glyph works.
- Use coloured / illustrative icons — if Lucide is introduced, strokes only, `currentColor`.
- Invent gradient-filled decorative icons.

---

## Index to kits + slides

| Resource | Purpose | Width × Height |
|---|---|---|
| `ui_kits/ledger/index.html` | The AI Ledger dashboard — dark, data-first, the flagship publication | 1400 × ~1800 |
| `ui_kits/advisory/index.html` | Hepburn Advisory firm site — light, executive, two-track | 1200 × ~2000 |
| `slides/index.html` | 16:9 slide templates for briefings (`deck_stage`) | 1920 × 1080 per slide |

---

## Caveats + known gaps

- **PPT template (`uploads/PPT-Template.potx`) was not readable** at build time — the file was either removed or not accessible. Slide templates here are derived from the Ledger's dark theme + Advisory's light theme, **not** from the PowerPoint file. Please re-attach the `.potx` if the slide look should match it.
- **Fonts substituted to Google Fonts.** Inter + Source Serif 4 + JetBrains Mono are all CDN-loaded. If you have brand-licensed alternates (or if the PPT template specifies a different face), replace the `@import` in `colors_and_type.css`.
- **Simon's headshot** is referenced in the site plan but not placed in `assets/` — I have not copied a personal photograph without explicit approval. Drop `Simon-Bowker-Headshot-2.jpg` into `assets/portrait.jpg` if you want it in the advisory kit.
- **"Fractional" must never appear** in output from this system. Encoded in SKILL.md as a hard rule.

---

## Change log

| Date | Change |
|---|---|
| 2026-04-24 | Initial system. Palette locked to live Ledger tokens. Two surfaces (light Advisory, dark Ledger) sharing one type + palette. |
| 2026-04-28 | **Defect flagged (post-launch cleanup):** the two SVG mark files have file names inverted relative to their on-disk colour. `assets/logo-icon.svg` is *white sparkle on black square* (rect `#0A0A0A`, path `#FFFFFF`) — the README and SKILL.md both describe it as "black on white". `assets/logo-icon-inverse.svg` is the opposite: black sparkle on white square. Functionally the dark-Ledger ui_kit consumes the right asset (`logo-icon-inverse.svg`) and renders correctly, but the names contradict the docs. Renaming was deferred to avoid mid-launch risk during wq-033. Cleanup task: either rename the files to match the docs, or update README/SKILL/brief descriptions to match the files. Flagged by Track A Phase 0b, 2026-04-28. |
