# wq-098 hotfix — arrModel source-leak audit

_Generated_: 2026-05-08T08:52:32Z

Each row in `arrModel.apps.*` and `arrModel.compute.*` and the data
source it actually reads from. Generated on every site build by
`scripts/wq096_emit.py:emit_arrmodel`. Reconcile assertion #8
(`a_arrmodel_vault_backed`) reads this and fails if any entry
sources from a non-vault path.

## Summary

- **Total arrModel entries:** 92
- **Vault-backed (entities.json + provenance dp-id, or curated evidence file):** 68
- **Legacy fallback (dashboard.providers / topConsumers / enterpriseReality):** 24

## arrModel.apps.aiNative (44 entries)

| entity | arr ($B) | source_path | source_dp_id | vault_backed |
|---|---|---|---|---|
| OpenClaw | 0.01 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Cursor (Anysphere) | 2.0 | entities.json:financials.2026.arr | dp-148 | ✅ |
| Kilo Code | 0.008 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Perplexity | 0.5 | entities.json:financials.2026.arr | dp-195 | ✅ |
| Replit | 0.252 | entities.json:financials.2025.arr | editorial-replit-2025-arr | ✅ |
| Cognition (Devin) | 0.155 | entities.json:financials.2025.arr | editorial-cognition-(devin)-2025-arr | ✅ |
| Lovable | 0.4 | entities.json:financials.2025.arr | editorial-lovable-2025-arr | ✅ |
| Cline | 0.005 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Character.ai | 0.15 | entities.json:financials.2025.arr | editorial-characterai-2025-arr | ✅ |
| ElevenLabs | 0.33 | entities.json:financials.2025.arr | editorial-elevenlabs-2025-arr | ✅ |
| Wrtn Technologies | 0.1 | entities.json:financials.2025.arr | editorial-wrtn-technologies-2025-arr | ✅ |
| micro1 | 0.25 | entities.json:financials.2025.arr | editorial-micro1-2025-arr | ✅ |
| Midjourney | 0.3 | entities.json:financials.2025.arr | editorial-midjourney-2025-arr | ✅ |
| Harvey AI | 0.19 | entities.json:financials.2025.arr | editorial-harvey-ai-2025-arr | ✅ |
| Monica AI | 0.1 | entities.json:financials.2025.arr | editorial-monica-ai-2025-arr | ✅ |
| Jasper | 0.13 | entities.json:financials.2025.arr | editorial-jasper-2025-arr | ✅ |
| Glean | 0.1 | entities.json:financials.2025.arr | editorial-glean-2025-arr | ✅ |
| Janitor AI | 0.015 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Descript | 0.1 | entities.json:financials.2025.arr | editorial-descript-2025-arr | ✅ |
| Yellow.ai | 0.0795 | entities.json:financials.2025.arr | editorial-yellowai-2025-arr | ✅ |
| Intercom Fin | 0.05 | entities.json:financials.2025.arr | editorial-intercom-fin-2025-arr | ✅ |
| Writer | 0.1 | entities.json:financials.2025.arr | editorial-writer-2025-arr | ✅ |
| BLACKBOX.AI | 0.0317 | entities.json:financials.2025.arr | editorial-blackboxai-2025-arr | ✅ |
| Sierra AI | 0.1 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| DeepL | 0.1 | entities.json:financials.2025.arr | editorial-deepl-2025-arr | ✅ |
| Hebbia | 0.025 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Clay | 0.05 | entities.json:financials.2025.arr | editorial-clay-2025-arr | ✅ |
| Gamma | 0.1 | entities.json:financials.2025.arr | editorial-gamma-2025-arr | ✅ |
| Captions | 0.03 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Decagon | 0.05 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Mercor | 0.075 | entities.json:financials.2025.arr | editorial-mercor-2025-arr | ✅ |
| Speak | 0.05 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Synthesia | 0.1 | entities.json:financials.2025.arr | editorial-synthesia-2025-arr | ✅ |
| Genspark | 0.05 | entities.json:financials.2025.arr | editorial-genspark-2025-arr | ✅ |
| Chai Research | 0.03 | entities.json:financials.2025.arr | editorial-chai-research-2025-arr | ✅ |
| OpenArt | 0.07 | entities.json:financials.2025.arr | editorial-openart-2025-arr | ✅ |
| Abridge | 0.05 | entities.json:financials.2025.arr | editorial-abridge-2025-arr | ✅ |
| Photoroom | 0.05 | entities.json:financials.2025.arr | editorial-photoroom-2025-arr | ✅ |
| Runway | 0.1 | entities.json:financials.2025.arr | editorial-runway-2025-arr | ✅ |
| Fathom | 0.02 | entities.json:financials.2025.arr | editorial-fathom-2025-arr | ✅ |
| Pika | 0.025 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Suno | 0.12 | dashboard.topConsumers (legacy fallback) | — | ❌ legacy fallback |
| Retell AI | 0.036 | entities.json:financials.2025.arr | editorial-retell-ai-2025-arr | ✅ |
| Cal AI | 0.012 | entities.json:financials.2025.arr | editorial-cal-ai-2025-arr | ✅ |

## arrModel.apps.frontier (14 entries)

| entity | arr ($B) | source_path | source_dp_id | vault_backed |
|---|---|---|---|---|
| ByteDance | 0.0 | dashboard.providers (legacy fallback) | — | ❌ legacy fallback |
| Google/Gemini | 4.2 | entities.json:current.arr | — | ❌ legacy fallback |
| OpenAI | 25.0 | entities.json:current.arr | — | ❌ legacy fallback |
| Alibaba/Qwen | 0.5 | dashboard.providers (legacy fallback) | — | ❌ legacy fallback |
| Anthropic | 30.0 | entities.json:current.arr | — | ❌ legacy fallback |
| Tencent | 0.3 | dashboard.providers (legacy fallback) | — | ❌ legacy fallback |
| Meta | 0.0 | entities.json:current.arr | conv-meta-current-arr | ✅ |
| Baidu | 0.4 | dashboard.providers (legacy fallback) | — | ❌ legacy fallback |
| DeepSeek | 0.3 | entities.json:current.arr | — | ❌ legacy fallback |
| Minimax | 0.15 | entities.json:current.arr | — | ❌ legacy fallback |
| xAI | 0.5 | entities.json:current.arr | — | ❌ legacy fallback |
| Mistral | 0.4 | entities.json:current.arr | — | ❌ legacy fallback |
| Moonshot/Kimi | 0.1 | entities.json:current.arr | — | ❌ legacy fallback |
| Others/Self-hosted | 1.5 | dashboard.providers (legacy fallback) | — | ❌ legacy fallback |

## arrModel.apps.tradSaas (20 entries)

| entity | arr ($B) | source_path | source_dp_id | vault_backed |
|---|---|---|---|---|
| m365_copilot | 5.4 | data/evidence/enterprise_reality/*.json | — | ✅ |
| github_copilot | 1.65 | data/evidence/enterprise_reality/*.json | — | ✅ |
| google_workspace_ai | 1.5 | data/evidence/enterprise_reality/*.json | — | ✅ |
| salesforce_agentforce | 0.8 | data/evidence/enterprise_reality/*.json | — | ✅ |
| databricks_mosaic | 0.6 | data/evidence/enterprise_reality/*.json | — | ✅ |
| servicenow_now_assist | 0.6 | data/evidence/enterprise_reality/*.json | — | ✅ |
| adobe_firefly | 0.45 | data/evidence/enterprise_reality/*.json | — | ✅ |
| microsoft_dynamics_copilot | 0.4 | data/evidence/enterprise_reality/*.json | — | ✅ |
| notion_ai | 0.25 | data/evidence/enterprise_reality/*.json | — | ✅ |
| intuit_assist | 0.2 | data/evidence/enterprise_reality/*.json | — | ✅ |
| oracle_fusion_ai | 0.2 | data/evidence/enterprise_reality/*.json | — | ✅ |
| snowflake_cortex | 0.2 | data/evidence/enterprise_reality/*.json | — | ✅ |
| atlassian_intelligence | 0.15 | data/evidence/enterprise_reality/*.json | — | ✅ |
| sap_joule | 0.1 | data/evidence/enterprise_reality/*.json | — | ✅ |
| zendesk_ai | 0.1 | data/evidence/enterprise_reality/*.json | — | ✅ |
| hubspot_breeze | 0.08 | data/evidence/enterprise_reality/*.json | — | ✅ |
| box_ai | 0.05 | data/evidence/enterprise_reality/*.json | — | ✅ |
| github_advanced_security_ai | 0.05 | data/evidence/enterprise_reality/*.json | — | ✅ |
| workday_ai | 0.05 | data/evidence/enterprise_reality/*.json | — | ✅ |
| zoom_companion | 0.05 | data/evidence/enterprise_reality/*.json | — | ✅ |

## arrModel.compute.aiNativeCompute (10 entries)

| entity | arr ($B) | source_path | source_dp_id | vault_backed |
|---|---|---|---|---|
| anyscale | 0.05 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| coreweave | 6.0 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| crusoe | 0.48 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| fal_ai | 0.095 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| fireworks | 0.14 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| groq | 0.09 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| lambda_labs | 0.72 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| nebius | 1.36 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| replicate | 0.05 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |
| together_ai | 0.13 | data/evidence/compute_disclosures/aiNativeCompute/*.json | — | ✅ |

## arrModel.compute.tradCompute (4 entries)

| entity | arr ($B) | source_path | source_dp_id | vault_backed |
|---|---|---|---|---|
| aws | 15.0 | data/evidence/compute_disclosures/*.json | — | ✅ |
| azure | 37.0 | data/evidence/compute_disclosures/*.json | — | ✅ |
| gcp | 12.0 | data/evidence/compute_disclosures/*.json | — | ✅ |
| oci | 3.6 | data/evidence/compute_disclosures/*.json | — | ✅ |

