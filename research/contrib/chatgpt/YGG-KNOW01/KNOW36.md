# KNOW36 — Frozen prospective noisy two-regime study

**One-shot requested 2026-11-20. This file is a source-only trigger note, NOT a result.**

- Protocol frozen *before evaluator* at commit `01e9ca76e7b358ea3d414fd22450b90910d6f2d4`, Git blob `af1769f93a78b89f3f76577033787643f1185efe`.
- Existing KNOW35 candidate is unchanged, blob `8aa74ada276748faa7b32f834d406a9293ef40e0`. Evaluator source blob `79484ead408dc1144b01897b7133a0e4c416ba55`; mock-only tests blob `75c62d55a7349f34838b1bbb089ae876578c5fb1`.
- Frozen 12 FIT and disjoint 24 HELD synthetic worlds; each public trajectory is A64→B64→A64→B64, Bernoulli probabilities .85/.15 and 16 context-action pairs per 16 steps.
- Fully online fitted global switching HMM (FIT-only hazard), equal-bank random-gate ablation, last-8 rolling memory and single Beta controls. Equal public events/actions for all arms, no hidden phase or private consequence access by learners.
- Primary score: expected prequential Brier on the second B phase in both B1 and B2 cohorts; require candidate margin >=0.005 and >=9/12 wins per cohort against HMM, also margin against random ablation. Return-A retention, A/B posterior identity, sham false switches, cold restore and resource costs are frozen failure checks.
- **Source budget:** exactly 3,072 calibration events + 9,216 uniquely opened HELD events, 10,752 model observations per arm across shared-prefix and forked branches. No tests use any FIT or HELD outcome.
- One exact-key *first-attempt-only* GitHub job is allowed only after atlas source sealing, full final Linux/Windows regression and original-source read-only compatibility. Failed/uncertain first use is consumed and must not be rerun.
- The synthetic result cannot authorize native Yggdrasil scientific promotion, protected original-world #426 first use, Amalgam #1278 accepted-state updates, merge, owner-runner work, scheduling, paid API or deployment.

Report absolute original run/SHA/tree, frozen hypothesis verdict, fit-selected HMM, per-family Brier/paired wins, false switches, cold-retention counts, cost data, failures and next falsifiable mechanism. Preserve negatives; do not tune to HELD.
