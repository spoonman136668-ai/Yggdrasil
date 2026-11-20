# ENERGY-45 — Contradiction-gated causal factor replacement (frozen primary)

**Date:** 2026-11-18. **Decision:** **DEVELOPMENT_NO_GO**, 7/9 frozen gates PASS. No native Yggdrasil science or model training.

## Research question and setup

Does replacing a contradicted causal support, instead of adding corrective coefficients indefinitely, retain old knowledge and improve unfamiliar-condition prediction? The scorer/auditor source was committed to PR #1210 at `2945114b2381b3673bd5e51084f4c591e6f91242`, then the **nine frozen gates, fresh seeds and controls were committed before primary scoring** at `c57ebb9c8c8d62f1a806cd31e396718ef94b3c20`. No threshold or model was tuned on primary seeds.

This is self-authored **synthetic** source; each world has 12 binary randomized intervention variables, five planted signed factor mechanisms from a known 364-feature parity/AND library, three shared factors, one old-only and one new-only. Each method has 96 old and 96 new labeled interventions; holds 128 disjoint probes in each old/new/cold domain. **27 changed worlds**, and **9 true no-change worlds** where only nuisance cues shift. Hidden factor supports/weights and held labels are available only to the evaluators, not learners. All 11 arms receive the same observations.

Candidate: learn old OMP4 model; freeze its old predictions, propose dropping one support and adding a newly discovered factor using the first 72 new observations, and apply the proposed structural change only when the 24 new-context **training-validation** labels indicate an MSE reduction of at least 0.12. Refit four new-context weights on all 96 new witness labels. The old context remains unchanged. Frozen control algorithms: unconditional same-budget replacement, OMP2 delta, stagewise OMP4, cumulative OMP structural-memory7, standard OMP7, ElasticNet, Ridge, random forest, no repair and shuffled consequences. All models are supervised; no native Yggdrasil learner, autonomous hypothesis/action acquisition or general-purpose intelligence was tested.

## Frozen primary metrics

| Fully trained method | Old held MSE | New held MSE | Cold held MSE | Local fit+predict seconds |
|---|---:|---:|---:|---:|
| gated_replace | 0.112399 | 0.110384 | 0.111630 | 0.27171 |
| omp_structural_memory | 0.103927 | 0.108554 | 0.131138 | 0.45476 |
| omp_delta2 | 0.112399 | 0.124098 | 0.165042 | 0.21142 |
| elasticnet | 0.139537 | 0.135076 | 0.173626 | 0.51263 |
| full_omp7 | 0.139229 | 0.141684 | 0.321189 | 0.45922 |
| stagewise_omp4 | 0.112399 | 0.137228 | 0.321004 | 0.21440 |
| unconditional_replace | 0.112399 | 0.349563 | 0.342984 | 0.26600 |
| no_repair | 0.112399 | 1.601963 | 1.618785 | 0.18563 |
| shuffled_gate | 0.112399 | 4.219304 | 4.171640 | 0.25779 |
| ridge | 2.155449 | 1.913656 | 2.195372 | 0.48140 |
| forest | 2.768932 | 2.654858 | 2.835837 | 2.05685 |

**Mean cold error:** candidate **0.111630** vs best conventional structural-memory control **0.131138**; candidate reduction **14.88%**, exceeding the +10% frozen aggregate margin. This qualifies a **development observation**, not accepted science. Contradiction gating correctly deleted the planted old-only support and installed the new-only support in **27/27 changed worlds** and rejected change in **9/9 unchanged worlds**. Old held error remained exactly equal to the frozen old checkpoint **0.112399**, but the strongest fully trained conventional learner achieved **0.103927**. This missed the frozen old-vs-best-control 5% bound. The seed-level gate also failed: exactly **1/3 seeds** strictly outperformed the strongest control within that seed. The aggregated benefit is not reproducibly superior across all independent seed cohorts.

## Frozen nine gates

| Gate | Outcome |
|---|---|
| `cold_vs_stagewise_omp4_5pct` | **PASS** |
| `cold_vs_strongest_10pct` | **PASS** |
| `cost_max_3x_stagewise` | **PASS** |
| `nochange_false_gate_at_most_10pct` | **PASS** |
| `old_prediction_protected_1pct` | **PASS** |
| `old_vs_best_control_5pct` | **FAIL** |
| `replaced_truth_support_70pct` | **PASS** |
| `seed_stability_2of3` | **FAIL** |
| `sham_negative_new_20pct` | **PASS** |


**7 PASS / 2 FAIL = DEVELOPMENT_NO_GO**. No post-result tuning, no extra primary seed evaluations. Existing matched algorithms (especially OMP structural memory) remain strong. The candidate's old-model inference is protected, but its original old weights are not independently requalified against the strongest control. The three primary seeds are only three independent experimental clusters; the point estimate is not a statistically established generalized improvement.

## Seed stability

| Seed | Candidate cold MSE | Strongest conventional control in that seed | Control cold MSE |
|---|---:|---|---:|
| 8803 | 0.093083 | stagewise_omp4 | 0.093086 |
| 8819 | 0.145943 | omp_structural_memory | 0.112791 |
| 8831 | 0.095863 | stagewise_omp4 | 0.095852 |


## Independent custody and reproducibility

- Frozen exact source bundle `source.tar.br` Git SHA `044aef93b34f020b00e9906bb8e4f00f29858d80`, packed SHA-256 `0951c0cb804c3f4bdd1ecf910926bb0b59d59007c9615e35c5aefd0cbb7f13e7`; original scorer SHA-256 `0f57e0ef01f69cfc94e6b31b355d628e27813bcbaf454d6c88f1eac643d77718` and independent auditor SHA-256 `947a47d93085c7478687d183edc8da7dc63a4ae56b8e6ac4bbc3b66e58c28213`.
- Byte-exact full original primary `scored.json` (200,007 bytes) archived as `scored.json.bz2` (31,327 bytes); original SHA-256 `46601621373db4ff6531bda4a36c8d4c50775b147df18137581a3f80d67c8347`, compressed SHA-256 `2fa2657af994e50e71f52aa247cdd8c4edafba6a04cb75128a4a87e4bcf92295`, compressed Git blob `a9f0ab844a9c3fa87a27a1d4e88b7c68b5478664`. This includes **all 36 worlds, all 11 arms and individual selected factor identities/coefficients and times**.
- Per-case fixed CSV `case_receipts.csv` (27,058 bytes, 36 rows) SHA-256 `56f58705418db694cc8966ffa2f88846c20253896728ff6353d43de871e313f8`, Git blob `4d36162a61962eb08c396169aea0e34233973616`; redundant outcome integrity checker is `verify_archive.py`.
- An **independently authored** generator and refit auditor, not importing ENERGY-45 scorer, checked every old/new/cold prediction under all 11 complete learners, gate decisions and every latent support: **154,113 comparisons PASS**. It shares NumPy/scikit-learn back-end solvers, not their internal independent reimplementation.
- The single unchanged-source semantic replay **PASS**: byte-identical timing-free canonical record (96,245 bytes), SHA-256 `84e55203bf407496011257ad0acdc4dedb38373f49d693ca5b3d5412bbf52236`. Timings differ naturally and are excluded from the deterministic identity, but original and replay wall seconds are preserved in `replay_result.json`.
- Environment: Linux CPU, Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0; single-threaded BLAS; no GPU, external model or paid API.
- **No native Yggdrasil full regression, protected scientific first-use, acceptance, model training, accepted-ref changes, controller/runner/scheduler/queue actions or deployment**. Repository code-atlas CI is a distinct engineering gate and must not be reported as this scientific result.

## Decision and next falsification

**Preserve the genuine aggregate signal but do not promote.** The contradiction gate works well as a synthetic structural-edit selector, including no-change detection. The unresolved qualification gaps are (1) preserving competitive **accuracy**, not merely frozen old predictions; and (2) replicating gains across independent seeds, distinct environment families and larger complex mechanisms. A new preregistration with disjoint causal generators, calibrated confidence to avoid harmful edits, and matched conventional structural-memory baselines is required before integrating any mechanism into native Yggdrasil.
