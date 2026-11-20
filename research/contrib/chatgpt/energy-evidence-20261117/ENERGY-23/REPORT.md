# ENERGY-23 — Disagreement is not expected information gain

**Date:** 2026-11-18. **Classification:** source-grounded exploratory mathematical diagnostic, not a new prospective native CKAD experiment or independent scientific qualification. Existing CKAD-22 `DEVELOPMENT_GO` is preserved; scientific acceptance remains unverified.

## Source pin and question

At Yggdrasil draft CKAD PR #1207 commit `5da91380fdbb7aeb955735ad39225ce8ac5e89c2`, `yggdrasil/native_episode_experience.py` Git blob `5c428b88bb46e251f6ced5b1aa6887b18d4c3faa`, lines 234–328, the novel context starts with 7/8 weight on prior candidates and 1/8 on a new candidate. `context_explore` selects the action with highest weighted variance among candidate forecasts; it breaks ties toward predictions nearest 1/2 and then action0. This is a legitimate disagreement heuristic but it is **not necessarily optimal Bayesian experimental design**.

## Exact counterexample at source prior

Take **one prior** and **one new** hypothesis weighted 7/8 and 1/8, and two candidate interventions. The Bernoulli probability of the next revealed binary result under the two hypotheses is:

| Candidate intervention | Prior hypothesis P(result=1) | Novel hypothesis P(result=1) | Forecast variance | Expected mutual information | Expected correct hypothesis identification |
|---|---:|---:|---:|---:|---:|
| Action 0 | 13/20 | 1/10 | 847/25600 (~0.03309) | 0.10493 bits | 7/8 = 87.5% |
| Action 1 | 19/20 | 9/20 | 7/256 (~0.02734) | **0.13272 bits** | **9/10 = 90.0%** |

Source disagreement selects action0 since 0.03309 > 0.02734; **expected hypothesis information instead prefers action1**, a 0.02778-bit gain (~26.5% more information). If one uses maximum-posterior hypothesis identification immediately after the result, action1 achieves 2.5 percentage points higher expected identification accuracy.

These are **synthetic feasible Bernoulli forecasts** with the source's two-candidate prior, not verified to be an actual reachable CKAD-22 checkpoint state. The criterion applies to a binary transition observation alone; full two-stage transition-plus-reward probe value requires an independent extension, and selecting higher information does not guarantee higher terminal reward.

## Exhaustive exploratory sweep

For each action and each hypothesis, predictions range over 1/20, 2/20, ..., 19/20, yielding 361 forecast pairs per action. There are 129,960 ordered, non-identical pairs of interventions. The primary implementation computes each candidate's exact rational forecast variance and Shannon mutual information; independently implemented KL-based auditing recomputes the full enumeration.

- **8,704/129,960 (6.70%)** of ordered two-action cases prefer different actions by disagreement versus expected information (excluding numerically tied information scores).
- Largest one-action information shortfall from following source disagreement instead of mutual information on this grid: **0.0525708733 bits**.
- Neither the grid distribution nor its mismatch rate is an empirical estimate of CKAD-22 encountered environments. The exploratory grid was not preregistered as a scientific heldout, and the example was selected during analysis. Do not convert these into a generalization-rate claim.
- The independent KL-identity audit passed all 129,960 ordered comparisons and example checks after correcting two bookkeeping/coding errors in development before final score preservation. Full frozen-source regression, original native checkpoint replay and scientific first-use remain **UNVERIFIED**.

## Consequences

**ENGINEERING:** formula-level exploratory counterexample reproduced and checked with a separate mathematical implementation. No native code changed.

**SCIENCE:** No accepted gain or improvement. This identifies a **testable intervention-selection gap** rather than a proven defect in the learned native model. Since `ENERGY-22` already showed normalized energy is algebraically the same as CKAD's existing Bayesian mixture, there is no reason to replace the native planner. If studied, compare the existing forecast-disagreement probe policy to exact one-step expected information gain (plus a reward-aware exploration control) on new, separately frozen public contexts with identical probe counts, strongest conventional trained controls, OOD transfer, retention and entire cost. Do not tune on CKAD-22's already consumed held results.

**DEPLOYMENT:** None. CKAD-22 development GO remains historical and unmerged; this archive branch is read-only relative to native Yggdrasil.