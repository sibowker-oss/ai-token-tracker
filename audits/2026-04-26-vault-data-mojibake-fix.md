# fix_vault_data_mojibake.py — vault-data.json

date: 2026-04-26 08:14:45
target: vault-data.json
field changes: 78
items touched: 39

First 5 examples:

- dataPoints[147].sourceAuthor (id=dp-148, passes=1)
    before: 'Sacra â\x80\x94 Cursor Deep Dive'
    after:  'Sacra — Cursor Deep Dive'

- dataPoints[147].notes (id=dp-148, passes=1)
    before: 'From Sacra â\x80\x94 Cursor Deep Dive'
    after:  'From Sacra — Cursor Deep Dive'

- dataPoints[148].sourceAuthor (id=dp-149, passes=1)
    before: 'Sacra â\x80\x94 Cursor Deep Dive'
    after:  'Sacra — Cursor Deep Dive'

- dataPoints[148].notes (id=dp-149, passes=1)
    before: 'From Sacra â\x80\x94 Cursor Deep Dive'
    after:  'From Sacra — Cursor Deep Dive'

- dataPoints[149].sourceAuthor (id=dp-150, passes=1)
    before: 'Sacra â\x80\x94 Cursor Deep Dive'
    after:  'Sacra — Cursor Deep Dive'

---
# fix_vault_data_mojibake.py — data-updates/archive/review-decisions-2026-04-25-wq027-replay.json

date: 2026-04-26 08:16:12
target: data-updates/archive/review-decisions-2026-04-25-wq027-replay.json
field changes: 78
items touched: 39

First 5 examples:

- accepted[0].sourceAuthor (id=auto-20260424-src-035-1, passes=1)
    before: 'Sacra â\x80\x94 Cursor Deep Dive'
    after:  'Sacra — Cursor Deep Dive'

- accepted[0].notes (id=auto-20260424-src-035-1, passes=1)
    before: 'From Sacra â\x80\x94 Cursor Deep Dive'
    after:  'From Sacra — Cursor Deep Dive'

- accepted[1].sourceAuthor (id=auto-20260424-src-035-2, passes=1)
    before: 'Sacra â\x80\x94 Cursor Deep Dive'
    after:  'Sacra — Cursor Deep Dive'

- accepted[1].notes (id=auto-20260424-src-035-2, passes=1)
    before: 'From Sacra â\x80\x94 Cursor Deep Dive'
    after:  'From Sacra — Cursor Deep Dive'

- accepted[2].sourceAuthor (id=auto-20260424-src-035-3, passes=1)
    before: 'Sacra â\x80\x94 Cursor Deep Dive'
    after:  'Sacra — Cursor Deep Dive'

---
