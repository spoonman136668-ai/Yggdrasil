# ENERGY-TRANSFER-17 — independent-source simulator robustness falsifier

**2026-11-20 | isolated Energy Research contributor | engineering frozen-source/audit PASS | scientific NO-GO | deployment NONE**

## Question and methodological distinction

Does ENERGY-COVERAGE-16's coverage-constrained local hypothesis repair survive a separately written simulator, higher observation noise, additional nonlinear causal changes outside its fitted representation, and stronger conventional Bayesian controls?

**This is a separate implementation by the same research assistant, not an independent scientific operator or external protected-source test.** The 48 primary worlds, source-law counter stream, posterior and action-selection implementation were frozen before one primary. All outcomes are synthetic. Its gains are not native Yggdrasil cognition, energy efficiency, cold retention, scientific acceptance or transfer from grounded human-world knowledge.

## Exact-source custody and pre-registration

- Existing isolated [Yggdrasil draft research PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346), accepted-main reference `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`; native integration remains only with the authorized [Amalgam #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278).
- Preregistered [prereg.json](prereg.json) at commit **`484ae238fa629b47e639572375480ba05b46031e`** before any new executable source.
- Authored [experiment.js](experiment.js) independently of the prior source (no imported prior algorithms), frozen at commit **`bc98a372acc05a196ac96b9817aef4b13164e50b`**, GitHub blob **`70d960ca7483e258f0fbde9e02a646f86ee8453e`** read back at exact head **before** smoke and primary.
- Separate, single frozen smoke seed `88501`: four family worlds, counts, cohort and action-coverage checks PASS.
- Single consumed primary: **12 new seeds** (exact list in prereg) × **4 causal families** = **48 worlds**, 32 binary intervention inputs, 62 possible nonzero XOR masks/biases, 15% known flip noise.
- **1,152 OLD** observations across worlds, **768 NEW** observations *per arm* across seven arms, **30,720 paired held consequences** scored equally on each arm. Models observe no true source mask/nonlinear gate. Every coverage arm must select >=12 unique contexts in each world.
- Four scenario families: NULL, SINGLE_EDGE, DOUBLE_EDGE, and **NONLINEAR_AND**, with the latter's NEW law adding an unmodeled AND interaction outside all 62 candidate XOR hypotheses.
- Stronger conventional controls: MAP-prior full Bayesian information-gain and coverage, plus full Bayesian OLD-posterior marginalized information-gain and coverage, plus full all-hypothesis random actions. With constant known binary observation noise, maximizing Bernoulli predictive entropy **is** exactly maximizing one-step expected information gain for hidden XOR hypothesis, up to the constant observation conditional entropy.
- Saved [result.json](result.json) has world-level paired action traces, cohort metrics and frozen decisions. Independently written [audit.js](audit.js) reads only saved results, verifies paired actions, scores, sample budgets, and cohort membership; [audit-result.json](audit-result.json) **11/11 arithmetic checks PASS**. It does not independently rerun the experiment.

## Results (held binary Brier; lower is better)

| Model / action policy | Familiar XOR worlds (36) | Nonlinear AND worlds (12) | Changed XOR recovery (24 worlds) | NULL false change (12 worlds) |
|---|---:|---:|---:|---:|
| Full 62-hyp MAP-prior Bayes information gain | **0.141231** | 0.211157 | 87.50% | 4/12 |
| Full 62-hyp marginalized-OLD Bayes information gain | 0.142115 | 0.217157 | **95.83%** | 4/12 |
| Full 62-hyp MAP-prior Bayes + coverage12 | 0.157751 | 0.223998 | 83.33% | 4/12 |
| Full 62-hyp marginalized-OLD Bayes + coverage12 | 0.146456 | 0.221312 | 87.50% | 4/12 |
| Full 62-hyp deterministic random actions | 0.157631 | 0.231478 | 91.67% | 5/12 |
| **Local repair + coverage12** | **0.168031** | **0.200859** | **75.00%** | **4/12** |
| Local repair + unrestricted entropy | 0.200699 | 0.218515 | 70.83% | 3/12 |

### Exactly what passed or failed

**PASS, bounded:** local coverage improved over the same local learner without coverage by **0.032668 familiar-world Brier** and **0.045565 DOUBLE_EDGE Brier**. In NONLINEAR_AND, local coverage reduced Brier **0.017655** versus the local unrestricted selector and was better on this single cohort than the strongest conventional fitted comparator's 0.211157. All 48 worlds met >=12 distinct coverage contexts, every arm used exactly 16 actions, and the derived hypothesis-evaluation operation proxy was favorable: conventional marginalized Bayes IG 42,036 vs local coverage 13,606, a **3.09× ratio**. This is not an actual measured runtime or energy benefit.

**FAIL against strongest control:** candidate familiar-world Brier **0.168031**, best fitted full-Bayesian IG **0.141231** (candidate worse by 0.026799, beyond allowed +0.015); important per-family score gaps exceeded the frozen tolerance.

**FAIL on known causal shift recovery:** local candidate exactly recovered **18/24 changed parity mechanisms = 75.0%**, below frozen >=80%. Full Bayesian marginalized IG recovered **23/24 = 95.83%**.

**FAIL on unchanged-causal false alarms:** local candidate declared changes in **4/12 NULL worlds = 33.3%**, vs frozen <=5%. Several *full conventional Bayesian* arms also had 4/12 NULL false declarations; this suggests the current structural-change declaration and fitted model are weak under this synthetic regime, and does not isolate the local-selection mechanism as the only problem.

**NO-GO:** 3 of 9 frozen development criteria fail (strongest conventional score tolerance, parity recovery and false-alarm rate). The separate arithmetic auditor **11/11 PASS** means the saved negative scores are internally coherent, not that the hypothesis succeeded.

### Why Gate 16's finding was insufficient

ENERGY-COVERAGE-16 showed a strong single-cohort coverage signal on an earlier simulator with 10% flip noise, and a closely matched full-Bayesian coverage arm almost tied. ENERGY-TRANSFER-17 changes both simulator and noise level and adds out-of-family nonlinear mechanisms. The coverage intervention benefit persisted *within the local learner*, but the strong-conventional and reliability requirements did not. The data therefore cannot establish that higher noise alone caused the failure, and nonlinear mean advantages from 12 synthetic worlds are too weak for generalizable superiority claims.

**Functional-retention boundary:** 48/48 OLD posterior/readout objects survived a same-process JSON serialize/parse check, but were not cold-reloaded by a different process, used to drive a native persistent learner, or subjected to interference tests. No native cumulative retention was demonstrated.

## Status and corrective direction

**ENGINEERING:** Prereg before source, exact-source Git blob readback before one smoke and one primary, all original summary/trace records in GitHub, independent arithmetic/cohort audit PASS. No independently operated source simulation or full Python/JS native cross-platform final regression was completed. The unrelated preexisting [G29 atlas source-index check](https://github.com/spoonman136668-ai/Yggdrasil/actions/runs/44791865700) failed both OS on an earlier head. The current final-head CI result must be read separately. This is a source-set/index engineering limitation, distinct from negative science.

**SCIENTIFIC:** **NO-GO**. No warranted gain in general causal discovery, long-term retention, hardware efficiency, or autonomous intelligence. The next *distinct* test should first isolate change detection/calibration at fixed actions, strong posterior predictive controls and a reserved out-of-family cohort; do not tune on or replay these consumed seeds. Prefer stricter NULL false-declaration controls before experimenting with further intervention heuristic changes. Native Amalgam qualification only after independently operated reproduction on novel source truth.

**DEPLOYMENT:** **NONE**. Draft PR only; no accepted main, model learned-state update, original-source first-use, checkpoint promotion, runner, controller, scheduled task, merge, paid API or owner operational change.
