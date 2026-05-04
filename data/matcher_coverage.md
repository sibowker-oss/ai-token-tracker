# Matcher coverage report

_Generated 2026-05-04T23:13:00Z — wq-039_

## Summary

- **Entities**: 103/103 = 100.0%
- **Fields**:   56/56 = 100.0%

## How to add coverage

Add an entry to `data/matcher_overrides.json`:

```json
{ "entity_aliases": { "openai": ["chatgpt enterprise", "gpt"] },
  "field_synonyms": { "arr": ["annualized recurring revenue"] } }
```

Then re-run `python3 scripts/build_matcher_rules.py`.