# wq-030 vault-inbox mojibake cleanup — 2026-04-29 17:33:49

Mode: WRITE
Items in inbox:        2128
Items cleaned:         101
Fields rewritten:      186
Items skipped (frozen accepted/declined): 1196
Items skipped (other status):             0

First 5 examples:

- id=auto-20260424-src-033-2 status=raw_pool
    before: '{"id": "auto-20260424-src-033-2", "claim": "Anthropic revenue was $9B at the end of 2025.", "value": 9, "unit": "USD_billions", "sourceUrl": "https://sacra.com/research/anthropic/", "sourceType": "web'
    after:  '{"id": "auto-20260424-src-033-2", "claim": "Anthropic revenue was $9B at the end of 2025.", "value": 9, "unit": "USD_billions", "sourceUrl": "https://sacra.com/research/anthropic/", "sourceType": "web'

- id=auto-20260424-src-033-3 status=raw_pool
    before: '{"id": "auto-20260424-src-033-3", "claim": "Anthropic revenue grew approximately 1,400% year-over-year as of March 2026.", "value": 1400, "unit": "percent", "sourceUrl": "https://sacra.com/research/an'
    after:  '{"id": "auto-20260424-src-033-3", "claim": "Anthropic revenue grew approximately 1,400% year-over-year as of March 2026.", "value": 1400, "unit": "percent", "sourceUrl": "https://sacra.com/research/an'

- id=auto-20260424-src-033-6 status=raw_pool
    before: '{"id": "auto-20260424-src-033-6", "claim": "Business customers account for approximately 80% of Anthropic revenue as of October 2025.", "value": 80, "unit": "percent", "sourceUrl": "https://sacra.com/'
    after:  '{"id": "auto-20260424-src-033-6", "claim": "Business customers account for approximately 80% of Anthropic revenue as of October 2025.", "value": 80, "unit": "percent", "sourceUrl": "https://sacra.com/'

- id=auto-20260424-src-033-7 status=raw_pool
    before: '{"id": "auto-20260424-src-033-7", "claim": "The number of customers spending over $100,000 annually on Claude has grown 7x in the past year.", "value": 7, "unit": "times", "sourceUrl": "https://sacra.'
    after:  '{"id": "auto-20260424-src-033-7", "claim": "The number of customers spending over $100,000 annually on Claude has grown 7x in the past year.", "value": 7, "unit": "times", "sourceUrl": "https://sacra.'

- id=auto-20260424-src-033-8 status=raw_pool
    before: '{"id": "auto-20260424-src-033-8", "claim": "Over 500 customers now spend over $1 million annually on Claude, up from a dozen two years ago.", "value": 500, "unit": "customers", "sourceUrl": "https://s'
    after:  '{"id": "auto-20260424-src-033-8", "claim": "Over 500 customers now spend over $1 million annually on Claude, up from a dozen two years ago.", "value": 500, "unit": "customers", "sourceUrl": "https://s'

---
