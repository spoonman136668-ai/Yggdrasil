# ENERGY-HYPOTHESIS-15 — bounded causal-hypothesis repair and intervention selection

**2026-11-20 · Contributor-only · ENGINEERING bounded audit PASS / full CI UNVERIFIED · SCIENCE NO-GO · DEPLOYMENT NONE**

## Decision
The fixed-budget, structural-repair learner **did not** pass its preregistered useful-accuracy and changed-relationship identification thresholds. It used fewer **counted hypothesis evaluations** but did not demonstrate faster hardware runtime, native retention, accepted Yggdrasil intelligence growth or model improvement.

## Frozen execution custody
- Existing draft research PR [#1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346); accepted main at branch baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. Sole native Yggdrasil cumulative learner integration remains [Amalgam #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- Protocol was committed *before executable source*: `d53520fee65ee7254fc1086a0cd71388e98c9be9` (`prereg.json`).
- Executable `experiment.js` was committed second at `99c1ff1ed15cb7c09ff8f663c1584739df296ae2`, then GitHub read-back-verified, source Git blob `963b6f77764ff4bcd570e0ef711ccbf87aabab4c`, prior to any smoke or primary execution.
- Disjoint smoke: seed 88091, 3 scenario worlds, protocol-integrity checks PASS. One primary: 12 frozen seeds × NULL/SINGLE_EDGE/DOUBLE_EDGE = **36 worlds**. **864 OLD observations**, **576 NEW intervention outcomes per arm**, **23,040 held binary outcomes** shared for all arms. No primary reruns or post-result tuning.
- Frozen results and all world-level metrics: [result.json](result.json). One separate postscore arithmetic audit: [audit.js](audit.js), [audit-result.json](audit-result.json), **12/12 arithmetic/cohort checks PASS**. This auditor does not independently regenerate outcomes or prove an exact full scientific replica.

## Results: held binary Brier (lower is better)

| Method | Overall | NULL | SINGLE_EDGE | DOUBLE_EDGE | Exact changed-mask recovery |
|---|---:|---:|---:|---:|---:|
| Full Bayesian IG active, correctly modeled | 0.099020 | 0.089927 | 0.095931 | 0.111203 | 95.83% |
| Full Bayesian deterministic random action | **0.098942** | 0.091417 | 0.105969 | **0.099440** | 95.83% |
| Bounded structural repair, local action selector | 0.136666 | 0.089900 | 0.095932 | **0.224166** | 79.17% |
| Bounded repair, *same* Bayes-IG action/outcome trace | 0.099063 | 0.089912 | 0.095934 | 0.111342 | 95.83% |

**Falsification:** local active repair lost **0.037646 Brier** to matched full Bayes IG, violating the frozen maximum +0.015 loss-gap. Its 79.17% changed-mask recovery fell short of 80%. The DOUBLE_EDGE unfamiliar two-change case was particularly poor: 0.224166 versus 0.111203. Conventional random actions were slightly better than Bayesian IG on overall Brier in this frozen cohort; no assertion that Bayes IG won all comparators.

**Mechanistic diagnostic:** When trained on the exact Bayesian active action/outcome trace, the same local hypothesis-repair model had Brier 0.099063, only **+0.000043** versus its fully fitted Bayes IG counterpart. In contrast, choosing interventions itself produced 0.136666. Local intervention selection visited only **7.75 distinct contexts per world**, compared with **13.75** for full Bayesian IG and 13.14 for full-Bayesian random selection. This implicates narrow, repeated local committee-disagreement queries; it does **not** conclusively prove the sole cause without a separate frozen action-selection ablation.

**Cost and retention:** active local cost 13,295 counted hypothesis evaluations/world versus full Bayesian IG 39,184, or **2.947x fewer abstract operations**, not a measured CPU/GPU/wall-clock speedup (no device or whole-process matched resource qualification). NULL false-change declarations: **0/12**. OLD predictions survived **36/36 JSON serialization/reparse checks within the same executing process**; not an independent-process cold restart, native function restoration or learning retention.

## Engineering / scientific / integration boundaries
**Engineering:** protocol-before-source, exact Git source-blob readback, frozen smoke and primary, bounded results committed, and separate arithmetic auditor PASS. Independent original simulation reproduction, full raw action-trace custody, environmental performance measurements, complete final regression and dual-OS CI acceptance remain **UNVERIFIED**. Earlier [G29 run 44782479527](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44782479527) failed Linux/Windows at the **generated atlas indexed source set**; that check is an engineering index blocker, not scientific superiority evidence.

**Science:** **NO-GO**, no new established generalized causal reasoning. Exact Bayes with correct generative assumptions is a strong synthetic information/accuracy reference, not a claim of real-world transfer or an expected bound to beat. This is a finite synthetic development falsifier, not a qualified native learner experiment.

**Deployment:** **NONE**. No native checkpoint, controller, runner, accepted main, merge, protected first-use, live environment or central Amalgam integration changed.

## Next distinct scientific test
Pre-register **coverage-constrained active hypothesis discrimination**, comparing local posterior-entropic selection with a novelty/coverage penalty, fully fitted Bayesian IG, deterministic random, and exact matched-trace ablations on **fresh disjoint worlds**. Hold the model and 16-action budget fixed; test whether covering genuinely distinct contexts rescues DOUBLE_EDGE discovery *without sacrificing NULL stability*, and measure hypothesis evaluation cost separately. Do **not** tune on or rerun ENERGY-HYPOTHESIS-15 primary seeds.
