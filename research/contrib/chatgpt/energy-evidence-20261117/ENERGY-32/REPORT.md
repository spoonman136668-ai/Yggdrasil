# ENERGY-32 — Independent repeat interventions to separate observation noise from causal change

**Date:** 2026-11-18. **Classification:** `DEVELOPMENT_NO_GO` on frozen source-free synthetic development cases. **Native Yggdrasil checkpoint:** NOT EXECUTED. **Scientific pass:** false. **Deployment:** NONE.

## Scientific question

ENERGY-30 and ENERGY-31 showed that surprise-sensitive causal novelty triggers are either too aggressive under noisy familiar observations or too conservative when actual causal relations change. ENERGY-32 tests a different causal signal: request an **independent second outcome at exactly the same intervention**, and treat two matching disagreements with a confident old-model prediction as stronger evidence of structural change than a single improbable observation. A repeat costs a real observation; the source enforces **equal total evidence budgets** rather than giving the tested mechanism a free second label.

This is an explicit finite Bayesian model over a known 160-rule grammar: 40 signed XOR3 familiar causal functions and 120 signed XOR3-plus-AND2 composite functions. It does **not** establish an energy-specific method, novel grammar invention, native CKAD training or a general intelligence result.

## Frozen source and controls

All 240 primary cases come from **four new seeds 5021, 5039, 5051, 5059 × 20 old causal laws × three schedules**. The schedules are stationary unchanged rules, a change to a new composite causal law, and a switch to a different familiar law. Hidden causal law, noise, and change status remain evaluator-side. A public learner sees only six-bit intervention choices and resulting binary observations. Source outputs independently flip with Bernoulli 15% observation noise, each repeat from a new independent SHA-256 draw.

Each case has **24 distinct old-rule witnessed interventions, then 8 distinct challenge interventions repeated twice (16 additional actual consequences), and 12 never-seen disjoint held interventions**, so all learned methods use precisely the same 40 observed action/outcome pairs. The trial tests predictions of the **noise-free consequence** on held actions, with no held updates. No physical or original Yggdrasil source action takes place.

Methods: (1) full-history Bayes with no reset, (2) a single observed outcome with posterior likelihood below 0.18 triggering one reset, (3) two identical contradictory repeat outcomes with old predictive confidence at least 0.80 triggering one reset, (4) fully fitted exact Bayesian renewal hazard 1/48 per observation, (5) Bayesian last-16 observation window, and (6) a **privileged change-at-phase-boundary oracle**, explicitly not an information-matched competitor. All use prior mass 7/8 familiar and 1/8 novel and the same 160-rule prediction grammar. The original Bayesian mixture can be written as a normalized energy; there is no distinctive energy architecture.

**Before primary scoring**, `protocol.json`, `experiment.py`, and the original `independent_audit_v1.py` were SHA-256 frozen in `freeze.json`; separate smoke seed 99991 was run and audited. The original frozen development gates require (i) paired-confirmation held accuracy at least +3 percentage points over single surprise in **both** true-change scenarios, (ii) at most 10% false paired alarms on stationary cases, (iii) at least fixed-hazard held accuracy in all three scenarios, and (iv) at least 95% stationary held accuracy. No threshold, seed, or scoring code changed after primary scoring.

## Primary result

| Scenario, 80 worlds each / 960 withheld interventions | Full history | Single surprise | Paired confirmation | Exact fixed hazard | Recent 16 | Privileged oracle |
|---|---:|---:|---:|---:|---:|---:|
| Stationary unchanged rule | **949** | 757 | **882** | 938 | 757 | 949 |
| New composite causal rule | 495 | **635** | **631** | 587 | 635 | 635 |
| Switch to different familiar rule | 569 | **791** | **789** | 754 | 791 | 791 |

**False alarms on 80 stationary cases:** single-surprise 76/80 (95%), paired confirmation 15/80 (18.75%). This is a substantial 61-world decrease, but still misses the frozen <=8/80 (10%) false-alarm limit. For genuine changes, the paired mechanism triggers in 77/80 novel changes and 78/80 familiar switches, yet its final accuracy is **4 and 2 fewer correct** than the single-surprise rule, respectively. Exact fixed-hazard Bayes is **56/960 more accurate** than paired confirmation when nothing changed, despite lagging after real changes; strong contextual controls are necessary. Full history retains **949/960** stationary held correct without any resets.

**Frozen development gates:** all four `false`, so **DEVELOPMENT_NO_GO**. This is not a scientific performance or transfer result, and a reduction in false alarms alone cannot override missing reward/retention requirements. No post-result tuning on the scored sources.

## Independence, numerical caveat and reproduction

The independently written scalar-Python auditor reconstructs all 240 source truths, seed-keyed action partitions, independently noisy duplicate observations, the 160 candidate rules, six posterior decision models, all **17,280 held predictions**, aggregate metrics, and retained-state/first-use boundaries without importing the NumPy scorer. The primary scoring and a fresh replay are **semantically identical for all 240 cases** after excluding only `wall_seconds` (SHA-256 of canonical semantic JSON `9400993054ec808bcf402320647c051c77bca45ee7cd11970eeb7052ce51478f`).

The **original frozen independent auditor failed** on nine predictions in its cross-implementation comparison: scalar floating sums and NumPy summation classified posterior probabilities mathematically **exactly 1/2** on opposite sides of the strict `>0.5` threshold. The original failure and frozen source bytes are retained, without altering the primary scored file. A **separate post-score exact-integer likelihood certificate** verifies 17 mathematically exact half-probability predictions across all cases, including **all nine mismatched readouts**. The post-score qualified auditor matches the remaining 17,271 held decisions directly, checks nine ambiguous decisions have exact 1/2 rational forecasts, checks the recorded label/counts on those ties, reconstructs all scenario totals and frozen pass/fail results, and reports **50,880 source/invariant checks**. This is a post-score numerical qualification, not a preregistered new scientific experiment. It neither changes nor cherry-picks the frozen result; all four frozen gates remain failed beyond the rounding ambiguity. The limited fixed-hazard arm had no auditor disagreement.

No cross-platform or native Yggdrasil regression was run here; recorded source local runtime includes only this synthetic CPU process. No justified end-to-end speedup or autonomous-training claim.

Reproduce in Python 3.12+ with NumPy:

```bash
python -B experiment.py --smoke --out smoke_recheck.json
python -B independent_audit_v1.py smoke_recheck.json
python -B experiment.py --out primary_recheck.json
# Confirm primary_recheck.json and scored.json agree after removing wall_seconds.
# The original independent_audit_v1.py on scored.json fails on documented exact ties.
python -B numerical_tie_certificate.py
python -B postscore_independent_audit.py scored.json
```

## Decision and boundaries

**ENGINEERING:** Frozen source/protocol hash checks PASS; deterministic semantic replay PASS; original independently refitted audit **FAIL at exact numerical ties**, separately qualified post-score audit **PASS WITH NUMERICAL CAVEAT**. Evidence preserved in original ZIP and repository. Mandatory native Linux/Windows full regression and independent acceptance **UNVERIFIED**.

**SCIENCE:** `DEVELOPMENT_NO_GO`. Repeat interventions substantially reduce false change alarms, but the tested rule still forgets familiar knowledge too often and provides no gain over strong controls after true structural changes. This test does not establish a new native knowledge or learning gain. The unresolved question is how to retain uncertainty and calibrate false alarms without trusting a single pair of contradictions; further threshold tuning against these consumed seeds is prohibited.

**DEPLOYMENT:** NONE. No native learner edit, accepted source promotion, protected first-use, merge, research loop, runner, scheduler or controller mutation.
