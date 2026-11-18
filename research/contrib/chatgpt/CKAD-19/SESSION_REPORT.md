# CKAD19 — frequency-matched causal transfer, frozen negative

**Local development: 4/4 unit checks PASS; paired trial complete; preregistered DEVELOPMENT_NO_GO.** This is an isolated synthetic sidecar and not a change to Yggdrasil's native learner or accepted `main`.

## Evidence and custody

- Parent exact Yggdrasil PR #1207 candidate: `337ead74cc3a600598580747c3d8ca2d422777d0` (tree `6dc08e25f3322f69cb213c58e9b250128d23c987`); parent exact-final regression 9/9 at Actions run 44215859139
- Protocol frozen **before first CKAD19 score** at `e10eade9f2d84f062993080f7ca215fece32cfe7`
- Local source blob `c4465efc5edd142c9ad2cc48df2ab0b9f5150b76` matches committed Git blob byte-for-byte; local tests blob `1d6d4d844e78edb620a35fc5f8d58be37a626f18` matches Git
- Two local results produced identical stable semantic SHA256 `46b7f64a2c390c89f85452ec5fa9a74853593582a3450f23d823c60a1ca99685`
- 120 case-folds, 10 frozen seeds, 2 parity family types, 6 withheld rules per family; 4 distinct training tasks per case, 5 publicly selected interventions per training task; no exact held rule appears among training tasks
- Every one of the 12 preprogrammed candidate rules has **exactly 8 positive outcomes across 16 complete context/actions**. A positive-outcome-rate shortcut cannot distinguish the families in the population
- Two SHA-pinned cold-restores passed, tampering rejected; 28,800 independently enumerated Bayes prediction comparisons agree. No protected source reset/do, private hidden state or external model API

## Frozen comparisons

Mean Brier and decision regret after **two** held-world interventions (smaller is better):

| Arm | Brier | Regret |
| --- | ---: | ---: |
| Accumulated family prior + entropy-selected query | 0.083853762603 | 0.166666666667 |
| Flat family prior + identical entropy selector | 0.166800000000 | 0.250000000000 |
| Accumulated family prior + seeded random query | 0.099386131468 | 0.181250000000 |
| Frequency-only action-conditioned control | 0.263594415128 | 0.500000000000 |

Paired `meta_active - flat_active` at t=2: Brier -0.08294624 (1000-resample 95% bootstrap [-0.09324664,-0.07161632]); regret -0.08333333 ([-0.10416667,-0.06041667]).

Paired `meta_active - meta_random` at t=2: Brier -0.01553237 (95% CI [-0.03167615,+0.00061145]); regret -0.01458333 ([-0.04583333,+0.01666667]).

Regret reduction against the random-query arm is **only 8.05%, below the frozen 10% gate**. That gate FAILS; no tuning, threshold adjustment, new seeds, or postscore choice is allowed. Forecast after four interventions: accumulated+active Brier 0.000000692, random Brier 0.012747689, flat Brier 0.000769556; flat and accumulated+active both have zero decision regret at that stage.

Matched labels eliminate the population outcome-frequency shortcut, but this small preprogrammed hypothesis family itself is strong inductive bias. A conventional independent Bayesian enumerator with the identical hypothesis class ties all predictions; the experiment does not demonstrate architectural superiority or open-ended law discovery. Evaluating on preprogrammed unseen **rules** must not be described as discovering a genuinely unforeseen family.

Cross-task family posterior puts mean probability 0.9999929005 on the correct synthetic family. Shuffling training labels reduces mean correct-family posterior to 0.5946421489; the inverted-family diagnostic mass is 0.0000070995. These are diagnostics, not independent scientific validation.

## Result

**ENGINEERING locally PASS; DEVELOPMENT_NO_GO; SCIENTIFIC_PASS=false; DEPLOYMENT NONE.**

Keep CKAD17/18 accepted engineering results intact. Do **not** integrate CKAD19 into the native learner or merge it into accepted `main` based on this data. Next evidence should test adaptive intervention value on nontrivial delayed effects with fully trained matching control and independent new-world qualification, respecting separate source first-use.

The complete canonical 120-case traces are generated deterministically by `campaign.py`; qualification run uploads exact trace files as CI artifacts. `LOCAL_RESULT_SUMMARY.json` retains the bounded summary permanently in Git. This report documents the local development finding; formal dual-platform exact-candidate status is recorded separately after CI.
