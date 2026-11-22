# CSRR-02 — Action-conditioned structural repair: source-free developer result

**Research status: MIXED_DEV_ONLY; scientific gain UNVERIFIED; native Yggdrasil unchanged.**

This contributor experiment tests whether public action-specific consequence contrasts can suppress false structural promotion under stochastic noise while retaining reversible local exceptions when a synthetic causal rule changes. It is **not** a new Yggdrasil native learner or an independently unfamiliar source family. The base `a XOR x` mechanism, possible exception grammar, and fully informed comparison classes are preprogrammed. No original-world observations or donor weights were used.

## Exact reproducibility and trial custody

- **Prereg before primary:** `4a197cad442d67744377d704abcc85803fe6e498` (tree `52087ce276639b029c8d6c77a4b274cc55f72fa3`); `study.mjs` Git blob `8a6cdfaaea26a05880021669ed76b1a90a89385c`, SHA256 `f37d1b5ea8f3b1c5fe1d064cc19dee98ff2b2f78ce27b1d617e9180d542b9458`.
- Run `node study.mjs` from this directory with Node v22 and standard library only. `result.json` records the compact primary metrics, and `provenance.json` records the SHA256 of the complete stdout. A second independent Node process generated the **same full output bytes**.
- **Invalid predecessor preserved:** `INVALID_ATTEMPT.md` details a first frozen attempt that failed on a `const` reassignment after partial synthetic observations and produced no results. New seeds 707, 808, 909 were frozen before the successful primary run; the invalid seeds were not reused as new evidence.
- Six 256-step phases A B A C A B plus a stationary all-A null sequence, three seeds; 9,216 synthetic consequences per policy. Each policy receives exactly one post-action binary outcome per step. The evaluator computes pre-action expected Brier on both possible actions in the same public context; models never receive evaluator probabilities or phase identities.

## Observed development result

| World A/B/A/C/A/B Brier (lower is better) | Mean |
|---|---:|
| Raw XOR | 0.130000 |
| New active two-action repair | 0.104861 |
| Same two-action repair with passive probes | 0.108681 |
| CSRR-01 fixed rule repair on same active observations | 0.103333 |
| Windowed Bayes on same active observations | 0.100497 |
| Fully informed symbolic exception locus, same observations | 0.099434 |
| Fully informed symbolic with always-action1 sampling, equal action count | **0.096592** |

Frozen changed-phase gain against raw **+0.060833** Brier. Old-rule-return drift **+0.015833** (limit +0.020; PASS). Stationary null false structural promotions: candidate **0**, CSRR-01 control **2**; zero cold future readout mismatches, exact action-count parity, reproducible two-Node-process bytes. The active probe policy's changed-phase edge over the passive same mechanism was **+0.004861** — below +0.005 if treated as the meaningful margin. Strong symbolic/Bayesian models are still better, and the earlier CSRR-01 method itself has a slightly lower whole-run Brier under the matched active observations.

**MIXED_DEV_ONLY:** Improved specificity in this stationary null fixture and passed the old-retention limit, but **did not** beat the strongest equal-budget comparisons. This cannot establish long-term memory, unfamiliar causal-family transfer, or native learned representations. No SCIENTIFIC_PASS or engineering promotion.

**ENGINEERING:** Focused Node execution and fresh-process reproduction PASS. Full Linux/Windows final regression and G29 are UNVERIFIED; latest GitHub push prepare workflow failed without starting jobs. **SCIENCE:** UNVERIFIED (non-native synthetic, supplied causal grammar). **DEPLOYMENT:** NONE. Protected original-source actions: zero.

**Research disposition:** Retain as a negative/partial mechanism finding. Do not tune using these consumed seeds or add further guardrail complexity in the same trial; instead qualify an independent action-consequence learning mechanism against strong matched controls if existing owner admission becomes available. [Yggdrasil source-owner issue #426](https://github.com/spoonman136668-ai/Yggdrasil/issues/426) remains original-world NO-GO. [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278) retains native coordinator scope. No merge, native checkpoint mutation, paid API, workflow dispatch, or autonomous controller modification occurred.
