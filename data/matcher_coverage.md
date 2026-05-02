# Matcher coverage report

_Generated 2026-05-02T03:32:51Z — wq-039_

## Summary

- **Entities**: 92/92 = 100.0%
- **Fields**:   56/56 = 100.0%

## How to add coverage

Add an entry to `data/matcher_overrides.json`:

```json
{ "entity_aliases": { "openai": ["chatgpt enterprise", "gpt"] },
  "field_synonyms": { "arr": ["annualized recurring revenue"] } }
```

Then re-run `python3 scripts/build_matcher_rules.py`.