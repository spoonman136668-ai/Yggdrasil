TITLE: EXP-DG1C Repeated Exposure
SCHEMA: ckb-plane.research-experiment.v1
EXPERIMENT: EXP-DG1C-REPEATED-EXPOSURE-001
CANDIDATE: CAND-REPEATED-EXPOSURE-001
HARNESS: yggdrasil-isolated
BASELINE_SHA: b643a0ac0318315b5f670c41524a24b4df3fbb43
PROPOSAL_SHA256: bd7c4b09b88f755d2b7b3650996dddffd090f65373d96484c1bd9f25e69d981e

QUESTION
Does repeated exposure to related tasks compress future development trajectories as measured by decreasing regeneration cost and retained state across a task sequence?

HYPOTHESIS
Repeated exposure to structurally similar tasks compresses future development trajectories, reducing regeneration cost ratio and retained state bytes ratio while maintaining capability recovery ratio.

CONTROLS
- Cold retraining baseline for each task in sequence
- Fixed-architecture sequential learning baseline
- Random task order control to isolate structural similarity effect

FIXED PARAMETERS
memory_budget_mb=512
population_budget=1000
regeneration_budget_steps=100
structural_similarity=0.7
task_sequence_length=5
wake_state_budget_bytes=10240

METRICS
regeneration_cost_ratio_task5_vs_task1 < 0.8
retained_state_bytes_ratio_task5_vs_task1 < 0.8
capability_recovery_ratio_min >= 0.8
development_steps_ratio_task5_vs_task1 < 0.7

SEEDS
42,123,456,789,101112,131415,161718,192021

STOP CONDITIONS
- Regeneration cost ratio increases for 2 consecutive tasks
- Capability recovery ratio falls below 0.75
- Compute budget exhausted
- All 5 tasks completed

POSITIVE_MEANING
Regeneration cost ratio and retained state bytes ratio decrease monotonically across the 5-task sequence while capability recovery ratio remains >= 0.8. Repeated exposure compresses development trajectories.

NEGATIVE_MEANING
Regeneration cost ratio and retained state bytes ratio do not decrease across the task sequence, or capability recovery ratio falls below 0.8. Repeated exposure does not compress development trajectories.

MIXED_MEANING
Regeneration cost decreases but capability recovery drops below 0.8, indicating over-compression losing functional information.
