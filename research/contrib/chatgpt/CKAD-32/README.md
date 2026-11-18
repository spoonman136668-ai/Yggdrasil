# CKAD32 — Causal hypothesis tournaments with real intervention outcomes

**Research-only / source-only / external contributor.** No edits to accepted native Yggdrasil, original owner, orchestration, controlled first-use, Forge or production. No merge/promotion.

## Question

CKAD29 and CKAD30 showed that adding native sparse extrapolations can make Yggdrasil's unseen causal predictions worse. CKAD31 showed that a conservative source-span guard can prevent confident wrong guesses but provides little coverage. CKAD32 changes the **selection of public interventions** rather than the hypothesis training substrate: maintain competing source-consistent explanations; choose a discriminating context/action input; observe that consequence; eliminate falsified explanations; repeat.

This implementation uses a **supplied conventional 2,880-law prior** and a bounded 24-law hypothesis committee. That is not native causal discovery, not general intelligence, and not evidence of the native learner discovering the grammar. Its value would be strictly in improving how the unchanged `NativeCumulativeLearner` collects action/consequence evidence.

## Frozen, before first use

- Parent: `8711148ccf161afbda3616cd65a7103eaf4e4cf8`.
- Preregistration committed FIRST: `fe11284f07f13ad218e014536075b73f2042e7c0`.
- Pilot seeds: `9451,9452`; primary seeds: `1451,1452,1453` must not be consumed without independently validated pilot GO.
- Each seed reserves **the same 12 held interventions for all four arms** (never publicly revealed), supplies six shared observed initial interventions, then permits **ten actual source feedback interventions** selected from the remaining 14 public inputs.
- Same native learner, optional native sparse repair and six independent extra memory-pressure slots for each policy. Full Bayesian posterior + conventional fitted baselines, uniform random, fixed public-order and full-entropy intervention controls are retained.
- Exactly 144 revealed source outcomes/arm/seed (48 old +96 pressure), and 36 held composite outcomes/arm/seed. Same held inputs across policies; matched information budget, not necessarily matched measured CPU cost.
- `PILOT_GO` requires one seed to improve repaired-native held Brier by >=0.025 over BOTH random and fixed at the same action budget, with post-intervention posterior size no larger than random; memory/custody tests must pass in both pilots. Otherwise `SCREEN_NO_GO` and **no primary B**.
- Results are development evidence only. Fully conventional exact Bayesian intervention methods must be considered in every scientific interpretation.

## Evidence custody

This branch will contain the source Git blob pin, original one-use pilot JSON receipts, independent policy/action-count and no-held-leak audit, frozen decision and final cross-platform regression receipts. Synthetic source SHA only establishes immutable identity, not real-world action authentication.

Preflight (no experiment outcomes, before eligible first-use):

```bash
PYTHONPATH=. python -B -m unittest discover -s research/contrib/chatgpt/CKAD-32 -p test_ckad32.py -v
PYTHONPATH=. python -B research/contrib/chatgpt/CKAD-32/campaign.py --mode preflight
```
