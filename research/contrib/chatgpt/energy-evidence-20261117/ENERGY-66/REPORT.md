# ENERGY-66 — Sequential learning of two unfamiliar fourth-order causal factors

**2026-11-19. Preregistered verdict: `SCREEN_NO_GO`, 4/9 frozen gates PASS.** External synthetic research evidence only, **NOT native Yggdrasil training or an accepted scientific pass**.

## Chronology and reproducibility

- Prior archive HEAD `719b9199ace1dcc93d39d80805513773adebd535` on draft PR #1210. **Exact scorer and independent auditor froze in GitHub commit `488d351bc2d942b43926be758012f1c3fd28c6f8`.** `source.tar.bz2` SHA-256 `81c8aac1ca9e6cef267051fcb3664bb11515e2d5ded456e0d602badf0c0e1b6a` and Git blob `e9cfce1e57fdd8b4a0eccdd5e17efae779ae296f`; exact scorer `2f1db4e7d202baada49c7c2635a4b6ffd608d2f30611235c2a59dec9f7a12801`, auditor `ec05440518e3dc77e00afd752cd52e7f1a7d12c6734b27c2a99dcd7dc03ad59c`.
- **Separate GitHub preregistration `febf6ded85f7662223123059eabe311aaf69b41e` read back BEFORE prospective seeds** `999637` and `999659` were run. The 3-world prefreeze engineering seed `999599` is excluded from confirmation, independently audited with 5,322 checks.
- Each fresh seed: world IDs 0-3 × `double_quad`, `triple_quad`, `double_quad_plus_fifth`, totaling **24 worlds**. Reserved primary seeds `[108101,108119,108137]` **NOT scored** because screening failed the frozen stop rule.
- Every world: 8 directly controllable binary variables, 256 possible intervention identities; **212 disjoint underlying assignments** = 56 OLD witnessed +48 NEW witnessed +36 OLD/NEW/COLD held each, Gaussian noise sigma=.18. Cold is NEW mechanism at unseen intervention IDs, not a natural-world generalization. Hidden planted supports and held outcomes never enter fitting.

## Question and methods

Can a historical three-pair causal model **add two previously unseen fourth-order effects** with sequential residual-based feature selection, without overwriting its OLD predictions, more accurately than the strongest fully trained conventional model on the same witnessed actions?

Candidate learns three old pair supports using OMP3 over a supplied 28-pair Walsh bank; freezes OLD head; twice residualizes NEW witnessed outcomes against active supports, orthogonalizes 70 author-supplied quadruple features against the active basis, greedily selects two, then jointly refits NEW Ridge. Mechanisms: two planted fourth-order factors, three factors (capacity overrun), or two fourth-order factors plus an unrepresentable five-way factor. The causal feature grammar and the selection strategy are **researcher authored**, not freely discovered. Checkpointed OLD retention follows from a frozen OLD head by design, not mutable-network interference resistance.

Strong realistic matched-label controls: 3-fold CV ElasticNet on exact old supports plus all fourth-order features; 3-fold CV ElasticNet on all 98 pairs+quads; matched-bank OMP5; full-bank OMP5; conventional softmax memory mixing OLD and NEW OMP5. Old-support-only Ridge, frozen OLD, shuffled-label negative; truth-informed oracle is **diagnostic only** and excluded from strongest-control comparisons. All arms receive identical 104 outcomes; models use different computational effort and capacity, so equal observations do **not** imply equal compute.

## Original prospective cold held MSE (lower better)

| Arm | Cold MSE |
|---|---:|
| `truth_oracle` (truth-informed diagnostic) | 0.038935 |
| `matched_elasticnet` | 0.633000 |
| `two_factor_residual` | 0.711541 |
| `full_bank_elasticnet` | 0.733944 |
| `matched_omp5` | 0.789140 |
| `softmax_memory` | 0.953922 |
| `full_bank_omp5` | 0.957872 |
| `old_frozen` | 2.640078 |
| `old_support_only` | 2.823309 |
| `shuffled_new` | 7.042050 |

**Candidate 0.711541 vs strongest realistic `matched_elasticnet` 0.633000: candidate has 12.41% greater cold MSE.** Full-bank ElasticNet MSE 0.733944; conventional softmax memory 0.953922. Candidate improves on the latter but not on the best control. The unattainable truth-informed oracle MSE 0.038935 is not evidence of learned transfer.

### Per prospective seed cold MSE

| Seed | Candidate | Matched ElasticNet | Full ElasticNet |
|---|---:|---:|---:|
| 999637 | 0.712878 | 0.639960 | 0.789496 |
| 999659 | 0.710204 | 0.626040 | 0.678393 |

### Per causal family cold MSE

| Mechanism | Candidate | Matched ElasticNet | Full ElasticNet |
|---|---:|---:|---:|
| `double_quad` | 0.034296 | 0.074818 | 0.070334 |
| `double_quad_plus_fifth` | 1.046506 | 1.714549 | 1.961621 |
| `triple_quad` | 1.053820 | 0.109634 | 0.169879 |

**Exact planted two-quad recovery in `double_quad` family: 100.0%**, but recovery and the preauthored representation are not equivalent to general compositional intelligence. `triple_quad` exposes the two-feature update's hard capacity limit; full matched ElasticNet handles the additional factor much better. `double_quad_plus_fifth` creates an out-of-bank term that no supplied four-way-only candidate can represent.

## Frozen qualification gates

| Frozen gate | Result |
|---|---|
| `cold_gain5_full_elasticnet` | **FAIL** |
| `cold_gain5_matched_elasticnet` | **FAIL** |
| `cold_gain5_strongest` | **FAIL** |
| `double_quad_both_recall70pct` | PASS |
| `each_family_nondegradation10pct` | **FAIL** |
| `improvement20pct_old_frozen` | PASS |
| `old_exact` | PASS |
| `per_seed_strict_wins` | **FAIL** |
| `shuffled_negative20pct` | PASS |

**Classification `SCREEN_NO_GO`:** 4/9 pass; all four critical gates `cold_gain5_strongest`, `cold_gain5_matched_elasticnet`, `per_seed_strict_wins`, `each_family_nondegradation10pct` fail. Prospective results were neither refitted nor thresholds changed. No reserved 36-world primary scored.

## Engineering verification, limits and custody

- Independent auditor does not import scorer and reconstructs the original intervention IDs, labels, planted coefficients/noise, two new-feature selections, old readouts, all 10 fitted arms, held-out predicted vectors and aggregate errors: **42,366 PASS checks**. Audit uses the same disclosed generator semantics and NumPy/sklearn backend; it is not an independent scientific replication.
- Frozen exact-source deterministic replay **PASS**, semantic SHA-256 `ed21c81da7928373bf4abe2ed0d540bf3c0c21b7aa0df15fd0a1b9c908a083c2`, excluding only `runtime_seconds`. Replaying identical seeds is not a new scientific dataset.
- Original scored result `screen_scored.json` SHA-256 `caa730eebf2b5aa61f8c0528dbcb4552bb4567449c72ed272cf7de45999f07b8`, byte-exact original audit, replay, audit-of-replay, excluded prefreeze development records and per-world original predictions live inside split `EVIDENCE.tar.bz2` with manifest and verifier. `case_receipts.csv` indexes selected versus planted causal terms and per-world cold errors.
- Single-thread CPU prospective scorer wall time 1.3804s excluding auditor, replay, GitHub and other infrastructure. Neither energy in Joules nor whole-process cost was measured. Native Yggdrasil Linux/Windows full regression, owner acceptance and scientific first use remain independently unverified.

## Decision

Preserve the negative result. **Recovering both factors is insufficient evidence of robust cumulative native causal learning** when three factors or unrepresentable higher-order effects appear. On these synthetic worlds, the fully trained matched-feature conventional learner is a stronger predictor. Do not use consumed seeds for an outcome-tuned re-test; leave Yggdrasil native runtime, accepted main and autonomous loop unchanged.
