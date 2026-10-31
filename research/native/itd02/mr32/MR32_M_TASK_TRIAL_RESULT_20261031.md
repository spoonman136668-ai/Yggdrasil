# MR32-M — task-derived utility trial result

Date: 2026-10-31
PR #716 remains OPEN / DRAFT / UNMERGED.
Exact tested source head: `700a89e1db1cfde91e1e8914a5f95127755b0338`.
Exact GitHub Actions run: `41228618752`.
- Windows job `124618304368`: PASS, 69 tests, task-trial contract sentinel PASS.
- Ubuntu job `124618304566`: PASS, 69 tests, task-trial contract sentinel PASS.
- The workflow compiled all relevant modules, executed 256-step resource inventory and the prior synthetic retention diagnostics, executed the task-derived trial, validated its receipt invariants and passed clean checkout.

## Frozen experiment and evidence identity

- Frozen protocol: `research/native/itd02/mr32/MR32_M_TASK_DERIVED_UTILITY_PROTOCOL.md`, blob `c57605887fb4aaaca8c5df9c67470e9317baf6b0`.
- Implementation: `task_utility_trial.py`, blob `718fb492fbfc8b4f23d1e8d9cb6dacc2920c8887`.
- Focused tests: `test_task_utility_trial.py`, blob `ebb7586b477e717bd6333e55cfbd30e5f3d91fa1`.
- Feedback semantics clarification, committed before execution: `MR32_M_IMPLEMENTATION_CLARIFICATION.md`, blob `89bcb760ce00e9f3b02722c69fb0ad8aeac5e718`.
- Workflow: `.github/workflows/mr32-residual-belief-source-only.yml`, blob `b10b5a4fac42787e06fe306731caae4b7883904c`.
- Complete Windows receipt: `MR32_M_TASK_TRIAL_WINDOWS_20261031.json`, blob `37f727d0f55c27f2ed83625cbfc231b6b6c9d239`.
- Complete Linux receipt: `MR32_M_TASK_TRIAL_LINUX_20261031.json`, blob `4cbea77dd906c797e0757d1f41c41ad95b460543`.

## Cohort and feedback receipts

FIT: 8 seed clusters, 4 per regime, 6 episodes per cluster = 48 episodes / 768 task events.
- MR32-H selected-use feedback events: 320.
- Interaction-Bayesian selected-use feedback events: 303.
- Complete FIT per-event receipt hash on both operating systems: `50b9fae42ccb8d2947f0e9e1bd94b5896da02dbbbab0517a4208b8bc695057bd`.
- FIT receipts contain 48 episode summaries and 623 selected-use feedback records. Policy-specific feedback counts differ because controllers select different memories; neither receives feedback for unselected items.

TRANSFER: 16 disjoint seed clusters, 8 per regime, 4 episodes per cluster = 64 episodes / 1,024 task events.
- MR32-H transfer feedback events: **0**.
- Interaction-Bayesian transfer feedback events: **0**.
- Complete TRANSFER event receipt hash on both operating systems: `5eb3145cffa0f0550768cf4721b03f72b4fa5342d6e2ede25dbc63ddc7191c1b`.
- The receipts include all 64 episode summaries, 16 cluster summaries, selected memory IDs and task returns for all five methods.

The task fixture compares a selected memory's proposed action return (+1 or -1) with a no-memory abstention return (0) on the same deterministic task event. Only the selected-use paired return delta is passed back after the event. This is a synthetic contextual task-selection fixture, not a second real-world replay.

## Transfer results

Primary endpoint: mean TRANSFER task return per seed cluster.

| Method | Mean return |
|---|---:|
| Random | -0.041015625 |
| Evidence-only | -0.001953125 |
| Fixed recency | 0.005859375 |
| MR32-H learned utility | 0.0751953125 |
| Interaction Bayesian utility | **0.0791015625** |

MR32-H minus strongest comparator (interaction Bayesian): **-0.00390625**.
MR32-H wins against:
- Random: 16 / 16 clusters.
- Evidence-only: 13 / 16.
- Fixed recency: 13 / 16.
- Interaction Bayesian: **8 / 16**.

Paired cluster bootstrap 2.5th percentile for MR32-H minus interaction Bayesian: **-0.025390625**.

### Regime breakdown against the strongest overall comparator

| Regime | MR32-H mean | Interaction Bayesian mean | MR32-H wins |
|---|---:|---:|---:|
| 0 | 0.078125 | 0.05859375 | 6 / 8 |
| 1 | 0.072265625 | 0.099609375 | 2 / 8 |

## Preregistered disposition

The frozen development-signal gates all apply. MR32-H fails:
- Required +0.02 advantage over strongest comparator: **FAIL** (actual difference -0.00390625).
- Required at least 12/16 wins: **FAIL** (actual 8/16).
- Required at least 6/8 wins in each regime: **FAIL** (actual 6/8 and 2/8).
- Required bootstrap lower bound above zero: **FAIL** (actual -0.025390625).

The following safeguards passed:
- FIT/TRANSFER seed disjointness: PASS.
- Zero TRANSFER feedback for both trained controllers: PASS.
- Windows/Linux FIT event hashes identical: PASS.
- Windows/Linux TRANSFER event hashes identical: PASS.
- 69 focused tests and exact-head clean checkout on both platforms: PASS.
- Contract sentinel `MR32M_TASK_DERIVED_FEEDBACK_SOURCE_ONLY_CONTRACT=PASS`.

Therefore:
`MR32M_DEVELOPMENT_SIGNAL=FALSE`
`MR32H_VS_INTERACTION_BAYESIAN=FAIL_FROZEN_CRITERIA`

## Interpretation

The task-derived experiment is a meaningful falsification of MR32-H's current additive five-metadata-feature utility scorer. It substantially beats the simple random, recency and evidence-only controls, but does not beat the interaction-capable Bayesian utility control.

The regime result is particularly diagnostic: MR32-H does better in regime 0, but the interaction Bayesian control is substantially better in regime 1. The synthetic regime-1 task generator includes a feature interaction; the Bayesian control has hand-authored pairwise metadata interaction terms, while MR32-H's scorer is additive. This is consistent with a function-class mismatch, not proof that Bayesian architecture is generally superior. It is also a limitation of this test: the comparator is deliberately more expressive than MR32-H on a known interaction structure.

The trial is a static memory-selection/contextual-bandit-style task fixture. Candidate memory contents, metadata and stored proposed binary actions are constructed by a hand-designed generator; the utility function learns which existing memory records to retain. The trial does not demonstrate learning the representation itself, open-ended causal world-model formation, multi-step intervention planning, persistent cognition under real distraction, or transfer to an unfamiliar external source family.

No original Farama, Pycolab, MiniGrid, Crafter, Gridworlds or protected first-use data/environment was touched. FSA-04 #83 remains OPEN. The result is controlled task-fixture development evidence only and grants no admission or promotion.

## Cross-platform resource diagnostics

Whole trial process, one execution per hosted OS:
- Windows: CPU `1,421,875,000 ns`, wall `1,434,327,400 ns`, peak working set `26,484,736 bytes`, tracemalloc peak `1,609,433 bytes`.
- Linux: CPU `979,572,521 ns`, wall `979,688,777 ns`, peak RSS `25,346,048 bytes`, tracemalloc peak `1,609,320 bytes`.

Mean diagnostic selector payload bytes:
- MR32-H: 4,815.1875 Windows / 4,816.1875 Linux.
- Interaction Bayesian: 3,326 Windows / 3,325 Linux.
- These payload figures exclude shared record storage and interpreter/runtime overhead; they are NOT all-in resource parity. Process-level CPU/RSS is the complete multi-method trial process, not a per-model isolated cost benchmark.

The event hashes and task-return metrics are identical across OS, but Bayesian posterior checkpoint hashes differ because of tiny floating-point arithmetic differences: maximum absolute difference in posterior means was about `1.47e-16`, and posterior variances about `1.39e-17`. This is numerical agreement within floating-point roundoff, not bitwise checkpoint identity. No bitwise cross-platform Bayesian-state reproducibility claim is made.

## Next scientific gate

Do not retune MR32-H using the TRANSFER cohort. Preserve the negative result. A new successor requires a new frozen prospective seed cohort/protocol before execution. The most discriminating direction is to test whether a learned interaction-aware utility mechanism can match or exceed the interaction Bayesian control without hand-coding the interaction basis, under the same selected-use feedback and 16/7/9 budget. Preserve a separate regime-held-out evaluation and all negative results. Any successor remains synthetic development-only until independent FSA first-use authority is qualified.

No PR merge, accepted-reference change, original-world dispatch, R7 integration or model promotion is requested.
