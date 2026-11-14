# WSP89 — CC0 source-backed factual knowledge in directly edited numeric weights

**Isolated research, NOT accepted Yggdrasil intelligence or deployment.**

This work is an expansion of WSP88 ([PR #1001](https://github.com/spoonman136668-ai/Yggdrasil/pull/1001), head `f7b7cb1d7cbb2e49e2ec20d9866bd515e043fb33`). WSP88 achieved synthetic raw-command **DEV_GROUNDING_FEASIBLE**, tied a fully trained ordinary classifier, and did not demonstrate general language understanding.

The source and scientific protocol is frozen in `prereg.json`, committed at `9d5fdc123b26fa6245361a2e493c67ea04d30a35` before any WSP89 collector or model code and before any DEV cohort. No frozen outcome or source list is rewritten to gain a positive.

## New capability under test

WSP89 reads real CC0 country claims (Wikidata QIDs, property IDs P36 capital, P37 official language, P30 continent), not invented fact names. The collector uses [Wikidata's public free MediaWiki API](https://www.wikidata.org/wiki/Wikidata:Data_access), stores the original claim/statement IDs, source entity IDs, last-revision IDs, SHA256 derivation and immutable source revision URLs in **one** repo snapshot. The authoritative answer is defined as *the captured Wikidata statement*, not as independently verified universal truth. Multiple active claims for a relation may coexist.

The writer's numeric weights hold source-backed relation support; **provenance is held in a separate explicit event ledger**. It would be false to claim citations themselves are encoded solely in learned weights. The input is externally grounded IDs; no natural-text ingestion, entity extraction, tokenizer, transformer, next-token LM, novel ontology learning or unrestricted QA occurs.

A separate independent symbolic evidence store sees identical records, and a fully trained, non-generative, one-hot multi-label sigmoid model is refit on the same authoritative observation/correction events. Any ties or conventional wins must be reported. No gradient updates occur in the candidate numerical weights.

### Frozen evaluation

Public fixtures: country QIDs from the first eight listed in preregistration. Reserved DEV first-use: the remaining sixteen country QIDs, chosen **before** source capture, without changing the source pool. Both use the **same single pinned real Wikidata snapshot**; these are not independent corpora or independent publishers.

Stage A consumes real CC0 statements and must recall the exact verified (subject, predicate) claim set with revision-pinned statements and source references. Stage B introduces clearly labeled **synthetic untrusted contradictory decoys** (not real source claims) and verifies the genuine source facts continue to win. Stage C introduces **counterfactual verified corrections** in a sandbox fork to test explicit retraction, replacement, historical cold restoration and retention of unrelated facts. These counterfactual statements are not represented as actual changes on Wikidata.

The development success label `DEV_SOURCE_KNOWLEDGE_FEASIBLE` requires all frozen criteria: 24+ source claims, perfect source-specific factual recall and revision attribution, exact symbolic parity, 100% decoy rejection and simulated correction, 100% unaffected retention, unknown abstentions, numerical cold restore, checksum/tamper and zero-weight negative controls, the conventional classifier's 99%+ training accuracy, and resource/CPU accounting. Failure must be `DEV_SOURCE_KNOWLEDGE_NEGATIVE`. Neither label implies `SCIENTIFIC_PASS`, useful open-domain reading, modern LLM-equivalent world knowledge, or lower total computational cost.

## Qualified use boundaries

```sh
# One-shot source snapshot, only through scoped source-capture CI on isolated branch:
python research/contrib/chatgpt/WSP-89/source.py --capture-once

# Public structural/real-source fixtures after source snapshot capture:
python -m unittest discover -s research/contrib/chatgpt/WSP-89 -p 'test_*.py' -v
python research/contrib/chatgpt/WSP-89/experiment.py --public-fixture-only

# Never run before dual-platform full regression and frozen source check:
python research/contrib/chatgpt/WSP-89/experiment.py --reserved-dev-first-use
```

The CI first creates the real-source dataset in a **single** source-only commit; then generates a separate three-artifact-only G29 atlas companion; then runs full inherited WSP80–WSP89 focused tests, Yggdrasil root regression and G29 on Ubuntu and Windows at the candidate SHA. A scoped one-shot reserved DEV job is conditional on *both* platforms passing, never on public fixture successes alone. No scheduled tasks, paid API, new runners, main merge, accepted ref, controller/official loop edits, protected-science first-use, deployment or ChatGPT Library files.

## Decisive next step, independent of fixture success

An unfamiliar-domain source corpus + raw unstructured prose/QA ingestion experiment, independently pre-registered and evaluated under properly trained retrieval, symbolic and neural controls, must follow. WSP89 is primarily the **provenance-and-correction foundation**. Answering facts directly observed as structured QID records does not establish unseen factual generalization.
