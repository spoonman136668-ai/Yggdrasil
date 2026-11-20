# ENERGY-27 — Falsifying information-gain acquisition in causal constraint learning

**Date:** 2026-11-18. **Final status:** `DEVELOPMENT_NO_GO` on a prospectively frozen corrected R1 cohort. **Engineering:** local independent source audit PASS; original native Yggdrasil regression NOT EXECUTED. **Scientific:** no distinctive energy-model advantage, no retention/transfer acceptance. **Deployment:** NONE.

## Why this experiment was needed

ENERGY-23 showed abstract candidate probabilities where forecast disagreement and information gain choose different interventions. ENERGY-24 tested a separate two-candidate source and found no downstream gain. ENERGY-25/26 trained causal-rule learners from a *passively selected* 16-intervention evidence set and found energy models failed to outperform exact, fully fitted Bayesian causal rules. This gate tests the distinct remaining mechanism: **actively choosing which unknown causal relation to interrogate**, with the same six actual action-consequence observations per learner and disjoint held intervention patterns.

For fixed symmetric binary observation error e and deterministic candidate hypotheses, let q be the posterior probability of a positive causal outcome, and m=e+(1-2e)q. Then:

- Forecast disagreement variance: **V=(1-2e)^2 q(1-q)**.
- Information gained about the hidden hypothesis: **I(H;Y|a)=H₂(m)-H₂(e)**, where H₂ is binary entropy.

Both functions reach their maximum when q=1/2, and induce the same ordering of actions at fixed e. **Consequently, replacing disagreement with information gain cannot improve acquisition in a constant-error deterministic binary-rule world.** With intervention-dependent noise the rankings *can* differ; the frozen primary asks whether that distinction matters after real learning.

## Frozen causal task and strong controls

- Five binary action variables, an evaluator-secret signed XOR relation on one of ten possible three-parent triples (**20 causal laws**), and **six distinct actions per world** actively selected from 24 eligible configurations. Eight other intervention configurations were held out from **every** acquisition arm; learning never receives their answers. Truth and action-conditioned noise are strictly source-side; predictors only see the actual public intervention and the observed outcome.
- Six independently disjoint R1 seeds (`1543`, `1549`, `1553`, `1567`, `1571`, `1579`) ×20 laws ×two observation conditions = **240 worlds**; three acquisition policies per world = **720 model/evaluation cases**, **4,320 genuinely executed synthetic probe consequences**, and **5,760 scored held outputs** across arms.
- Homogeneous corruption flips public outcomes with fixed probability 10%. Heterogeneous corruption flips them with 2% probability when first intervention bit is zero, and 35% when it is one. These error rates are **publicly specified** to every learner, not the hidden causal law.
- All arms learn a **fully fitted exact finite 20-rule Bayesian hypothesis posterior** from *their actual witnessed* outcomes. An equivalent normalized classical-energy encoding `exp(-E_h) ∝ prior_h × product P(observed consequence | h, action)` matches it by construction, so it is NOT a new learned architecture. Separately inspect a hard best-hypothesis readout and a completely refitted conventional cubic ridge readout on the **same chosen receipts**. A hash-deterministic, no-hidden-rule random acquisition control receives the same six-action budget.
- The frozen R1 gate demanded >=29 extra correct of 960 heterogeneous held predictions for information gain vs disagreement, positive paired gain in at least four of six seeds, no seed loss worse than eight held examples, and identical predictions/actions in the homogeneous negative control. The comparator is an **acquisition-policy test**, not an energy-model superiority trial.

## Final corrected R1 primary (not the excluded first score)

| Observation regime | Disagreement / variance | Exact expected information gain | Random acquisition |
|---|---:|---:|---:|
| homogeneous | 828/960 (86.25%) | 828/960 (86.25%) | 812/960 (84.58%) |
| heterogeneous | 936/960 (97.50%) | 936/960 (97.50%) | 705/960 (73.44%) |

Both informed methods chose **identical full six-action sequences in all 120/120 homogeneous and 120/120 heterogeneous matched worlds**, despite theoretical ranking differences being possible when e depends on action. The information-gain arm has **zero additional successes**, zero seed-specific gain, and identical held Brier to the variance arm. It therefore **FAILS every positive-gain requirement**. The homogeneous equality negative control PASS.

Under the heterogeneous source, hard-MAP held accuracy was 933/960 and conventional cubic ridge 638/960; posterior mixture scored 936/960. Rule identification reached 115/120. These results support retaining uncertainty rather than committing to a single hypothesis, but do not imply generic causal reasoning or native model improvement. Random-acquisition differences are **different witnessed intervention choices**, not matched identical receipts; they measure acquisition behavior under equal action budgets, not a fitter comparison.

Local CPU wall charged for each arm's source fitting, acquisition and held readout, summed over 120 worlds per regime: homogeneous disagreement 0.0345s, information gain 0.0456s; heterogeneous disagreement 0.0355s, information gain 0.0454s. These sub-second Python process-dependent timings are not native or GPU speed qualification.

## Audit, replay, and provenance

**Frozen R1 source SHA-256:** `acc8df1a62dc7dddf53ae9766ba90961a989fc22f83e7a59c6961c0c9927bb92`. **Frozen R1 protocol SHA-256:** `35d22fedcbefbdeb5325f4c64faed222358d67e8ff8230ba4f69360c3ca8d482`. The source and protocol were frozen before R1 scoring, and the R1 cohort had no overlap with the preceding pilot or initial invalid score.

- **51,935 independent audit checks PASS**: an auditor written after scoring, without importing the scorer, regenerated all true parent laws and SHA-keyed public outcomes, verified **every intervention was selected before its outcome**, recomputed 4,320 updates to 20-rule posteriors using exact rational arithmetic, checked all 5,760 held truths/predictions, independently refitted conventional ridge using augmented least squares (the scorer used normal equations), and checked all classification/aggregate/count receipts.
- **Semantic replay PASS:** a fresh exact-source run generated the same result SHA-256 `16827f89476c0801905cef80c8fb54f9c615e25bce86c7b29fac149266f69dac` after excluding nondeterministic timing fields. This is a deterministic local repeat, not external CI.
- **First score excluded:** The initial six-seed cohort had `uniform_random` seeded by the private source causal-law ID (hidden information in the action selector's hash, even though cryptographically masked) and noisy float signs around exact half-probability ties. The first post-score exact auditor stopped on a tie. The entire initial score, source, freeze, failure and diagnostic are preserved separately under `initial-invalid/`. **Neither initial result nor its audit is accepted as primary qualification.** R1 changed only the random-control seed to depend on seed/regime/public step and made numeric half-probability and MAP ties deterministic, then used six fresh primary seeds; original protocol success thresholds were not optimized or relaxed.
- A small non-scoring pilot on seed9001 after the initial 12-probe smoke reduced the training budget to six **before the initial frozen score**, avoiding a trivial ceiling; source/protocol and pilot receipts are retained. R1 preserves the six-probe design.

## Native Yggdrasil implications and final decision

**DO NOT integrate information-gain action selection into CKAD on this evidence.** In the current 20-rule conditional causal task, the existing disagreement policy captures the same interventions and held performance as information gain, while information gain takes more local computation. The strong Bayesian causal rule control is *identical* to normalized energy posterior algebra; no energy-specific learning gain exists here. A further trial is justified only for a new causal hypothesis family with calibrated variable uncertainty, active information **outside** the current rule bank, matched newly trained conventional/native controls, genuinely disjoint native source actions, retained prior knowledge and separate full process cost.

**ENGINEERING:** local frozen R1, independent audit and semantic replay PASS; native Linux/Windows regression **UNVERIFIED**, G29 CI status must be checked separately. **SCIENTIFIC:** `DEVELOPMENT_NO_GO`, protected first-use 0, real-world actions 0, scientific_pass=false. **DEPLOYMENT:** NONE; no main, model, controller, runner, research loop, merge or accepted checkpoint modified.
