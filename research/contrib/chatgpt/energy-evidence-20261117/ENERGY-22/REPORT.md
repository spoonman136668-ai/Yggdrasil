# ENERGY-22 — Energy/Bayesian hypothesis-mixture identity (source-grounded negative control)

**Date:** November 18, 2026. **Classification:** analytic development-only proof and independent source-free model-of-formula audit. **Scientific performance:** UNVERIFIED / NO PROMOTION. **Deployment:** NONE.

## Motivation and source

Yggdrasil's ongoing native CKAD-22 program already reports **DEVELOPMENT_GO** for a newly learning context candidate, while `scientific_pass=false`. Avoid repeating its frozen synthetic experiment or replacing its exact expected-reward planner with MAP/single-witness selection.

Read-only pinned source: `spoonman136668-ai/Yggdrasil` CKAD PR #1207, native head `f04cfcac2aa07806a6b942d968119de87bfb6aaf`, `yggdrasil/native_episode_experience.py` Git blob `5c428b88bb46e251f6ced5b1aa6887b18d4c3faa`. The source uses `NOVEL_PRIOR = Fraction(1, 8)`, 7/8 distributed uniformly over retrieved hypotheses, and updates exact Fraction weights with prequential transition and terminal likelihoods. Its terminal forecasts condition candidate weights on the observed next state. Code at lines 234–328 was read without modification.

## Exact equivalence

Let hypothesis `h` have weight `w[h]`, predicted next-state likelihood `p[h](s|a)` and terminal likelihood `q[h](y|s,a,b)`. Define a classical-energy potential with *unnormalized Boltzmann mass* `exp(-E(h,s,y|a,b)) = w[h] * p[h](s|a) * q[h](y|s,a,b)`. Then:

- Correct marginal next-state prediction is `P(s|a) = sum_h w[h] p[h](s|a)`.
- After the next state is actually observed, the correct terminal prediction is `P(y|s,a,b) = sum_h w[h] p[h](s|a) q[h](y|s,a,b) / sum_h w[h] p[h](s|a)`.
- After observing transition and reward, the correct posterior candidate weight is `w'[h] = w[h] p[h](s|a) q[h](y|s,a,b) / sum_k w[k] p[k](s|a) q[k](y|s,a,b)`.

These are **the same mathematical operations** as the existing CKAD-22 Bayes/mixture implementation. Correctly normalized energy marginalization changes the parameterization, not the predictions, actions, or learning information. Its computational implementation can differ, but no improvement in reward or prediction follows solely from expressing exactly the same mass as an energy.

## Completed exact-rational check

The frozen analytic protocol covers **384 deterministic candidate-probability configurations**, with 1, 2, 3 and 5 retained hypotheses plus one new candidate. It evaluates 5 distinct points per configuration, 4 sequential witnessed posterior updates and a separately updated novel candidate; all candidate transition/reward probabilities are strictly between 0 and 1. It does not consume original scientific heldouts, run native checkpoints, access protected actions or train on historical CKAD outcomes.

Two **independently written implementations** (no shared imports) checked **26,496 exact-rational equalities**, covering posterior normalization, transition probabilities, next-state-conditioned terminal forecasts, and chosen first actions. Both executed PASS. Byte-identical primary result on rerun.

| Negative-control failure | Count of disagreements with normalized mixture |
|---|---:|
| Treat terminal weights as unconditioned on observed next state | 14,519 forecast comparisons |
| Use one highest-weight candidate rather than marginalizing | 14,987 forecast comparisons |
| Use winner-take-all candidates for first actions | 326 / 1,920 decision comparisons |

These control counts describe **artificial analytic probability configurations**, not failures of native CKAD-22 on its own source test set. The actual cost of an energy-based implementation is also unmeasured; no speedup claim.

## Engineering / science / deployment decision

**ENGINEERING: PASS (local analytic only).** Source code/protocol/results and independent audit are retained with SHA-256 custody. Full native Yggdrasil multi-platform regression and CKAD-22 original-source replay are **NOT EXECUTED** in this gate. GitHub G29 atlas acceptance must be evaluated separately.

**SCIENTIFIC: NO NEW GAIN CLAIM.** This closes the *representationally identical energy rewrite* as a standalone path to better native performance. It does **not** disprove novel energy features, causal consistency constraints or new learned hypothesis families. For those, a distinct prior or additional learnable structure is needed and a prospectively frozen native heldout must beat original CKAD-22, trained conventional and exact controls, with retained learning and whole-process cost.

**DEPLOYMENT: NONE.** No model change, accepted reference, research loop, controller, schedule or merge.
