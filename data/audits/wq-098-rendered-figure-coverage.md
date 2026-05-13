# wq-098 hotfix follow-up — rendered-figure vault coverage

_Generated_: 2026-05-12T22:43:42Z

Every numeric figure rendered on `usage.html` (and its source). Generated on every site build by `scripts/wq096_emit.py` and read by reconcile assertion #9 (`a_rendered_figure_coverage`).

**Backing categories:**
- `vault` — the entity has provenance pointing at a `dp-NNN` vault id.
- `entities (no provenance)` — entity has the value but provenance is missing (likely set pre-apply-pipeline; flagged for review).
- `evidence` — sourced from `data/evidence/*` curated files (intentional for trad-SaaS claimed-vs-real).
- `legacy fixture` — value from a hardcoded site-data.json seed or `wq096_tagging.json` backfill (no entity record exists, or the entity has no `arr` field populated).
- `no value` — row has no figure at all.

## Summary

- **entities (no provenance)**: 8 rows
- **evidence**: 20 rows
- **legacy fixture**: 17 rows
- **no value**: 12 rows
- **vault**: 34 rows
- **Total**: 91 rows
- **Rows with rendered ↔ entity gap**: 1

## Rows where rendered figure diverges from entities.json

| block | entity | rendered ($B) | entity arr ($B) | gap ($B) | backing |
|---|---|---|---|---|---|
| dashboard.enterpriseReality | salesforce_agentforce | 0.8 | 0.3 | 0.5 | evidence |

## dashboard.providers (14 rows)

| entity | rendered ($B) | entity arr ($B) | dp-id | backing | gap ($B) |
|---|---|---|---|---|---|
| ByteDance | 0.0 | None | — | legacy fixture | — |
| Google/Gemini | 4.2 | 4.2 | — | entities (no provenance) | — |
| OpenAI | 25.0 | 25.0 | — | entities (no provenance) | — |
| Alibaba/Qwen | 0.5 | None | — | legacy fixture | — |
| Anthropic | 30.0 | 30.0 | — | entities (no provenance) | — |
| Tencent | 0.3 | None | — | legacy fixture | — |
| Meta | 0.0 | 0.0 | conv-meta-current-arr | vault | — |
| Baidu | 0.4 | None | — | legacy fixture | — |
| DeepSeek | 0.3 | 0.3 | — | entities (no provenance) | — |
| Minimax | 0.15 | 0.15 | — | entities (no provenance) | — |
| xAI | 0.5 | 0.5 | — | entities (no provenance) | — |
| Mistral | 0.4 | 0.4 | — | entities (no provenance) | — |
| Moonshot/Kimi | 0.1 | 0.1 | — | entities (no provenance) | — |
| Others/Self-hosted | 1.5 | None | — | legacy fixture | — |

## dashboard.topConsumers (57 rows)

| entity | rendered ($B) | entity arr ($B) | dp-id | backing | gap ($B) |
|---|---|---|---|---|---|
| Portkey.ai | None | None | — | no value | — |
| OpenClaw | 0.01 | None | — | legacy fixture | — |
| Cursor (Anysphere) | 2.0 | 2.0 | dp-148 | vault | — |
| OpenRouter | 0.0175 | None | — | legacy fixture | — |
| Kilo Code | 0.008 | None | — | legacy fixture | — |
| Perplexity | 0.5 | 0.5 | dp-195 | vault | — |
| Replit | 0.252 | 0.252 | editorial-replit-2025-arr | vault | — |
| Cognition (Devin) | 0.155 | 0.155 | editorial-cognition-(devin)-2025-arr | vault | — |
| Duolingo | None | None | — | no value | — |
| Lovable | 0.4 | 0.4 | editorial-lovable-2025-arr | vault | — |
| Canva | None | None | — | no value | — |
| Cline | 0.005 | None | — | legacy fixture | — |
| Character.ai | 0.15 | 0.15 | editorial-characterai-2025-arr | vault | — |
| ElevenLabs | 0.33 | 0.33 | editorial-elevenlabs-2025-arr | vault | — |
| Wrtn Technologies | 0.1 | 0.1 | editorial-wrtn-technologies-2025-arr | vault | — |
| micro1 | 0.25 | 0.25 | editorial-micro1-2025-arr | vault | — |
| Midjourney | 0.3 | 0.3 | editorial-midjourney-2025-arr | vault | — |
| Harvey AI | 0.19 | 0.19 | editorial-harvey-ai-2025-arr | vault | — |
| Monica AI | 0.1 | 0.1 | editorial-monica-ai-2025-arr | vault | — |
| Jasper | 0.13 | 0.13 | editorial-jasper-2025-arr | vault | — |
| Glean | 0.1 | 0.1 | editorial-glean-2025-arr | vault | — |
| Janitor AI | 0.015 | None | — | legacy fixture | — |
| Descript | 0.1 | 0.1 | editorial-descript-2025-arr | vault | — |
| Yellow.ai | 0.0795 | 0.0795 | editorial-yellowai-2025-arr | vault | — |
| Intercom Fin | 0.05 | 0.05 | editorial-intercom-fin-2025-arr | vault | — |
| Writer | 0.1 | 0.1 | editorial-writer-2025-arr | vault | — |
| BLACKBOX.AI | 0.0317 | 0.0317 | editorial-blackboxai-2025-arr | vault | — |
| Klarna | None | None | — | no value | — |
| Grab | None | None | — | no value | — |
| Sea/Shopee | None | None | — | no value | — |
| Kakao | None | None | — | no value | — |
| Sierra AI | 0.1 | None | — | legacy fixture | — |
| DeepL | 0.1 | 0.1 | editorial-deepl-2025-arr | vault | — |
| Hebbia | 0.025 | None | — | legacy fixture | — |
| Clay | 0.05 | 0.05 | editorial-clay-2025-arr | vault | — |
| Gamma | 0.1 | 0.1 | editorial-gamma-2025-arr | vault | — |
| Roo Code | None | None | — | no value | — |
| Captions | 0.03 | None | — | legacy fixture | — |
| Decagon | 0.05 | None | — | legacy fixture | — |
| Luminance | None | None | — | no value | — |
| Mercor | 0.075 | 0.075 | editorial-mercor-2025-arr | vault | — |
| Speak | 0.05 | None | — | legacy fixture | — |
| Synthesia | 0.1 | 0.1 | editorial-synthesia-2025-arr | vault | — |
| Genspark | 0.05 | 0.05 | editorial-genspark-2025-arr | vault | — |
| Chai Research | 0.03 | 0.03 | editorial-chai-research-2025-arr | vault | — |
| OpenArt | 0.07 | 0.07 | editorial-openart-2025-arr | vault | — |
| SillyTavern | None | None | — | no value | — |
| Abridge | 0.05 | 0.05 | editorial-abridge-2025-arr | vault | — |
| Photoroom | 0.05 | 0.05 | editorial-photoroom-2025-arr | vault | — |
| Runway | 0.1 | 0.1 | editorial-runway-2025-arr | vault | — |
| Agent Zero | None | None | — | no value | — |
| Fathom | 0.02 | 0.02 | editorial-fathom-2025-arr | vault | — |
| Pika | 0.025 | None | — | legacy fixture | — |
| Suno | 0.12 | None | — | legacy fixture | — |
| Retell AI | 0.036 | 0.036 | editorial-retell-ai-2025-arr | vault | — |
| OpenHands | None | None | — | no value | — |
| Cal AI | 0.012 | 0.012 | editorial-cal-ai-2025-arr | vault | — |

## dashboard.enterpriseReality (20 rows)

| entity | rendered ($B) | entity arr ($B) | dp-id | backing | gap ($B) |
|---|---|---|---|---|---|
| m365_copilot | 5.4 | None | — | evidence | — |
| github_copilot | 1.65 | 1.65 | editorial-github-copilot-2025-arr | evidence | — |
| google_workspace_ai | 1.5 | None | — | evidence | — |
| salesforce_agentforce | 0.8 | 0.3 | editorial-salesforce-agentforce-2025-arr | evidence | 0.5 |
| databricks_mosaic | 0.6 | None | — | evidence | — |
| servicenow_now_assist | 0.6 | None | — | evidence | — |
| adobe_firefly | 0.45 | None | — | evidence | — |
| microsoft_dynamics_copilot | 0.4 | None | — | evidence | — |
| notion_ai | 0.25 | None | — | evidence | — |
| intuit_assist | 0.2 | None | — | evidence | — |
| oracle_fusion_ai | 0.2 | None | — | evidence | — |
| snowflake_cortex | 0.2 | None | — | evidence | — |
| atlassian_intelligence | 0.15 | None | — | evidence | — |
| sap_joule | 0.1 | None | — | evidence | — |
| zendesk_ai | 0.1 | None | — | evidence | — |
| hubspot_breeze | 0.08 | None | — | evidence | — |
| box_ai | 0.05 | None | — | evidence | — |
| github_advanced_security_ai | 0.05 | None | — | evidence | — |
| workday_ai | 0.05 | None | — | evidence | — |
| zoom_companion | 0.05 | None | — | evidence | — |

