# Claude API Automation — Project Spec

**Date:** 2026-03-31
**Purpose:** With an Anthropic API key now available, automate the remaining manual processes in the Global AI Dash pipeline.

---

## Current State

### Fully Automated (no changes needed)
| Script | Schedule | What it does |
|--------|----------|-------------|
| `auto_update.py` → `scrape_signals.py` | Daily 7am | Scrapes PyPI, npm, HuggingFace, GitHub, Docker, OpenRouter. Updates dashboard + site-data.json. Commits + pushes. |
| `news_monitor.py` | Daily 8am | RSS keyword alerts → news_alerts.json |
| `enrich.py` → `newsletter.py` | Monday 9am | Company enrichment + newsletter |
| `sync_ideas.py` | Daily 7:30am | Project Ideas folder → In Development page |
| `scrape_podcasts.py` | Wednesday 10am | Fetches transcripts from 8 podcast sources |
| `reconcile.py` | Wednesday 10:30am | Flags stale ARR/token estimates |

### Currently Manual (to be automated)
| Process | Current trigger | What blocks automation |
|---------|----------------|----------------------|
| **Claim extraction** from transcripts | Manual `python3 scripts/extract_claims.py` | Needed API key (now available) |
| **Vault URL enrichment** | Manual `python3 scripts/enrich_vault.py` | Needed API key (now available) |
| **Claim review + approval** | Manual via claims.html | Human judgement required |
| **site-data.json updates** from approved claims | Manual (paste into Claude Code) | Human judgement required |

---

## Proposed Changes

### 1. Auto-extract claims after podcast scrape
**What:** Chain `extract_claims.py` to run automatically after `scrape_podcasts.py` completes each Wednesday.

**Implementation:**
- Add to crontab: Wednesday 10:45am (after 10am scrape + 10:30am reconcile)
- Add `ANTHROPIC_API_KEY` to the cron environment
- Add GitHub Actions workflow `weekly-extract-claims.yml`
- Extract claims with `--auto-pr` flag → creates a PR with actionable candidates

**Outcome:** Every Wednesday, new transcripts are automatically scraped → claims extracted → PR created for review. Simon reviews the PR, merges what's valid.

**Estimated API cost:** ~$0.10-0.30/week (5-10 transcripts × 1-3 chunks × ~$0.03/chunk with Sonnet)

---

### 2. Auto-enrich vault Quick Add entries
**What:** Run `enrich_vault.py` on a schedule to process any URLs saved via the Quick Add form.

**Implementation:**
- Add to crontab: Daily 11am (catches any Quick Adds from the morning)
- Add GitHub Actions workflow `daily-enrich-vault.yml`
- Enriched entries get `status: pending` → appear in vault Weekly Review tab

**Outcome:** Simon pastes a URL + title in Quick Add. By next morning, the entry is fully enriched with extracted claims, entities, values, source types. Simon reviews in the Weekly Review tab.

**Estimated API cost:** ~$0.02-0.05 per URL enriched

---

### 3. Auto-generate weekly intelligence summary
**What:** New script that generates a weekly summary of all changes: new claims, reconciliation flags, stale data, ARR changes. Uses Claude to write a concise briefing.

**Implementation:**
- New script: `scripts/weekly_brief.py`
- Reads: reconciliation output, new claims, signals_latest.json, news_alerts.json
- Generates a markdown briefing summarising the week's intelligence
- Saves to `data-updates/weekly-brief-{date}.md`
- Optionally emails via Formspree webhook or saves to feed.html

**Outcome:** Every Wednesday afternoon, a ready-to-publish intelligence brief is generated summarising what changed, what's new, and what needs attention.

**Estimated API cost:** ~$0.05-0.10/week

---

### 4. Smart news alert enrichment
**What:** Currently `news_monitor.py` just matches keywords in RSS titles. With the API, it can read the full article and extract structured data points — same as podcast claims.

**Implementation:**
- Update `news_monitor.py` to optionally fetch full article text for high-priority alerts
- Send to Claude for claim extraction (same prompt as extract_claims.py)
- Save extracted claims alongside the alert in news_alerts.json
- Flag claims that conflict with current dashboard data

**Outcome:** When Bloomberg reports "OpenAI hits $25B ARR", the system automatically extracts the claim, matches it to the dashboard's current $20B figure, and flags the conflict for review.

**Estimated API cost:** ~$0.05-0.15/day (only processes high-priority alerts, not all RSS items)

---

### 5. Auto-reconcile with proposed updates
**What:** Currently `reconcile.py` flags conflicts but doesn't propose specific changes. With the API, it can draft site-data.json diffs.

**Implementation:**
- Add `--propose` flag to reconcile.py
- When conflicts are found, use Claude to draft the specific JSON changes needed
- Output as a structured diff that can be applied with one click/command
- Auto-create PR with proposed changes

**Outcome:** Instead of "Lovable ARR changed, tokens might be wrong", the system says "Lovable: update arrNumeric from 75M to 400M, update tokensNumeric from 20B to 100B" with a ready-to-merge PR.

**Estimated API cost:** ~$0.02-0.05/week

---

## Revised Weekly Pipeline (fully automated)

```
MONDAY
  09:00  enrich.py          — Company DB enrichment
  09:00  newsletter.py      — HTML intelligence brief

DAILY
  07:00  auto_update.py     — Signal scrape + dashboard update + push
  07:30  sync_ideas.py      — Project Ideas → In Development
  08:00  news_monitor.py    — RSS keyword alerts
  08:15  [NEW] news enrich  — Claude extracts claims from high-priority alerts
  11:00  [NEW] enrich_vault — Process any Quick Add URLs from vault

WEDNESDAY (podcast day)
  10:00  scrape_podcasts.py  — Fetch new transcripts (8 sources)
  10:30  reconcile.py        — Flag stale estimates
  10:45  [NEW] extract_claims.py --auto-pr  — Claude extracts + creates PR
  11:00  [NEW] weekly_brief.py  — Generate intelligence summary
```

**Human review points (cannot automate):**
- Approve/reject claim PRs (claims.html or GitHub PR)
- Review vault enrichments (vault.html Weekly Review tab)
- Final approval before site-data.json changes go live

---

## Implementation Priority

### Phase 1 — Ship this week (highest value, lowest risk)
1. **Add API key to cron environment** — one line in crontab
2. **Chain extract_claims.py to Wednesday cron** — one crontab entry
3. **Chain enrich_vault.py to daily cron** — one crontab entry
4. **Add both to GitHub Actions** — two new workflow files

### Phase 2 — Next week
5. **Smart news enrichment** — update news_monitor.py
6. **Auto-reconcile with proposals** — update reconcile.py

### Phase 3 — Following week
7. **Weekly intelligence brief generator** — new script
8. **Email delivery via Formspree** — webhook integration

---

## Environment Setup Required

```bash
# Add to ~/.zshrc or ~/.zprofile for local cron
export ANTHROPIC_API_KEY="sk-ant-..."

# Add to GitHub repo secrets (Settings → Secrets → Actions)
# Name: ANTHROPIC_API_KEY
# Value: sk-ant-...
```

---

## Cost Estimate

| Process | Frequency | Est. cost |
|---------|-----------|-----------|
| Claim extraction | Weekly | $0.10-0.30 |
| Vault enrichment | Per URL | $0.02-0.05 |
| News enrichment | Daily | $0.05-0.15 |
| Reconciliation proposals | Weekly | $0.02-0.05 |
| Weekly brief | Weekly | $0.05-0.10 |
| **Total** | **Monthly** | **~$8-15** |

All costs are for Claude Sonnet 4.6 at current pricing. Actual cost depends on volume of transcripts and news alerts.

---

## What Stays Manual

These require human judgement and should NOT be automated:
- Approving claims before they update site-data.json
- Setting provider ARR figures (high-stakes, needs verification)
- Editing the Sankey revenue flow model
- Adjusting COGS ratios and token estimation methodology
- Deciding which podcast sources to add/remove
