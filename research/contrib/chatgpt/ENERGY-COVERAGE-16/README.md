# ENERGY-COVERAGE-16 — coverage-constrained causal intervention selection

**2026-11-20 | independent Yggdrasil Energy Research contributor | frozen development signal PASS | scientific gain UNVERIFIED | deployment NONE**

## Exact research question
After ENERGY-HYPOTHESIS-15's local selection failure, can a *fixed* local hypothesis-repair learner learn unfamiliar causal changes by forcing broader **distinct intervention-context coverage**, instead of repeatedly choosing a few high-entropy contexts? Compare against the strongest fully fitted Bayes active and random selectors at exactly the same 16 NEW observations/world and same OLD evidence and held outcomes.

The 16-action candidate chooses the highest model-predictive-entropy as-yet-unvisited input among all 32 for its **first 12 actions**, guaranteeing 12 distinct input contexts; remaining four actions are unrestricted maximum-predictive-entropy. **No hypothesis prior, likelihood, repair threshold, fitted estimator, or original learner weights were changed.** This deliberately tests action selection, not a new energy substrate.

## Frozen provenance and isolation
- Same draft, isolated contributor [PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346); accepted main baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Central native cumulative integration authority stays [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- [prereg.json](prereg.json) frozen **first** at `01c67c37c29f885583f858a5692de0171d3407da`, before any source or result.
- [experiment.js](experiment.js) frozen **second** at `d5131e16589f9d701ca252eaaefc0d32fa7968c6`, GitHub source blob **`b72b087a2794d512d5edea63e6acf41008ff93ba`** read back on that commit before smoke and primary. Derived surgically from the GitHub-verified ENERGY-HYPOTHESIS-15 source `963b6f77764ff4bcd570e0ef711ccbf87aabab4c`.
- One smoke on disjoint seed `88289`, 3 families, 12-context constraint and event counts PASS.
- One frozen primary with 12 new seeds `88307..88441` (see exact list in preregistration) × **NULL, SINGLE_EDGE, DOUBLE_EDGE** = **36 worlds**. No reuse of ENERGY-HYPOTHESIS-15 seeds, no new train/test split tuning, no postscore rerun.
- **864 OLD training observations**, **576 NEW consequences per selector arm** (six policies, separately budget-matched), **23,040 held-out binary consequences** paired for all arms, 32 possible intervention contexts, 62 explicit XOR mask+bias hypotheses, 10% known observation noise. Source truth withheld from learners.
- [result.json](result.json) includes all 36 world-level Brier/cost/recovery/false-declaration/coverage measures, aggregate results and preregistered verdict. [audit.js](audit.js) and [audit-result.json](audit-result.json) independently reaggregate the saved results without repeating original outcomes or consumed seed trials: **10/10 arithmetic/cohort checks PASS**.

## Frozen six-arm development result

Held binary Brier, **lower is better**:

| Matched 16-action selector and model | Overall | NULL | SINGLE_EDGE | DOUBLE_EDGE | Changed-mask recovery | Distinct contexts / world |
|---|---:|---:|---:|---:|---:|---:|
| **Candidate local bounded repair + 12-context coverage** | **0.093919** | 0.088551 | 0.104012 | 0.089193 | **95.83%** | **13.31** |
| Same local repair + unrestricted entropy (unmodified predecessor) | 0.143241 | 0.088553 | 0.118554 | 0.222615 | 75.00% | 7.78 |
| Fully fitted Bayesian information-gain active planner | 0.097209 | 0.110379 | **0.092081** | 0.089166 | **100.00%** | 13.67 |
| Fully fitted Bayesian deterministic random actions | 0.097002 | 0.089619 | 0.111308 | 0.090077 | 91.67% | 12.69 |
| Fully fitted Bayesian + same 12-context coverage | 0.094309 | **0.088542** | 0.105229 | 0.089155 | 95.83% | 14.36 |
| Local repair + *exact* full-Bayes IG action/outcome trace | 0.097112 | 0.110392 | 0.091778 | **0.089166** | **100.00%** | 13.67 |

- Candidate vs same local learner with unrestricted action choice: overall Brier reduction **0.049322**, or **34.4% relative**; DOUBLE_EDGE Brier reduction **0.133422**, or **59.9% relative**, with **no per-scenario degradation >0.010**.
- Candidate vs standard fully fitted Bayesian active planner: apparent Brier **0.003290 lower on this one synthetic cohort**. This small apparent win is **not** a statistically or independently qualified scientific advantage; the full Bayes model uses the correctly specified model family, and finite-world noise permits positive/negative realized score differences.
- Stronger coverage control: full Bayes with the same constraint achieved **0.094309**; it nearly tied candidate (**0.000390** score difference). This limits claims of a *distinctive local-repair intelligence mechanism*: broadly probing new situations appears to be the key intervention.
- Candidate changed-mask recovery **23/24**, compared to unmodified local **18/24**, full Bayes IG **24/24**, fully fitted random **22/24**, and full Bayes coverage **23/24**. Candidate and unmodified local had **0/12 NULL false-change declarations**; full Bayes IG produced **1/12**, also not a scientific win for the local mechanism.
- Candidate fit+decision+held-readout cost proxy = **12,319 counted hypothesis evaluations/world**; standard full Bayes IG = **39,184**, **3.181×** ratio. **This is NOT measured CPU/wall-clock/GPU speed, device cost, or whole-process efficiency gain**. Fully fitted Bayesian random decisions used fewer counted operations than the candidate, so no broad compute-superiority claim.
- OLD readouts survived **36/36 same-process JSON serialization/reparse checks**. This is *not* independent-process cold functional restoration, native cumulative-memory retention, or after-learning transfer to other worlds.

## Preregistered disposition
All eight frozen development boolean conditions passed: improvement over local unrestricted, full Bayes-IG tolerance overall and per family, >=12 novel contexts per world, exact action budget, >=2.0× counted-operation ratio vs Bayes IG, >=80% changed recovery, <=5% NULL false-change rate and OLD JSON snapshot readout integrity.

**ENGINEERING:** frozen protocol-before-source and exact Git source readback, one smoke and one primary, bounded audit **PASS**. Original trace archival, independent experiment-source replication, full final regression on exact candidate, production hardware runtime and native cold restoration are **UNVERIFIED**. The prior [G29 failure](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44790584450) failed Linux/Windows on `scripts/build_code_atlas.py --check-if-present`: stale generated source-set index, not an energy-science verdict.

**SCIENCE:** **DEV_SIGNAL_UNQUALIFIED**, not `SCIENTIFIC_PASS`. The value of intervention coverage is supported by this frozen synthetic contrast; originality beyond conventional coverage controls, real unfamiliar-world generalization, native continual knowledge learning, uncertainty calibration and independent reproducibility are unresolved. Do not claim RSI/autonomy.

**DEPLOYMENT:** **NONE**; no native learned-state, central Amalgam integration, accepted main, protected experiment, owner loop, runner, controller, schedule, checkpoint promotion, merge or paid API.

## Next distinct high-value qualification
Independently reproduce coverage-vs-entropy on **fresh, source-sequestered worlds** using a separately authored simulator and strong *fully trained* conventional active controls; test sustained shifts, delayed observations, and actual independent-process cold functional restoration. Freeze random source, compute-matching and full runtime accounting before first use. Only then present a narrowly scoped qualified native integration interface to the **existing Amalgam owner**. No extra stage or merge is implied by this successful synthetic development signal.
