# Source Intake Pipeline — Spec

**Date:** 2026-03-31
**Problem:** Simon finds sources (reports, slide decks, commentators, research firms, data providers) faster than the system can ingest them. Currently no structured way to add a new source and have the system determine extraction method, frequency, and relevance.

---

## Current State

Sources are hardcoded in scripts:
- 8 podcast RSS feeds → `scrape_podcasts.py`
- 12 PyPI/npm packages → `scrape_signals.py`
- 5 RSS news feeds → `news_monitor.py`
- Manual vault entries → `vault.html` Quick Add

**What's missing:** A single intake form where you dump a URL and the system classifies it, determines extraction method, and schedules monitoring.

---

## Source Types (what the system should handle)

| Type | Example | Extraction Method | Frequency |
|------|---------|------------------|-----------|
| **Slide deck** | State of AI Report (Google Slides) | Export as PDF/images → Claude vision or text extraction | One-time + annual recheck |
| **Research report** | ARK Invest Big Ideas, Sequoia AI 50 | Fetch HTML/PDF → Claude extraction | Annual/quarterly |
| **Commentator/analyst** | Nathan Benaich, Benedict Evans, Simon Willison | RSS/Substack feed → transcript extraction | Weekly |
| **Data provider** | Sensor Tower, SimilarWeb, Crunchbase | API or scrape → structured data | Monthly |
| **Earnings call** | MSFT, GOOG, CRM quarterly earnings | Transcript service → claim extraction | Quarterly |
| **Podcast** | Already handled (8 sources) | RSS + STT/HTML | Weekly |
| **News article** | Bloomberg, WSJ, FT, The Information | Already partially handled (news_monitor.py) | Daily |
| **Twitter/X thread** | AI researchers, VCs posting data | Thread extraction → claim extraction | Daily |
| **GitHub repo** | Model cards, benchmarks, release notes | API → structured data | Weekly |
| **Public filing** | SEC EDGAR (10-K, 10-Q, S-1) | EDGAR API → filing text → claim extraction | Quarterly |

---

## Proposed Architecture

### 1. Source Registry (`sources-registry.json`)

Every source gets an entry:

```json
{
  "id": "src-042",
  "url": "https://docs.google.com/presentation/d/1xiLl0VdrlNMAei8pmaX4ojIOfej6lhvZbOIK7Z6C-Go",
  "title": "State of AI Report 2025",
  "type": "slide_deck",
  "author": "Nathan Benaich & Ian Hogarth",
  "organization": "Air Street Capital",
  "added": "2026-03-31",
  "tags": ["research", "annual-report", "market-sizing", "model-benchmarks"],
  "extraction_method": "google_slides_export",
  "frequency": "annual",
  "next_check": "2026-10-01",
  "last_checked": null,
  "last_claims_count": 0,
  "status": "pending_first_extraction",
  "notes": "Key annual AI industry report. ~200 slides. Rich in data points."
}
```

### 2. Source Classifier (`scripts/classify_source.py`)

Given a URL, auto-determine:
- **Type:** Is it a Google Slides deck? PDF? Substack? RSS feed? GitHub? SEC filing?
- **Extraction method:** Which script/approach to use
- **Frequency:** One-time, daily, weekly, monthly, quarterly, annual
- **Relevance score:** How likely to contain dashboard-relevant data

Classification logic:
```python
URL patterns → type:
  docs.google.com/presentation → slide_deck
  docs.google.com/document → document
  *.substack.com → newsletter/blog
  arxiv.org → research_paper
  sec.gov/cgi-bin/browse-edgar → sec_filing
  github.com → github_repo
  *.pdf → pdf_report
  twitter.com/x.com → social_thread
  youtube.com → video_transcript
  RSS feed detection (try fetching, check for XML)
  Default → web_page
```

### 3. Extraction Adapters

Each source type gets an extraction adapter:

| Type | Adapter | How it works |
|------|---------|-------------|
| `slide_deck` | `extract_slides.py` | Export Google Slides as PDF → Claude vision extraction per slide, or export as text |
| `pdf_report` | `extract_pdf.py` | Download PDF → text extraction → Claude claim extraction |
| `newsletter` | Existing `scrape_podcasts.py` pattern | Fetch HTML → extract body → claim extraction |
| `web_page` | Existing `enrich_vault.py` pattern | Fetch → regex + Claude extraction |
| `rss_feed` | Add to `news_monitor.py` or `scrape_podcasts.py` | Monitor feed, extract new items |
| `sec_filing` | `extract_sec.py` | EDGAR API → filing text → focused extraction on AI revenue mentions |
| `social_thread` | `extract_thread.py` | Thread unroll → claim extraction |
| `github_repo` | Existing `enrich.py` pattern | API → stars, releases, README |

### 4. Unified Intake Form (vault.html enhancement)

Enhance the Quick Add form:

```
[URL field] ← paste any URL
[Auto-classify] ← button that hits classify_source.py
↓ shows:
  Detected type: slide_deck
  Suggested extraction: Google Slides export → Claude
  Suggested frequency: annual
  Relevance estimate: high (contains "AI", "revenue", "tokens")
  [Confirm & Add to Registry]
```

### 5. Source Monitor (`scripts/monitor_sources.py`)

Scheduled script that:
1. Reads `sources-registry.json`
2. Checks which sources are due for re-extraction (`next_check <= today`)
3. Runs the appropriate adapter
4. Saves extracted claims to `data-updates/`
5. Updates `last_checked` and `next_check`
6. Logs results

Cron: daily (checks what's due, runs extraction on due items)

---

## For the State of AI Report specifically

This is a Google Slides presentation. Two approaches:

### Approach A: Export and extract (recommended)
1. Export as PDF: `https://docs.google.com/presentation/d/{id}/export/pdf`
2. Send each page to Claude vision (or extract text from PDF)
3. Claude extracts data points per slide
4. ~200 slides × ~$0.01/slide = ~$2.00 per full extraction

### Approach B: Published HTML
- The report is also at https://www.stateof.ai/
- Fetch the HTML → extract all data points
- Cheaper but loses chart/image data

### What we'd get from State of AI:
- GPU utilisation rates and trends
- Model benchmark comparisons
- Industry revenue estimates
- Geographic distribution of AI activity
- Research paper volume and trends
- Compute cost trajectories
- Enterprise adoption survey data

---

## Implementation Priority

### Phase 1: Source Registry + Quick Classify (1 session)
- `sources-registry.json` file
- `scripts/classify_source.py` — URL → type + method + frequency
- Enhanced Quick Add form with auto-classify
- Manual extraction trigger

### Phase 2: Extraction Adapters (2 sessions)
- PDF extraction adapter (covers slide decks exported as PDF)
- Web page adapter (already exists in enrich_vault.py)
- RSS feed adapter (add new feeds to existing monitors)

### Phase 3: Automated Monitor (1 session)
- `scripts/monitor_sources.py` — daily check of registry
- Auto-extraction when sources are due
- Integration with claims pipeline

### Phase 4: Advanced Sources (2+ sessions)
- SEC EDGAR integration
- Social thread extraction
- Google Slides direct API access
- Earnings call transcript services

---

## Quick Win: Add State of AI Now

Without building the full pipeline, we can extract from the State of AI report today:

1. Fetch `https://www.stateof.ai/` HTML
2. Run through `enrich_vault.py` extraction
3. Or: download the PDF and manually add key data points to vault

The full pipeline makes this repeatable and automatic for the next 50+ sources you find.
