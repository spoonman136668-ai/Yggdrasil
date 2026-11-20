# ENERGY-60 — Learned latent-state causal memory versus conventional softmax retrieval

**Date:** 2026-11-19. **Frozen decision: SCREEN_NO_GO (4/10 gates PASS; all four critical gates FAIL).** This is **external synthetic research**, not native Yggdrasil training, scientific acceptance, production, or promotion.

## Source, preregistration, and prospective ordering

Previous draft PR #1210 HEAD was `c430f446ffef6326664a8719c6883422d19637c3`. Source+independent auditor committed as **`dff08e665d4851128e9e5bb0846dc1179ca196d1`**; separate `prereg.json` at **`a91e153fc62a024e0059e0d9354a35c2a8397507`** before any 997601/997619 scoring. Source tar SHA-256: `af7abf7b3d2e6a4586ba1a21ca9a458d8695eea3c30cf253bd6f57992a137120`; scorer `a7e94c276fd4c4b5ba17f1f239990572c3f0118b7720fab7d1ff340d1be2dc56`; auditor `5dd892881b35444e317260726c14151a4062d8dc516684012177865525d02b34`. Excluded development-only seed **999701**, three worlds, was scored before freeze to check code, with 35,102 independent refit checks PASS; it is not a prospective result.

**Prospective screen**: seeds **997601 and 997619**, four world IDs x three families = **24** synthetic worlds. Three reserved primary seeds **102101,102119,102137 have not been scored**. The frozen critical screen gates failed, so primary execution was **stopped**.

## Method: is a latent-state codebook valuable?

The synthetic generator hides three consecutive response regimes behind chronological raw (action, consequence) observations, without regime IDs or changepoint markers. Each world has nine causal action bits, three observed nuisance cues whose correlations shift, and previously unseen 4-bit parity or 5-bit majority-threshold effects in regime C. Observed factors in the fitted models are deliberately limited to the older authored 286-dimensional pair/triple parity grammar; high-order hidden mechanisms exceed that linear feature span. All underlying causal action assignments are unique across training, calibration and held evaluation.

Every arm gets the same chronological stream (68–84 witnesses per regime), *the same 12 labeled probe interventions per queried regime*, and 52 separate withheld A/B/C probes. Thus this is **few-shot context retrieval**, not zero-calibration regime recognition. The proposed method clusters overlapping fitted OMP4 causal-snapshot predictions on 40 fixed unlabeled action designs to learn three latent prototypes, estimates state-to-state transitions from their chronological assignments, and applies a Markov prior to calibrated state weights. The cluster count, numerical solver and operator grammar are authored, not invented autonomously. **Conventional softmax retrieval uses the identical original snapshots and probe outcomes**, and prototype-softmax without temporal filtering isolates the transition mechanism. Fully fitted ElasticNet/KRR models and no-memory/shuffled controls provide additional baselines.

## Original screen scores (pooled A/B/C MSE, lower better)

| Arm | Held MSE |
|---|---:|
| `softmax_memory` | 0.842169 |
| `best_snapshot` | 0.921184 |
| `state_filter` | 1.249331 |
| `prototype_softmax` | 1.270297 |
| `pooled_elasticnet` | 2.449655 |
| `pooled_krr` | 3.021137 |
| `random_snapshot` | 3.197155 |
| `recent_elasticnet` | 3.428135 |
| `shuffled_probes` | 3.859874 |
| `last_snapshot` | 4.251301 |

**Candidate state filter = 1.249331; conventional softmax = 0.842169.** The candidate has **48.35% HIGHER error** than the strongest same-snapshot conventional control; it only improves on uniform-prior prototype retrieval by **1.65%**, below the frozen 5% condition. For cold C, candidate 2.461872 versus softmax 2.257587 (9.05% worse).

### Independent seed cohorts

| Fresh seed | Latent state MSE | Conventional softmax MSE |
|---|---:|---:|
| 997601 | 1.091155 | 0.648873 |
| 997619 | 1.407507 | 1.035466 |

### Distinct mechanism families

| Family | Latent state MSE | Conventional softmax MSE |
|---|---:|---:|
| novel_threshold | 2.134999 | 1.472496 |
| return_middle | 0.734238 | 0.500626 |
| return_old | 0.878755 | 0.553386 |

The temporal prior *did* affect retrieval: it changed the posterior by L1 >0.01 on **12.50%** of second/third query sessions. That crosses the frozen 10% exercise threshold, but does not establish benefit.

## Frozen gates: 4 pass / 6 fail

| Gate | Result | Prespecified test |
|---|---|---|
| `all_families_noninferior_10pct` | **FAIL** | state_filter pooled MSE <=1.10x softmax_memory pooled MSE on EACH family |
| `both_seed_positive_vs_softmax` | **FAIL** | state_filter pooled held MSE strictly lower than softmax_memory for BOTH screen seeds |
| `cold_C_gain5_vs_softmax` | **FAIL** | state_filter C held MSE <=0.95 * softmax_memory C held MSE |
| `historical_A_noninferior_5pct` | **FAIL** | state_filter held A MSE <=1.05x softmax_memory A held MSE |
| `independent_audit` | PASS | Every world, latent memory snapshot, transition, all 10 trained predictors, held predictions and aggregate scores pass auditor; unchanged-source semantic replay matches. |
| `last_snapshot_gain20pct` | PASS | state_filter pooled MSE <=0.80x last_snapshot pooled MSE |
| `negative_shuffled_20pct` | PASS | state_filter pooled MSE <=0.80x shuffled_probes pooled MSE |
| `pooled_gain5_vs_prototype` | **FAIL** | state_filter pooled MSE <=0.95 * prototype_softmax pooled MSE (isolates temporal effect) |
| `pooled_gain5_vs_softmax` | **FAIL** | state_filter pooled A/B/C MSE <=0.95 * softmax_memory pooled MSE |
| `temporal_prior_exercised` | PASS | At least 10 percent of second/third query posterior vectors differ by >0.01 L1 from uniform-prior prototype posteriors |

All four critical benefit gates failed; under the frozen decision rule, classification is **SCREEN_NO_GO**, not provisional GO or SCIENTIFIC_PASS. No parameters, seeds, controls or thresholds were tuned after the outcomes. Primary was not run.

## Audit, exact replay and integrity

Original score SHA-256 `23523f539818bd1f0f449083ec282a303e84119f87c6a65cd90f595de4871edf`. Independent non-importing auditor refitted all latent prototypes, empirical transitions, historical snapshots, ten arms and prediction vectors, checked disjoint underlying action assignments, held response-function consistency and every aggregate: **PASS 286,552 checks across 24 worlds**. Same-source deterministic replay passed all numerical and state fields exactly, excluding `elapsed_seconds` and `cases[*].fit.seconds_fit_predict`; its semantic SHA-256 is `5cd4941bae196e1af3e9d8161332965178c512d204b31897808d50dd75948584`. This replay is **not** another independent sample.

Audit shares NumPy/scikit-learn with the scorer and relies on the disclosed score-world noise rather than reproducing a wholly independent environment. The 286-feature authored grammar does not permit general new-operator discovery. CPU scorer time of 6.296 seconds for 24 worlds excludes audit/replay/packaging/CI and is not electricity usage.

**ENGINEERING:** local scorer, independent refit, deterministic replay and archive integrity PASS. Repo Windows/Linux CI code-atlas and native model regression require separate validation.

**SCIENCE:** valid preregistered external synthetic screening **NO-GO**. Conventional calibrated softmax retrieval remains the stronger control. No conclusion of autonomous intelligence, native continual learning, general transfer, or accepted Yggdrasil science.

**DEPLOYMENT:** none: no Yggdrasil owner runtime, training weights, acceptance, merge, controller, queue, first-use or release changes.

Reproduce from `source.tar.bz2` with the commands in `README.md` and run `verify_archive.py` for original evidence hashes. `case_receipts.csv` lists every world/context and model checkpoint checksum. The primary seeds are preserved for a *different independently frozen hypothesis* only if future governance permits.
