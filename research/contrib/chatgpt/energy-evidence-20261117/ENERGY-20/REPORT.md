# ENERGY-20 — Causal energy factors versus fully fitted conventional forecasts

**Date:** 2026-11-17 US Eastern (execution UTC 2026-11-18).  
**Outcome:** **DEVELOPMENT NO-GO**. Isolated, source-authenticated synthetic development. Not native Yggdrasil model acceptance or original scientific first-use.

## Plain English

We tested whether adding three learned causal-energy factors to the *transition forecast* helps Yggdrasil-style two-step action selection. It did **not** beat conventional models that learned from the same witnessed actions. On the changed causal world, its policy obtained **318/432 rewards**, versus **342/432** for the full-table Bayesian control (**24 fewer successful outcomes, -5.56 percentage points**). The energy approach also had a worse transition Brier error (**0.2511 versus 0.2316**, higher is worse).

This is not evidence that all energies are ineffective. The three parity features were explicitly selected to resemble the synthetic world, so even an improvement would **not** establish spontaneous discovery of new causal structure. The underlying native CKAD-20 already uses correct probability-weighted planning and historically failed its own scientific development thresholds. Our current experiment does not execute its pretrained checkpoint.

## Source / isolation

- Exact public development environment **byte-for-byte copied** from `spoonman136668-ai/Yggdrasil` draft PR #1207, commit `d8f27db46af889afdfeb104fc471a710fc6d5c06`, path `research/contrib/chatgpt/CKAD-20/synthetic_world.py`.
- The source's Git blob SHA-1 is `160001d60f2ce2ca7ca3e9ab5d14261ba9ce42a8` and was independently confirmed after local copying.
- No imported protected data, real research environment actions, original scientific first-use, native model edits, runner dispatch, merge or deployment. All episodes are freshly generated under `energy20-*` public development cohorts.
- Existing source uses two sequential binary interventions, a public first state, a second state and a delayed terminal reward; source-side hidden variables remain inaccessible to the trained models.

## Frozen comparison

- Pre-scoring frozen source hash: `experiment.py` SHA-256 `8e1199b637b5cfad0bf6000af3f9476ee763db74131dc80c55c5a684708e3b76`.
- Preregistration hash: `cb967809c759831fac4a74d2b708d692b5b779fab0b8f888bd5ce69075d723ad`. `freeze.json` seals the fixed inputs; `scored.json` was written once against that freeze.
- Seeds: **411, 523, 647**. Each seed received **112 witnessed, uniformly randomized** interventions in the invariant world, then **112 new witnessed interventions** in the shifted context-dependent world. Learning after each phase uses only the episodes available up to that point.
- Each phase was evaluated with **144 new, disjoint held episodes per seed** in each of three worlds: invariant, context-switch and terminal-switch. Therefore each world has 432 paired held episodes per phase, and each policy experiences the same source-generated exogenous episodes.
- All methods use the **same learned Beta terminal reward table** and the same correct, expectation-weighted, two-stage decision rule. The difference is **only in the transition probabilities**.
- Comparison arms: fully fitted full-context Beta, pooled Beta, prequentially selected Beta (CKAD-20 conventional-control logic), four-parameter saturated L2 logistic trained with L-BFGS, three-coefficient parity-factor energy (**only two independent feature directions; the reverse-action term is the negative of the invariant-action term**) trained by regularized conditional pseudolikelihood with L-BFGS, energy with shuffled initial contexts, and first-phase energy frozen against further training.
- All convex optimizer fits converged with maximum observed gradient infinity norm **4.28e-7**, below the prespecified 1e-5 limit. No tuning based on held outcomes.

### Held executed terminal rewards — after both learning phases (higher is better)

| Method | Original invariant family | Changed context family | Unfamiliar terminal family |
|---|---:|---:|---:|
| Full-context Beta | 322/432 | **342/432** | **138/432** |
| Selected Beta | 322/432 | **342/432** | **138/432** |
| Pooled Beta | **374/432** | 285/432 | 37/432 |
| Trained conventional saturated logistic | 353/432 | 318/432 | 86/432 |
| **Three-factor energy** | 353/432 | **318/432** | **86/432** |
| Context-shuffled energy (negative control) | **374/432** | 285/432 | 37/432 |
| Frozen first-phase energy | **374/432** | 285/432 | 37/432 |

The baseline table ties and inverse family performance are real: policy actions change only at the first decision; terminal models are shared. The initial training phase gave identical rewards across all arms: invariant **359/432**, shifted **251/432**, terminal-switch **92/432**. After additional training, the energy's original-family reward moved 359 to 353 (drop **6/432**, within the 5-point retention limit), whereas its shifted-family reward still fell below the strongest conventional controls.

### Held transition probability error — phase 1 (lower is better)

| Method | Invariant | Shifted | Terminal-switch |
|---|---:|---:|---:|
| Selected Beta | 0.1990 | **0.2316** | 0.3700 |
| Full-context Beta | 0.1990 | **0.2316** | 0.3700 |
| Pooled Beta | 0.1864 | 0.2746 | **0.3516** |
| Saturated logistic | 0.1980 | 0.2531 | 0.4754 |
| **Energy factors** | **0.1917** | **0.2511** | **0.4769** |
| Shuffled energy | **0.1617** | 0.3226 | 0.4688 |
| Frozen energy | 0.1761 | 0.4847 | 0.7335 |

Energy's shifted-family score is 0.0195 worse than Beta-selected; it does **not** meet the prespecified 0.01 better requirement. The negative shuffled arm helps in the original invariant family (by 0.0300 Brier) and hurts in the shifted family; no universal anti-shortcut claim follows. The unfamiliar terminal-switch family is a deliberate transfer stress test, not a target for tuning.

### Whole-method cost

Isolated CPU test implementation completed six fits/evaluations in approximately 0.61 seconds wall time. Mean fit times per run (local environment, not optimized end-to-end GPU): conventional Beta 0.00075 s; saturated logistic 0.00126 s; factor-energy 0.00105 s. These tiny costs are not scientifically meaningful runtime comparisons with native CKAD or GPU CRAM. Score timing was excluded from deterministic replay comparisons.

## Audit and classification

- Source SHA and preregistration sealed before score.
- `independent_audit.py` does not import experiment code; it independently reconstructs **1,296 unique held episodes** (144 × 3 families × 3 seeds), each evaluated twice (phase 0 and phase 1), and independently checks the 7 models on each source episode: **18,144 policy rollouts**. It verifies all scored reward counts, transition/terminal Brier, selected first actions and optimizer gradient convergence.
- **73,272 audit assertions PASS**, 126 aggregate arm/cohort rows checked. Independent computational-semantic replay matched after excluding non-deterministic timing metadata.
- **ENGINEERING:** local smoke, freeze, scored replay, independent audit PASS; required native full regression/OS qualification NOT RUN.
- **SCIENTIFIC:** preregistered development thresholds **FAIL**; general learned causal discovery, native Yggdrasil improvement, recurrent neural comparator, independent evaluation and scientific acceptance **UNVERIFIED**.
- **DEPLOYMENT:** none.

## Decision / next useful test

Do **not** replace the native expected-reward planner or promote these hand-selected energy features. The same learned conditional representation is mathematically equivalent to a small logistic classifier. **Design limitation:** its third parity factor is exactly the negative of its first factor, leaving only two independent energy directions. This was identified after scoring and is disclosed without modifying the frozen experiment, thresholds or test cohort, and the held shifted performance does not clear the fitted Beta control. Future science should identify an actually harder, out-of-family conditional consistency problem where both factor priors and independent baseline families can fail, then qualify against the **real native checkpoint** and a trained conventional model, with independent source custody. Preserve this negative rather than re-tuning the frozen results.
