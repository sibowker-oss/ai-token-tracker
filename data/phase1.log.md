# Phase 1 cohort log

Append-only per GUIDELINES §5.4. Each snapshot is one block.

---

## Cohort `wq-081` snapshot — 2026-05-04T03:59:11Z

- Cohort size: **9**
- Activation rate: **11%** (1/9 active)
- Pending: **6**, error: **2**
- Total claims on first run (`last_claims_count` sum): **16**

### Coverage split

| Coverage axis | Count | Notes |
|---|---:|---|
| **entity_coverage** | 3 | Sources whose claims attach to rendered entities (entityDirectory.qualifies = true) |
| **denominator_coverage** | 6 | Macro / grid / sector — not entity-targeted |

### Routing decisions

| Routing | Count |
|---|---:|
| `telemetry-feed` | 5 |
| `vault-inbox` | 4 |

### Sources in cohort

| id | title | tier | method | type | routing | coverage | status | first-run claims |
|---|---|---:|---|---|---|---|---|---:|
| `src-025` | SEC EDGAR — AI company 10-K/10-Q/8-K scan | 1 | `sec_edgar_scan` | `sec_filing` | `telemetry-feed` | entity | `active` | 16 |
| `src-073` | CAISO — Generator Interconnection Queue | 2 | `iso_queue_caiso` | `iso_queue` | `telemetry-feed` | denominator | `error` | 0 |
| `src-074` | FRED API — St Louis Fed macro denominators | 1 | `fred_api` | `gov_api` | `vault-inbox` | denominator | `pending_credentials` | 0 |
| `src-075` | World Bank Indicators API | 1 | `worldbank_api` | `gov_api` | `vault-inbox` | denominator | `error` | 0 |
| `src-076` | ABS — Australian Bureau of Statistics SDMX API | 1 | `abs_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-077` | RBA — Reserve Bank of Australia Statistical Tables | 1 | `rba_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-078` | AEMO NEM Data Dashboard | 1 | `aemo_nem` | `iso_queue` | `telemetry-feed` | denominator | `pending_first_extraction` | 0 |
| `src-079` | GitHub REST API — repo telemetry | 1 | `github_api` | `github_repo` | `telemetry-feed` | entity | `pending_first_extraction` | 0 |
| `src-080` | Hugging Face Hub API — model registry telemetry | 1 | `huggingface_api` | `package_index` | `telemetry-feed` | entity | `pending_first_extraction` | 0 |

### Phase 1 → Phase 2 gate (brief §5a)

- Activation rate ≥ 80%? **NO** (current: 11%)
- Stale rate ≤ 20%? **NO** (current: 22%)
- Other gate criteria (4-week observation, named gaps, review-queue throughput) require post-Week-1 data and are not evaluated here.


---

## Cohort `wq-081` snapshot — 2026-05-04T04:04:51Z

- Cohort size: **9**
- Activation rate: **11%** (1/9 active)
- Pending: **6**, error: **2**
- Total claims on first run (`last_claims_count` sum): **16**

### Coverage split

| Coverage axis | Count | Notes |
|---|---:|---|
| **entity_coverage** | 3 | Sources whose claims attach to rendered entities (entityDirectory.qualifies = true) |
| **denominator_coverage** | 6 | Macro / grid / sector — not entity-targeted |

### Routing decisions

| Routing | Count |
|---|---:|
| `telemetry-feed` | 5 |
| `vault-inbox` | 4 |

### Sources in cohort

| id | title | tier | method | type | routing | coverage | status | first-run claims |
|---|---|---:|---|---|---|---|---|---:|
| `src-025` | SEC EDGAR — AI company 10-K/10-Q/8-K scan | 1 | `sec_edgar_scan` | `sec_filing` | `telemetry-feed` | entity | `active` | 16 |
| `src-073` | CAISO — Generator Interconnection Queue | 2 | `iso_queue_caiso` | `iso_queue` | `telemetry-feed` | denominator | `error` | 0 |
| `src-074` | FRED API — St Louis Fed macro denominators | 1 | `fred_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-075` | World Bank Indicators API | 1 | `worldbank_api` | `gov_api` | `vault-inbox` | denominator | `error` | 0 |
| `src-076` | ABS — Australian Bureau of Statistics SDMX API | 1 | `abs_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-077` | RBA — Reserve Bank of Australia Statistical Tables | 1 | `rba_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-078` | AEMO NEM Data Dashboard | 1 | `aemo_nem` | `iso_queue` | `telemetry-feed` | denominator | `pending_first_extraction` | 0 |
| `src-079` | GitHub REST API — repo telemetry | 1 | `github_api` | `github_repo` | `telemetry-feed` | entity | `pending_first_extraction` | 0 |
| `src-080` | Hugging Face Hub API — model registry telemetry | 1 | `huggingface_api` | `package_index` | `telemetry-feed` | entity | `pending_first_extraction` | 0 |

### Phase 1 → Phase 2 gate (brief §5a)

- Activation rate ≥ 80%? **NO** (current: 11%)
- Stale rate ≤ 20%? **NO** (current: 22%)
- Other gate criteria (4-week observation, named gaps, review-queue throughput) require post-Week-1 data and are not evaluated here.


---

## Cohort `wq-081` snapshot — 2026-05-04T07:37:48Z

- Cohort size: **9**
- Activation rate: **11%** (1/9 active)
- Pending: **6**, error: **2**
- Total claims on first run (`last_claims_count` sum): **16**

### Coverage split

| Coverage axis | Count | Notes |
|---|---:|---|
| **entity_coverage** | 3 | Sources whose claims attach to rendered entities (entityDirectory.qualifies = true) |
| **denominator_coverage** | 6 | Macro / grid / sector — not entity-targeted |

### Routing decisions

| Routing | Count |
|---|---:|
| `telemetry-feed` | 5 |
| `vault-inbox` | 4 |

### Sources in cohort

| id | title | tier | method | type | routing | coverage | status | first-run claims |
|---|---|---:|---|---|---|---|---|---:|
| `src-025` | SEC EDGAR — AI company 10-K/10-Q/8-K scan | 1 | `sec_edgar_scan` | `sec_filing` | `telemetry-feed` | entity | `active` | 16 |
| `src-073` | CAISO — Generator Interconnection Queue | 2 | `iso_queue_caiso` | `iso_queue` | `telemetry-feed` | denominator | `error` | 0 |
| `src-074` | FRED API — St Louis Fed macro denominators | 1 | `fred_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-075` | World Bank Indicators API | 1 | `worldbank_api` | `gov_api` | `vault-inbox` | denominator | `error` | 0 |
| `src-076` | ABS — Australian Bureau of Statistics SDMX API | 1 | `abs_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-077` | RBA — Reserve Bank of Australia Statistical Tables | 1 | `rba_api` | `gov_api` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-078` | AEMO NEM Data Dashboard | 1 | `aemo_nem` | `iso_queue` | `telemetry-feed` | denominator | `pending_first_extraction` | 0 |
| `src-079` | GitHub REST API — repo telemetry | 1 | `github_api` | `github_repo` | `telemetry-feed` | entity | `pending_first_extraction` | 0 |
| `src-080` | Hugging Face Hub API — model registry telemetry | 1 | `huggingface_api` | `package_index` | `telemetry-feed` | entity | `pending_first_extraction` | 0 |

### Phase 1 → Phase 2 gate (brief §5a)

- Activation rate ≥ 80%? **NO** (current: 11%)
- Stale rate ≤ 20%? **NO** (current: 22%)
- Other gate criteria (4-week observation, named gaps, review-queue throughput) require post-Week-1 data and are not evaluated here.


---

## Cohort `wq-083` snapshot — 2026-05-04T10:56:53Z

- Cohort size: **11**
- Activation rate: **0%** (0/11 active)
- Pending: **11**, error: **0**
- Total claims on first run (`last_claims_count` sum): **0**

### Coverage split

| Coverage axis | Count | Notes |
|---|---:|---|
| **entity_coverage** | 11 | Sources whose claims attach to rendered entities (entityDirectory.qualifies = true) |
| **denominator_coverage** | 0 | Macro / grid / sector — not entity-targeted |

### Routing decisions

| Routing | Count |
|---|---:|
| `vault-inbox` | 11 |

### Sources in cohort

| id | title | tier | method | type | routing | coverage | status | first-run claims |
|---|---|---:|---|---|---|---|---|---:|
| `src-016` | OpenAI Newsroom | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-081` | Anthropic News | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-082` | Google DeepMind Blog | 2 | `web_extract` | `web_page` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-083` | Meta AI Blog | 2 | `web_extract` | `web_page` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-084` | Mistral AI News | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-085` | Microsoft AI Blog | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-086` | AWS What's New + ML Blog | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-087` | Google Cloud AI Blog | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-088` | One Useful Thing (Ethan Mollick) | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-089` | Marcus on AI (Gary Marcus) | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-090` | Import AI (Jack Clark) | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |

### Phase 1 → Phase 2 gate (brief §5a)

- Activation rate ≥ 80%? **NO** (current: 0%)
- Stale rate ≤ 20%? **YES** (current: 0%)
- Other gate criteria (4-week observation, named gaps, review-queue throughput) require post-Week-1 data and are not evaluated here.


---

## Cohort `wq-083` snapshot — 2026-05-04T21:29:32Z

- Cohort size: **11**
- Activation rate: **0%** (0/11 active)
- Pending: **11**, error: **0**
- Total claims on first run (`last_claims_count` sum): **0**

### Coverage split

| Coverage axis | Count | Notes |
|---|---:|---|
| **entity_coverage** | 8 | Sources whose claims attach to rendered entities (entityDirectory.qualifies = true) |
| **denominator_coverage** | 1 | Macro / grid / sector / infra — not entity-targeted |
| **cross_cutting_coverage** | 2 | Commentary / framing without a single entity target (adoption_signal, sceptic_anchor, capex_finance, etc.) |

### Routing decisions

| Routing | Count |
|---|---:|
| `vault-inbox` | 11 |

### Sources in cohort

| id | title | tier | method | type | routing | coverage | status | first-run claims |
|---|---|---:|---|---|---|---|---|---:|
| `src-016` | OpenAI Newsroom | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-081` | Anthropic News | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-082` | Google DeepMind Blog | 2 | `web_extract` | `web_page` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-083` | Meta AI Blog | 2 | `web_extract` | `web_page` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-084` | Mistral AI News | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-085` | Microsoft AI Blog | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-086` | AWS What's New + ML Blog | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | denominator | `pending_first_extraction` | 0 |
| `src-087` | Google Cloud AI Blog | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |
| `src-088` | One Useful Thing (Ethan Mollick) | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | cross-cutting | `pending_first_extraction` | 0 |
| `src-089` | Marcus on AI (Gary Marcus) | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | cross-cutting | `pending_first_extraction` | 0 |
| `src-090` | Import AI (Jack Clark) | 2 | `rss_feed` | `rss_feed` | `vault-inbox` | entity | `pending_first_extraction` | 0 |

### Phase 1 → Phase 2 gate (brief §5a)

- Activation rate ≥ 80%? **NO** (current: 0%)
- Stale rate ≤ 20%? **YES** (current: 0%)
- Other gate criteria (4-week observation, named gaps, review-queue throughput) require post-Week-1 data and are not evaluated here.


---

