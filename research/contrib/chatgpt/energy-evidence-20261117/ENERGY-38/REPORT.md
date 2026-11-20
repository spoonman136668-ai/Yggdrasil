# ENERGY-38 — Exact causal effects learned per unit of policy computation

**Date:** 2026-11-18. **Pre-registered external contributor research.** **Decision: DEVELOPMENT_NO_GO.** No native Yggdrasil training, scientific first-use, accepted-ref changes, research-loop/controller changes, merge, or deployment.

## Research question and mechanisms
ENERGY-33–37 repeatedly found that using classical energy formulations for model selection or active witness acquisition did not pass stronger conventional-control, generalization and cost gates. ENERGY-38 changes the evaluator from ordinary action-label prediction to **exact causal intervention-effect prediction**, on three source mechanism families rather than repeating the same old grammar and scores.

The full candidate is *one-pass sparse-energy action selector + a separately fully trained sparse-energy learner*. The selector uses one contrastive source gradient on 48 witnessed familiar-context (x0=0) actions, keeps the 12 strongest factor coordinates, and chooses 12 unseen x0=1 candidate interventions by learned uncertainty plus small Hamming diversity. Only *after choosing* those 12 actions does the learner observe their noisy outcomes. All policies see 60 real action-consequence observations and predict 48 **disjoint held suffix pairs** under both x0=0 and x0=1, producing a predicted causal effect in {-2,0,+2}. Exact effect agreement is required; predicting one label alone is not sufficient.

Controls use the same 48 prior outcomes and pool of 48 possible new actions: fully trained OMP12 uncertainty, Ridge predictive leverage, Hamming-diverse selection, and deterministic random selection. Each selector's acquired 60 observations train four distinct downstream learners: energy, OMP12 (same 12 active coupling limit), Ridge and decision tree; **20 complete selector/learner combinations**. A zero-effect null model and shuffled-observation control are included. Source mechanisms are hidden signed-majority parity/AND factors, context-specific parity switches, and a nonlinear gated composition. The shared 190-factor input dictionary is designed, not autonomously invented. No held outcomes are available to acquisition or model fitting.

## Frozen-before-primary custody
- Parent evidence archive: `ae1b56be031cec5d25a09c9df71486254192bb5d`.
- Original experiment and independent auditor committed *before primary* at `36bf1dba30ca406010ba794107c2ad468c97f36b`. The exact bzip2 Git blobs are `4b9a14b2140c369376684ce5488045841a6ec5be` and `b813c6addcc3d6d3fadac95c17fe6a2becb95a25`; decompressed SHA-256 respectively `879be3760bb28d34bacf03f7dc9603556d9adcc58b0f517cdc4c75d5a2418026` and `d477c790bdec0c646d86017190cd92eafdd1b95888206213f57b3e9374448e25`.
- Exact primary seeds, source, split, controls, 7 development gates and stop rule preregistered separately **before primary** at `4d66478a7b43932c7914556e5956cdbec0b39910`.
- Smoke only: excluded seed 99311, three worlds, independent source/refit 355 checks PASS; no primary seeds used in smoke.
- Primary: seeds **7807,7829,7841**, 6 worlds/seed × 3 causal mechanisms = **54 independent source worlds**, per policy **48 old witnessed interventions + 12 new selected witnessed interventions**, 48 held action pairs/world, **2,592 held causal effects and 2,592 each old/new held predictions per complete arm**.
- All modes evaluated in a single bounded, frozen primary; exactly one unchanged-source semantic replay and an independently authored full refit audit followed. **No postresult tuning or reranking**.

## Primary results

| Selector + final learner | Exact causal effects / 2,592 | Correct x0=1 labels / 2,592 | Correct old labels / 2,592 |
|---|---:|---:|---:|
| **OMP uncertainty + energy** (best learned alternative) | **1,330 (51.31%)** | **1,527** | 2,093 |
| Null, always no change | 1,305 (50.35%) | Not applicable | Not applicable |
| Random + energy | 1,298 (50.08%) | 1,500 | 2,078 |
| Hamming diversity + energy | 1,272 (49.07%) | 1,461 | 2,076 |
| **One-pass energy selector + energy** | **1,239 (47.80%)** | **1,424** | **2,099** |
| Random + OMP12 | 1,235 (47.65%) | 1,497 | 1,839 |

Compared against the best other fully fitted policy, the energy candidate missed **91/2,592 = 3.51 percentage points** of causal-effect correctness, far short of its frozen +3pp superiority gate. It also loses to the action-independent no-change null. The candidate has a slight old-context retention advantage (2,099 vs 2,093), but that does not compensate for failure to learn intervention consequences on unfamiliar held contexts. Candidate-new-label correctness 1,424 is 103 below strongest alternative, missing the +2pp new-label gate.

Causal-effect gain of the candidate over random+energy = **−59/2,592 = −2.28pp**, contrary to the predeclared +2pp action-selection value gate. Primary per-seed effect margins versus the strongest other learned arm were **−45, −17, −58**, so no seed showed the required positive advantage. Label-shuffled candidate gave **1,009/2,592** correct effects versus 1,239 using actual labels: sham-ablation PASS, but not superiority.

## End-to-end policy cost (bounded local component measurement)

Across 54 source worlds the instrumented `source_generation + intervention_selection + final_model_fit + held_prediction` cumulative wall-time proxy was:
- **One-pass energy + energy:** **0.152999 seconds**, 1,239 verified effects; approximately **8,098 correctly predicted effects per measured second**.
- **Random + OMP12:** **0.077935 seconds**, 1,235 effects; approximately **15,847 correctly predicted effects per measured second**.
- **OMP uncertainty + energy:** **0.191378 seconds**, 1,330 effects.

The candidate costs **1.96×** random+OMP but achieves only **0.51× its verified effect yield per measured second**, versus the preregistered required ≥1.5×. The complete experiment evaluating every arm was **1.479 seconds** on one local Linux CPU environment. These are measured Python components, not GPU/physical Joules or full operational engineering/CI/deployment cost. No distinctive physical-energy or system-wide speed advantage is claimed.

## Frozen gate accounting

| Gate | Result |
|---|---|
| +3pp exact causal-effect gain vs strongest 19 policies and no-change null | **FAIL** |
| +2pp held new-context accuracy vs strongest other trained policy | **FAIL** |
| Old-context retention no worse than 1pp below best control | **PASS** |
| +2pp intervention-selector gain vs random + same energy learner | **FAIL** |
| Positive effect gain vs strongest comparator on ≥2/3 seeds | **FAIL** |
| +5pp true-witness learning over shuffled-label negative | **PASS** |
| ≥1.5× correct causal effects / policy component second vs random+OMP | **FAIL** |

**2 PASS / 5 FAIL → DEVELOPMENT_NO_GO**. Do not adjust primary seeds, thresholds, source generator or cost metrics to rescue the result.

## Exploratory diagnosis after frozen scoring

Each mechanism family contributes 864 held effect pairs. For **majority**, one-pass energy scored 409, OMP uncertainty+energy 416 and no-change 433. For **context switch**, one-pass 491, OMP uncertainty+energy 550 and no-change 440. For **nonlinear gated composition**, one-pass 339, OMP uncertainty+energy 364, but no-change 432. This indicates the energy selector's difficulties are not concentrated in only one mechanism: it fails the conventional opponent on every family. These family analyses were computed **after scoring**, are not supplementary acceptance gates and must not justify primary-seed retuning.

## Independent engineering custody
- Original timing-bearing primary `scored.json` **480,626 bytes**, SHA-256 `824c15f4f3cf58ea0794eed53cf3e0a03a610b3b9c8fbdf5e87539fdb2fe6bef`. This original file is retained in the local research workspace, not the GitHub branch.
- **Complete deterministic semantic primary record is deposited on GitHub** as `semantic.json.bz2`, 8,645 bytes, Git blob `9f9dffc5fce26c72215d843e8ee7322c9bf6e22c`, compressed SHA-256 `a145d2084dbed2281a8e77865990c9a57a0f05b1fe434c0f67400eb1435603f0`, decompresses to **137,119-byte JSON** SHA-256 `2000f13a214e4503f3a6d9d62fe8449d6d4591015c77c575ebf699a930155f18`. Every source-world ID, each of the five policies' exact selected 12 interventions, their acquired consequences, every fitted model's scores and active supports, frozen gates, null and shuffled controls are preserved. Only nondeterministic timing fields are excluded from this artifact; aggregate timing values are retained in `result.json`.
- **54-world summary receipt CSV** `world_receipts.csv`, 2,446 bytes, Git blob `7a01676b644b435cf331676bf2a28282325bce0c`, SHA-256 `856a3d4bb5c085748058ae82e5839ceeb65d4be95fc42055d50145b1ea8a3dd8`.
- Independent `audit.py` source rebuilds the causal generator separately, recomputes observed noisy actions and labels, reconstructs all 5 acquisition policies and refits all 20 complete learned arms, checks all 54 case records and their 48 paired held predictions, support sizes, costs and frozen classification, without importing the scorer. **6,169 independent checks PASS.** Both codepaths use the same third-party scikit-learn implementation for the conventional estimators; no claim of independent reimplementation of sklearn.
- A separate exact-source replay matched the complete 137,119-byte semantic record **byte-for-byte**, SHA-256 unchanged. Local Python 3.13.5, NumPy 2.3.5, sklearn 1.8.0, Linux CPU with single-threaded BLAS; no paid API, native runner or GPU. **Mandatory final native cross-platform regression and independent scientific acceptance NOT RUN**, so this evidence grants no Yggdrasil learning qualification, adoption or integration authority.

## Reproduction

On the exact evidence branch commit, enter `ENERGY-38`. Before scoring, decompress both `experiment.py.bz2` and `audit.py.bz2` to matching .py files and verify their decompressed SHA-256 against the pinned `prereg.json`. Then:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B experiment.py --out replay.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B audit.py replay.json replay_audit.json
python -B verify_archive.py
```

The original timing-bearing primary SHA will vary on replay. Compare the canonical semantic record (exclude `wall_seconds`, `policy_full_seconds`, per-case `source_s`, `shuffled_fit_s`, per-policy `selection_s` and per-arm `fit_pred_s`/`policy_total_s`). `verify_archive.py` checks the deposited original deterministic semantic and summary receipts without rerunning any primary seeds.

## Decision and research direction
**Stop this class of energy-guided witness-selector optimizations on consumed source mechanisms and seeds.** The one-pass selector underperforms the best fully trained active acquisition policy, trivial no-change control and inexpensive conventional cost/benefit benchmark. A further small selector-threshold tweak is unlikely to address the underlying missing causal generalization. If classical energies research continues, move to a **distinct falsifiable strength: constraint satisfaction and compositional energy minimization against exact and optimized graph solvers**, with end-to-end CPU budgets and unfamiliar graph structures. Such a new hypothesis needs prospective seeds, stronger controls and independent native qualification before any promotion.

**ENGINEERING:** local scorer/auditor/replay PASS; native CI/full regression UNVERIFIED. **SCIENCE:** DEVELOPMENT_NO_GO. **DEPLOYMENT:** NONE.
