# NKR-01 — Bounded native causal relationships, non-duplicating intake

**Scope:** optional native Yggdrasil developmental extension; **not** an automatic write to the accepted model checkpoint or a source of authority. Preregistration first commit `a0c72c0651b5c281e5b6f167f0b1b63b41ba611c` before any new code or tests. Base Yggdrasil main `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Inherited `PublicCausalCells` maintains its 16 addresses, seven active/nine retained and 164-byte YPC1 snapshot.

## Real native connection

`yggdrasil/native_relation_memory.py` adds `NativeRelationMemory`, which programs ten exact float32 synapses in each of **at most 16 already-addressed native slots** from `observe_public(address, context, action, outcome, source_ref, retained=...)`. The direct weight program is an exact GF(2) parity model over four binary contextual variables, an action and their interactions. It uses deterministic online elimination, **no gradient, tokenization, transformer, trained frontier-model output or hidden scientific labels**. Unidentified predictions abstain.

`PublicCausalCells.choose_contextual(address, context, bank, retained=...)` is the same native decision path with explicit opt-in. It chooses a context-specific action only when **both actions are identifiable from public evidence and have different observed-consequence predictions**. Otherwise it executes the unchanged `choose()` baseline. Legacy `observe`, `choose`, `choose_wilson`, observed contrast, 164-byte snapshot and restore are unchanged.

**Relation deduplication:** one canonical (native slot, four-bit context, action) key per real deterministic observed consequence, regardless of source-ref alias or repeat; repeated same evidence is a strict no-op with **identical checkpoint bytes**, different-outcome duplicates and inconsistent consequences reject atomically. Identical numeric weight profiles across addresses are interned once in memory; separate address-bound evidence is not incorrectly collapsed. The opt-in relation checkpoint is separate, bounded, versioned and SHA256-protected with cold replay. **Source refs are provenance labels, not proofs of truth**: only a trusted upstream environment can supply actual observation consequences. Arbitrary coefficients or inferred hidden test outcomes cannot be imported as public observations.

## Fabricated-only qualification and limits

The preregistered test uses the same ten publicly observed action/consequence samples per native slot (160 samples across 16 addresses) for old native `PublicCausalCells.choose` and contextual readout. Unseen context states `3,5,6,7,9,10,11,12,13,14,15` across all 16 native slots give 176 prospective choices. Gate: at least 20 percentage-point improvement in actual public deterministic consequences while keeping the old methods and checkpoint exactly unchanged. Negative controls cover duplicate imports, cross-source duplication, conflicting or algebraically inconsistent evidence, unidentifiable action comparisons, wrong source/addresses, checkpoint integrity, cold restoration and a hard 512-unique-event upper bound. **This is DEV source-grammar feasibility, not scientific proof of general native learning or advantage over a trained gradient-based comparison**.

```
python -m unittest discover -s tests -p test_native_relation_memory.py -v
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/build_code_atlas.py --check-if-present
```

**Merge decision:** even if this opt-in mechanism passes exact-source dual-OS regression, no real learned Yggdrasil knowledge has been promoted. To activate it as a model capability, separately accept a trusted environment evidence-ingestion producer, compare cold-retention/cost on independently held-out native tasks against strongest matched controls, verify no duplication and no degradation of incumbent model decisions, and separately authorize accepted-state promotion. Never copy WSP114/115 world-specific experimental weights into different-semantic YPC1 counts. FKP-01's separate 128-concept priming research is not a substitute and is not edited by this PR.

**No scope expansion:** Yggdrasil only. No Wingless/Hybrid/FORGE, CKB controller, scheduling, native runner, private source, original WSP115 first-use, paid API, model acceptance or deployment changes.

## Fabricated-source fixture verification

Both GitHub-hosted Windows 2022 and Ubuntu focused NKR-01 tests, incumbent causal-cells/Wilson tests, and exact preregistration were **SUCCESS** at `4dee776c2b5e8b05dc98a61e89320865330ee12c`, [run #43711589118](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/43711589118). This is pre-acceptance DEV evidence only. Final exact-source qualification and independent G29 both operating systems remain mandatory.

### Exact-source independent G29 hygiene repair

First exact-source final regression passed on **both** Linux and Windows at `4355c555872115aa8ea4899567bfae6accef9ad3`, but independent G29 failed at the final `git status --porcelain` cleanliness check **after all four atlas tests passed** on both OS. Root cause is this independent job did not disable Python bytecode, unlike its passing final-regression counterpart. Workflow-only fix `83acfb3a0228c3a0b619b807e7504b8a6957a9ec` exports `PYTHONDONTWRITEBYTECODE=1` and `PYTHONHASHSEED=0` for all jobs. No learner or test outcome was modified; requalification on a newly pinned complete exact source is mandatory. The failed receipts remain recorded; no merge or scientific acceptance.
