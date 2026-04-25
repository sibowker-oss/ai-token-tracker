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
