# ENERGY-REPAIR-POWER-13 — Exact evidence budget for causal-row repair

**2026-11-20 — Independent source-free mathematical research. ENGINEERING PASS; SCIENCE NOT TESTED; DEPLOYMENT NONE.**

## Motivation and custody

[ENERGY-REMAP-GATE-12](../ENERGY-REMAP-GATE-12/README.md) proved the original [ENERGY-REMAP-11](../ENERGY-REMAP-11/README.md) row-local hard-reset could not activate from six OLD plus two NEW observations, because maximum reset posterior 5/7 was below the frozen 4/5 decision threshold. That original 36-world experiment was therefore a conventional sensor-mapping control, not activated topology repair.

The next scientific test must not consume new experiments before establishing both a feasible sample budget and acceptable null false-repair risk. This gate computes both **exactly** for a specified categorical source law. It does not change prior thresholds, previous consumed primary outcomes, or accepted native Yggdrasil.

The preregistration was committed at `db1dcc1c044172f7eb307fb49089db3924fc1b84` **before** the [executable mathematical certificate](certificate.mjs), committed `24f2b2d238800f593a0426b3bf6f102224905357` (Git blob `8e76bc55ef263fa8b52308f567eb9707ba7eb482`). The source was fetched from GitHub and compared byte-for-byte with the exact function **before evaluation**. The [original complete result](result.json) was saved at `30141282171fd0d19f4a6b8fc60126082d2e72c7`, Git blob `daf12b0f79989185f2dcb3d4a6caa631f9147681`.

## Precise source-law assumptions

Each source/action row has six categorical consequences. OLD observes exactly 6 independent consequences. The preferred old target (category 0) has probability 110/125 = 0.88; each of five other categories has 3/125 = 0.024. NEW receives m observations, m=1..8, under either a **stationary NULL** (old target remains category 0) or a **local REWIRE** (new preferred target category 1). Target identities are known only to the analytical probability calculator, not a learner.

The frozen conventional Bayesian guard is a symmetric Dirichlet(0.5) row prior, prior reset probability 1/4, and reset if posterior at least 4/5. For OLD counts c and NEW counts y, the reset-versus-stay Bayes factor is (9)_m/(3)_m times the product over six categories of (0.5)_(y_i)/(c_i+0.5)_(y_i). The gate is equivalent to **BF >=12**. Its maximum possible BF under any OLD/NEW row observations is (9)_m/(3)_m; this is attained when the NEW categories were not seen in the OLD evidence. The first sample budget with any possible activation is m=3.

All 462 possible OLD six-category count vectors are paired with every possible NEW count vector for each m. Their NULL and REWIRE probabilities are weighted with exact integer multinomial coefficients and rational category probabilities. Both probability masses must sum to one. **1,386,924** possible OLD/NEW count pairs are exhausted without Monte Carlo, original primary seed reuse, or native checkpoint execution.

Frozen eligibility requires **rewiring detection at least 80%** and **familywise false-repair upper bound at most 5% across 12 possible source/action rows**, using the conservative union bound 12 × single-row false probability. These are probability-model conditions, not learned intelligence qualification.

## Exact results

| NEW observations / row | Maximum possible reset posterior | Change-detection power | False reset per stationary row | 12-row false upper bound | Eligible |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 50.00% | 0% | 0% | 0% | No |
| 2 | 71.43% | 0% | 0% | 0% | No |
| 3 | 84.62% | 77.19% | 0.12092% | 1.45106% | No |
| 4 | 91.67% | 74.36% | 0.01361% | 0.16331% | No |
| 5 | 95.33% | 76.51% | 0.00253% | 0.03039% | No |
| 6 | 97.28% | 74.82% | 0.00058% | 0.00694% | No |
| **7** | **98.35%** | **89.25%** | **0.00335%** | **0.04016%** | **First eligible** |
| 8 | 98.96% | 93.64% | 0.00721% | 0.08652% | Eligible |

Rates need not increase smoothly with n due to exact discrete count thresholds.

**Minimum eligible sample count for this law is seven NEW observations per row**. For six states × two actions this would require 84 NEW public transitions, compared with the original 24: an additional **60 interventions** or **3.5 times** the prior NEW evidence budget. These 84 interventions have **not been performed**.

## Independent derivation and limitations

The [independent arithmetic audit](audit.mjs) was committed at `2414e63d83cdf15142dcfbbd8ae146c42b1792c0` (blob `f195cdff07c063ce20138fabbb26830081c62fd7`). It uses reversed count-composition generation, independent multinomial construction through successive binomial coefficients, and sequential predictive probability ratios rather than the first certificate's cached rising-factor ratios. It recomputed **all 1,386,924 cases**, exact false and true-positive integer numerators for every m, and the earliest eligible budget. **PASS**. The immutable [auditor output](audit-result.json) was committed `db0af02c0c22adc9a39c31590be69b1724996865`.

This result is limited to a given synthetic 0.88-dominant categorical mechanism with one preferred outcome moved. It proves neither an ability to discover **unknown** causal graph structures nor superiority over conventional Bayesian mixing and change detection. It does not test hidden/unsignaled contexts, cumulative native functional memory, genuine multi-step trajectories, out-of-family changes, action selection, real-world interventions, or independent native cold restoration. A Bayesian reset rule by itself is **a conventional control**, not novel AI.

### Engineering, scientific and deployment decision

**ENGINEERING PASS:** source pinned and readback verified, exact probability mass and exhaustive enumeration, independent full arithmetic audit.

**SCIENTIFIC NOT TESTED:** m=7 is only analytically eligible. No primary empirical intervention trial, measured gain, native learned causal relationship, retention, transfer or general intelligence verified. ENERGY-REMAP-11 remains MIXED_NO_GO, with consumed primary seeds untouched. Do not convert the analytical m=7 finding into a claim of beneficial native mechanism or promote it by bypassing strongest conventional comparator.

**DEPLOYMENT NONE:** no accepted main, Amalgam PR #1278, owner checkpoint, runner, scheduler, controller or operational ref changed. The research PR's G29 dual-platform atlas source-set CI block remains a separate unresolved engineering issue.

**Future science:** Only a *different mechanism that is demonstrably active*, with frozen disjoint intervention tasks, measured action-consequence improvements, independent cold retention and strong fully fitted conventional controls, could establish new science. Merely taking seven examples and repeating the original MAP reset is not enough.
