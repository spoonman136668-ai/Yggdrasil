# ENERGY-DELAY-07 — Delayed intervention versus immediate confounding

**2026-11-20 · Independent, source-free, tokenless-directed-energy research · SCIENCE: MIXED / NO-GO · DEPLOYMENT: NONE**

Research folder added to existing [Yggdrasil draft PR #1346](https://github.com/spoonman136668-ai/Yggdrasil/pull/1346) at accepted-main baseline `5e74f8db85b2f5839c42148c0dfba69a88b1a2c9`. The only canonical cumulative native learner remains with [Amalgam PR #1278](https://github.com/spoonman136668-ai/Yggdrasil/pull/1278). This contribution does **not** integrate or train that learner.

## Why this experiment, not another staged-memory copy

Read-only inspection of the central Amalgam branch `86264b41a08d49f558418c0fba367f3a2636befa` found overlapping tests of context retrieval, unsignaled contexts, checkpoint replay, open-set transfer, staged retention, and outcome-probing. The central staged-retention study reported DEV_NO_GO: additional adaptation damaged familiar predictions and lost to a fitted change-point control. We therefore **did not create a second canonical/context-memory learner or repeat that experiment**.

This independent falsification asks a different question: can an *energy-inspired lagged action-effect estimator* distinguish an actual **delayed causal intervention effect** from the misleading immediate and lagged correlations caused by a nuisance variable and biased observational action assignment?

## Frozen synthetic intervention setup

Each world has two **explicit public context labels** (OLD then NEW), three binary future outcome timestamps (lag 0/1/2), action 0/1, and a hidden nuisance bit U. Public proxy Z reports U correctly with probability 0.9. Noncausal outcomes have success probability 0.8 or 0.2 depending on U. Observational actions are biased toward U 90% of the time, but **24 interventions per context** are randomized independently of U.

In every scenario OLD context learns a genuinely lag-1 action effect with action 1 favorable (0.85 success versus 0.15). NEW context is one of: CONTRADICT (opposite sign, same lag 1), DELAY_SHIFT (favorable action 1 only at lag 2), or NULL (no action effect). Each context receives 24 confounded observational plus 24 randomized-intervention episodes, then 256 held randomized episodes per context. A world has 96 public training episodes and 512 held episodes with 1,536 binary held outcomes.

The candidate is bounded: from *intervention-only* action contrasts, select the largest absolute Beta(.5)-smoothed directed lag flux. Declare an effect only if its magnitude is >=0.30. At the chosen lag predict success .80 for the inferred beneficial action, .20 for the other. Other timestamps predict through public-proxy-stratified nuisance counts estimated on the public training stream. It keeps separate fixed OLD/NEW entries and cannot see the true lag, sign, U or scenario label. **Context labels are provided**, so retention in this experiment is not discovery of an unknown context.

The controls are fully fitted intervention-only Beta, proxy-stratified intervention Beta, all-data proxy-stratified Beta, nuisance action-blind Beta and immediate-only Beta. A **correctly specified seven-hypothesis temporal Bayesian reference** over NULL and all (lag, sign) possibilities is an oracle-class *reference bound*, excluded from the non-oracle superiority target under the exact-Bayes Brier identity. The privileged truth oracle has hidden U and is likewise only a lower bound. Every non-oracle learner sees the same training witnesses, public intervention assignment and held actions.

## Source freeze and execution sequence

1. [Preregistration](prereg.json) first committed `eaae907828bbfeb365e39669774d476967134686`. Two **prescore clarifications** established proxy-aware nuisance treatment and correctly excluded the source-family Bayesian reference from the superiority target. Final prereg at `3f6988955faf0acdb938a78af4c851c4dc8e4c71`, **before executable source**.
2. [Exact frozen executable](experiment.mjs) commit `299f728e0fb6b397300286c935350cbdc7736193`, Git blob `b6b282dfea714bc22b709058534e4bec49c9cc78`. Same JavaScript function source was serialized, committed, GitHub fetched and byte-for-byte compared *before* evaluating any smoke or primary worlds.
3. Separate smoke seed `94199`: 3 synthetic worlds, held 4,608 binary outcomes. It tested source identity and data quota, not scientific evidence.
4. **One primary cohort only**: frozen seeds `94211,94219,94229,94237,94243,94253,94261,94273,94283,94291,94307,94319` × 3 scenarios = **36 worlds, 3,456 fit episodes, 18,432 held episodes, 55,296 held binary outcomes**. No previous ENERGY primary seed was replayed.
5. The complete 36-world per-arm loss/causal-decision receipt was committed in [result.json](result.json) at `c953e80472e10e1f9e00e9fc526125e5b8f7b453`, Git blob `517b4ce8025f724d581e1ebf75776a9d3c7ab31e` (75,724 bytes). A separate, [postscore arithmetic auditor](audit.mjs), blob `eee515f3eaf98fdda3cdc7d396badb6b63951cb3`, checked unique world/source identities, evidence budgets, all per-world/scenario/aggregate losses and frozen rule classification against saved data **without re-running consumed primary episodes**: PASS.
6. Do **not** retune the 0.30 threshold, reuse these primary seeds or claim another first-use after seeing the results.

Non-primary smoke-only reproduction:
```bash
node --input-type=module -e "import('./research/contrib/chatgpt/ENERGY-DELAY-07/experiment.mjs').then(m=>console.log(JSON.stringify(m.energyDelay('smoke').summary)))"
```

Postscore **arithmetic audit only**, not replay:
```bash
node --input-type=module -e "import('node:fs').then(async fs=>{let m=await import('./research/contrib/chatgpt/ENERGY-DELAY-07/audit.mjs');console.log(m.auditDelay(JSON.parse(fs.readFileSync('./research/contrib/chatgpt/ENERGY-DELAY-07/result.json','utf8'))));})"
```

## Exact frozen outcome

Average binary Brier over OLD + NEW contexts, all 3 lags; lower is better:

| Arm | Held Brier |
| --- | ---: |
| Privileged U + true law oracle (reference only) | **0.150189** |
| Source-family seven-hypothesis temporal Bayes (reference only) | **0.174523** |
| **Intervention-flux candidate** | **0.183207** |
| Best fully fitted **non-oracle** (all-data proxy-stratified Beta) | **0.192551** |
| Intervention-only proxy-stratified Beta | 0.200048 |
| Action-blind proxy-stratified Beta | 0.221336 |
| Intervention-only unstratified Beta | 0.231367 |
| Immediate-only control | 0.243586 |

The candidate's improvement versus the strongest fitted non-oracle control was **0.009343902 Brier**, **below the preregistered >=0.010 requirement**.

| NEW scenario | Correct lag + direction | Candidate NEW Brier | Source-family Bayes NEW Brier |
| --- | ---: | ---: | ---: |
| CONTRADICT | **12/12** | 0.177878 | 0.168634 |
| DELAY_SHIFT | **12/12** | 0.174896 | 0.169284 |
| NULL | **8/12 correctly abstained; 4/12 false causal declarations** | 0.211737 | 0.192340 |

The four NULL false positives independently **fail the frozen required 0/12 false-effect criterion**. The 24/24 non-null effect diagnoses are encouraging but not scientific PASS. The candidate was also less calibrated than the source-family Bayes reference, as expected for hard lag selection.

The 36 OLD-context predictive readouts survived NEW training and one-process JSON serializing/loading. **This does not prove independently restored native checkpoint retention**, and the public context tags make it a simpler memory requirement than unsignaled context discovery. The episode-indexed lagged outcomes are **not** a continuous dynamical world model: that limitation also prevents claiming native multi-step temporal reasoning.

## Verdict, uncertainty, and next decisive work

**MIXED_NO_GO, not SCIENTIFIC_PASS.** Intervention-only delayed-action learning is feasible in this bounded synthetic demonstration; however, false positive action effects and failure to beat the frozen accuracy margin prevent promotion. Future studies must not rescue this result by relaxing the NULL guard or tuning to these 12 seeds.

A meaningful research follow-up is to develop **evidence-calibrated abstention with blinded intervention-source provenance**, not another source-family memorization exercise, then test out-of-family action-consequence changes and independent-process functional cold retention against well-fitted conventional baselines. This is only a recommendation; no further primary seeds are frozen or scored here.

- **ENGINEERING:** Source GitHub readback PASS; postscore math audit PASS; exact process resource cost, independent native cold restore and dual-OS G29 Atlas PASS **UNVERIFIED/FAIL** (separate repo-wide guard).
- **SCIENCE:** Frozen 36-world result MIXED_NO_GO; potential but not qualifying delayed intervention effect signal; no generalized causal intelligence or native benefit demonstrated.
- **DEPLOYMENT:** NONE. Accepted `main`, Amalgam, owner checkpoint, runner, controller, schedule, model training and production remain unchanged.
