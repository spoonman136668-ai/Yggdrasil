# CKAD25-U — native intervention choice against matched action budgets

**Research-only prospective synthetic developer qualification** (no protected CausalGym first-use; no accepted-model/source change). Tests the *existing* `NativeCumulativeLearner.propose()` rather than another confidence or repair threshold.

## Distinct hypothesis and falsification

CKAD25-S and CKAD25-T learned new fixed synthetic families from supplied intervention records but did not establish that their learner can **choose** informative interventions. CKAD30 and CKAD31 have already tested identifiability/sparse-repair guards and both are negative; this avoids repeating their consumed cohorts.

For each of three new seeds and six new four-input Boolean laws, precommit 16 SHA-permuted addresses: **4 identical external held test addresses**, **4 common revealed start interventions**, **8 available public acquisition addresses**. Each of four policies (the same old native learner's `propose()`, uniform random, fixed order, and a conventional exact Bayesian sparse-ANF expected-information selector) receives exactly **4 additional do-action/outcome revelations** and is tested on the exact same 4 reserved assignments. Every policy's native learner cold-restores the same original CKAD25 checkpoint, cumulatively learns all six families in existing slots 1..6, and preserves original slot0 and source properties. No labels of the true law family, future outcomes, or reserved test addresses reach the proposer.

**Important mechanism limitation:** At four source observations, the current native learner has *not yet fitted a degree hypothesis* (it fits at 8). Thus this is a test of the existing native **early-acquisition heuristic and direct witnessed-source support**, not of a learned posterior's sophisticated information gain. It is a valid falsification of whether the existing acquisition policy already helps under sparse cold-start conditions, not proof of general causal experiment design.

Predictions after eight observations are from existing native degree readout; opt-in sparse repairs are scored separately. Conventional exact sparse ANF, fully trained CART/RF/logistic and frequency controls use the same revealed observations. Scores are Brier on **the same fixed held test addresses** for all policies, with abstention p=0.5. The exact conventional EIG policy has a fixed supplied 697-function grammar, and may be misspecified for a law; its fallback and results must not be described as a universal oracle.

## Frozen protocol and boundaries

- Accepted `main`: `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9` unchanged.
- Native developer research parent PR #1244: SHA `93c66467427b7d5e3827eb9a27a6c0195e296c52`, tree `810d82b3dfd7fd7d9dac7721a9902f74a48a7e60`.
- Original source-owned cold checkpoint SHA256 `c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f`.
- **Prereg committed before executable source and before first use:** `d7fd9367d31e4dd1d17567444fcf2ba26c5510c8`.
- **New source committed before primary score:** `be2362d2172d38c7a110ab89b98c3c60a92034e3`; Git blob `661c9d73bf62a4b85c21a28c3a5c04fe30cccf58`.
- Reuses CKAD25-S's verified helper functions for original checkpoint validation, complete fitted conventional controls and scoring, not its consumed synthetic held cohort.
- 3 seeds × 6 families × 4 arms × 8 actions = 576 wholly synthetic intervention records; 72 held labels per arm; original/protected environment source calls **zero**. Repeated fixed family formulas are **not** 18 independent causal families.
- Frozen GO requires both 0.03 lower Brier than random and fixed native acquisition, near conventional exact EIG (+0.03), ≥18 confident correct out of 72, no >2 excess confident errors, within +0.02 of exact sparse Bayes on same candidate train rows, and lossless old native retention. Nonpass is **DEVELOPMENT_NO_GO**. No post-result adjustment/tuning.
- Run only on isolated research PR and GitHub-hosted Linux/Windows. No merging negative candidates, accepted `main` writes, owner/FORGE dispatch, controller/scheduler, native source modification, paid API or deployment. `SCIENTIFIC_PASS=false` independent of focused CI.
