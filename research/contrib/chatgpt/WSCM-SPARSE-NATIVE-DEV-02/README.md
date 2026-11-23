# WSCM-SPARSE-NATIVE-DEV-02 — opt-in v9 public causal-operator hypotheses

**Status:** UNPREREGISTERED EXPLORATORY ENGINEERING; no protected science and no deployment.

## Change and custody

Detached successor of WSCM-SPARSE-OPERATOR-DEV-01 commit `0634b632a007037cfeff2d60d4ce40f2f6f6fa14`, which itself is a child of qualified draft PR #1364 HEAD `1820b383f43164bf064214cd09cf26a59274f2ff` (tree `06da41d15795ee15dc9d5d75c3a5f253ba543c02`). The active PR ref is *not* advanced by this candidate.

This adds **one bounded native-package passive evidence component**, a new optional `v9-sparse-dev` checkpoint envelope on the **existing** `NativeEpisodeExperience`, and small forwarding methods on **existing** `NativeCumulativeLearner`. The baseline binary counter/forecast/plan and previous v1-v8 checkpoint semantics are intended to remain byte-identical when unused. No extra owner, actor, scheduler, controller, or Genome write.

## Native contract

- Only canonical `engineering_fixture_only` disclosed bytes, SHA256 integrity, and strict four-bit public view / opaque external action ID / binary outcome may be admitted.
- Max 256 rows, 32 action IDs, 64 KiB evidence checkpoint, 160 KiB combined native envelope; atomic capacity rejection, immutable copies, source-ID replay conflict refusal.
- A 114-model finite Boolean family of at most **two** public parents is a **supplied prior grammar**, not self-invented physics. The source-free new readout filters hypotheses by witnessed outcomes and returns `HYPOTHESIS_WITHIN_GRAMMAR`, `ABSTAIN`, `CONTRADICTION`, or `OUT_OF_GRAMMAR`. Never call a hypothesis source-certified or actionable.
- v9 checkpoint binds the native v1-v8 sub-checkpoint and sparse evidence sub-checkpoint with separate SHA256 digests; rejects nested self-envelopes, rehashed tampering, positive acceptance flags, and noncanonical bytes.
- Four-way AND after 15 zero witnesses is a **known out-of-family false prediction**: a unanimous sparse-zero forecast predicts zero at (1,1,1,1) while the true interaction outputs one. Do not confuse grammar-conditioned unanimity with universal causal induction.
- The fixture does **not** update causal counters, use real source interventions, learn hidden role names, charge or authorize a physical probe, promote models, or confer scientific first-use. Source owner issue #426 remains HOLD.

## Measured development tests

On isolated local Linux CPython 3.13.5, the exact newly added native evidence module and matching `tests/test_native_sparse_operator_evidence.py` passed **12/12** unit tests normally and **12/12** under `-O`. Both source and test files are exact-byte Git-blob matched (native `1fda97c9a3c53e32d0be880353bda2ce02b32237`, test `0a427227c6e418c37e9e0586b470473e9c8089b3`).

The additional original-native integration tests `tests/test_native_sparse_operator_integration.py` were **syntax-compiled locally**, but **NOT EXECUTED** against the complete original source/dependency tree. They target v1 legacy parity, opt-in v9 cold restore, nested v7/v8/v9 coexistence, tampered receipts, source replay, negative controls and cumulative method presence. Do not equate syntax validation or 12/12 isolated component tests with original-native integration success.

Reproduction once the exact candidate is checked out by a qualified runner:

```
python -B -m unittest discover -s tests -p test_native_sparse_operator_evidence.py -v
python -B -m unittest discover -s tests -p test_native_sparse_operator_integration.py -v
python -B -m unittest discover -s tests -p test_wscm_native_grid5_dev.py -v
python -B -m unittest discover -s tests -p test_native_episode_external_fixture_envelope.py -v
# Mandatory candidate-final complete tests/ plus research suites on Linux and Windows
```

No runner was dispatched and no generated G29 artifact was changed. **The prior full dual-OS + G29 PASS belongs only to exact original PR head `1820b383`, NOT to this new detached integration candidate.** No source-owner acceptance or protected trial is authorized.

## Gate results

ENGINEERING: isolated module **12/12 normal and 12/12 -O PASS**; integration **UNVERIFIED**; final candidate dual-OS regression, G29 and memory/performance qualification **UNVERIFIED**. This is a provisional implementation only.

SCIENTIFIC: unpreregistered development-only; no held novel law, equal-information matched Bayesian/symbolic comparator, independent qualification, retention advantage, or charged intervention. **SCIENTIFIC_GAIN_VERIFIED=false**.

DEPLOYMENT: no accepted `main`, active #1364 ref, source-owner actor, production device, Genome, merges, workflows or paid APIs modified. **NONE**.
