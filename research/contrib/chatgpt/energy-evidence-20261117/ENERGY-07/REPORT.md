# ENERGY-07-R1 — energy-guided exact inference on difficult noisy constraints

**Date:** 2026-11-17. **Primary outcome:** DEVELOPMENT NO-GO. **Secondary signal:** better feasible search incumbents, not faster certified reasoning. No Yggdrasil native integration or original scientific first-use.

## Scope and immutable qualification boundary

This source-free synthetic study is a new independent experiment inspired by classical energies, not a CRAM reproduction or a test of trained neural HRM/TRM. We fetched current GitHub state before the study: Yggdrasil `main` `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`, unmerged ENERGY-01 draft [PR #1201](https://github.com/spoonman136668-ai/Yggdrasil/pull/1201) at `69123bc92cad8bc14fe6596f42d9b2f4e71a2542`. No repository, code atlas, runner, scheduler, research loop or accepted state was altered by this study.

- New frozen scientific-protocol SHA-256: `3926907dc135f6e66258150458d06cf4a76e1f9113c688bc150f111043f7102a`.
- Tested executable SHA-256: `c67ab62bff3ee640a53140a176c850b681a7081cf2b476f1c6b96e1d3f1b5046`.
- Scored seeds **541, 653, 787**; graph sizes **24, 30, 36**; 8 unseen queries per combination = **72 cases**. All final cases accounted for.
- Non-scoring smoke seed **997** tested sizes 12 and 24. The auditor independently brute-forced all 4096 hard-clamp-feasible assignments of the two n=12 smoke cases and confirmed the solver's optimum.
- Nine graphs; each has 2*n known random 3-/4-way parity scopes and independently corrupted observations. The method fits factor noise rates from 320 independent labeled observations per graph and sensor noise rates from 48 calibration observations. Test cases have unobserved state variables, corrupted parity labels, sparse noisy unary readings and one truthful fixed state. **Factor scopes are known in advance, not learned; these are constraint tasks, not natural causal discovery.**
- Energy arm: five starts, 20 annealing sweeps, eight greedy sweeps. Looped arm: 20 fixed sum-product BP rounds plus greedy cleanup, *not a fully trained recurrent model*. Exact arm: HiGHS MILP with 0.45-second per-case time limit, no presolve, zero requested relative optimality gap; certify only status=0 and matching computed dual bounds. Guided arm: same MILP with valid upper-bound inequality from the energy incumbent, using the same total solver-plus-search budget. On timeout, retain the best feasible answer. CPU-only (not GPU).

## Primary frozen outcomes

| Variables | Scored | Unguided exact certificates | Energy-guided exact certificates | Energy equals exact on certified | BP equals exact on certified |
|---:|---:|---:|---:|---:|---:|
| 24 | 24 | 3 | 2 | 1 | 1 |
| 30 | 24 | 3 | 2 | 1 | 3 |
| 36 | 24 | 0 | 0 | 0 | 0 |
| **Total** | **72** | **6** | **4** | **2** | **4** |

**Preregistered PASS failed:** Guided MILP certified fewer cases than regular MILP (4 vs 6), and no certificates occurred at all for 36-variable cases. Neither achieves the required 2x *whole-process* improvement at matched certified accuracy. Only 6/72 unguided and 4/72 guided solved cases have independent MILP-side optimality certificates; all other MILP outputs are **feasible but unverified optimums**, not proven failures of the energy model's truth prediction.

### Secondary feasible-solution finding (not primary PASS)

At equal nominal solver time budget, guided exact found a **strictly better feasible fitted-energy objective than unguided exact in 65/72** cases, worse in **4/72**, tied in **3/72**. This is a positive heuristic *primal-incumbent* finding: energy search supplied a good starting upper bound on difficult instances. It is **not** proof that the true hidden state was recovered or that an optimum was found. With 36 variables, neither MILP variant certified any of the 24 cases.

Complete hidden-state recovery was energy **9/72**, BP **12/72**, guided **10/72**, plain MILP feasible output **5/72**. This is intrinsically low because the inference task is noisy and underdetermined; it was not the primary hypothesis.

### Whole-process elapsed (local CPU; measured, seconds)

| Variables | Energy-only | Looped BP proxy | Exact MILP | Guided MILP |
|---:|---:|---:|---:|---:|
| 24 | 0.364 | 0.427 | 10.583 | 10.826 |
| 30 | 0.401 | 0.489 | 10.791 | 11.050 |
| 36 | 1.407 | 1.527 | 12.821 | 12.515 |
| **Total** | **2.173** | **2.443** | **34.194** | **34.390** |

For seed 787/size 36, eight individually isolated processes retrained the common noise model separately. All eight training costs were charged to **every** arm. These group times therefore have more repeated fitting than the other eight groups and should not be used as clean throughput extrapolations. Solver wall-clock limits are nominal requests to HiGHS, not independently proven hard caps. Guided aggregate time was slightly **greater** than exact aggregate time. The ~30x lower time of energy-only is at **unmatched and predominantly uncertified accuracy**.

## Engineering and independent verification

- Original ENERGY-07 scored attempt was aborted by a reversed optimality assertion after eight cases and without a complete output. Its manifest/log are preserved in `../FIRST-SCORE-ABORTED.md`. The bug was corrected without changing model/search parameters and **fresh** seeds 541/653/787 were frozen before scoring R1.
- The monolithic R1 run then hit the local execution ceiling after four worlds and did not persist its in-memory results. The same frozen code and scored cohort were executed as bounded, durable per-world parts; the final 36-variable world was executed per case with twelve-second external watchdogs, all eight completing. This is transparent execution repair, **not scientific parameter tuning**. Some deterministic computations were repeated because their first outputs had not been written. The files and wrappers preserve that evidence.
- Independent `audit.py` uses no imports from `experiment.py`. It checks frozen source/protocol identities; 72 case and factor/assignment arithmetic receipts; hard clamps; objective invariants; solver certificates and reported dual bounds; full source output aggregation; and two 12-bit exhaustively enumerated smoke cases. **{a['checks']} local audit assertions PASS**; **{a['small_exhaustive_assignments_checked']}** brute-force feasible assignments independently checked; 72/72 final cases present.
- **Remaining limitation:** For 24- and 30-variable problems, we independently validate reported primal energies and MILP dual-bound consistency, but cannot cross-certify every MILP status or optimum with an unrelated complete solver. A consistent bound is not a proof of algorithm correctness in isolation.
- Full Yggdrasil native regression, Windows parity, trained recurrent baseline, scientific first-use acceptance, GPU efficiency, and integration **NOT PERFORMED**.

## Outcome and next test

**ENGINEERING:** local synthetic score and independent evidence audit PASS; native qualification UNVERIFIED. **SCIENCE:** NO-GO for the frozen certified speed/accuracy threshold; a narrower feasible-incumbent effect is promising but not proof of faster reasoning. **DEPLOYMENT:** NONE.

Do not tune these scored settings. The next useful scientific experiment would compare energy-guided primal starts to properly optimized exact solvers with official warm starts, separate objective-quality and certificate-time budgets, and a fully trained recurrent network, all on a new prospectively frozen cohort and an independently witnessed evaluation. This is not permission to enter the native research loop.
