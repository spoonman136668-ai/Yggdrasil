TITLE: Regeneration Lineage Experiment
EXPERIMENT_ID: EXP-REGEN-LINEAGE-001
CANDIDATE_ID: CAND-REGEN-LINEAGE-001
HARNESS: yggdrasil-isolated

QUESTION
Does retaining developmental lineage as bounded wake information enable efficient functional regeneration?

HYPOTHESIS
Structured developmental lineage enables functional regeneration at less than 50% of cold retraining cost while respecting bounded wake information.

CONTROLS
- Cold retrain from random initialization using the same architecture and compute budget.
- Regeneration from genome only without wake information.
- Regeneration with random wake information of the same size as lineage information.

FIXED_PARAMETERS
- developmental_steps_per_task: 2000
- lineage_encoding: graph_serialization
- memory_budget_mb: 512
- population_budget: 100
- task_sequence: permuted_mnist_5_tasks
- wake_info_size_limit: 0.1

METRICS
- regeneration_cost_vs_cold_retrain_ratio < 0.5
- function_recovery_accuracy >= 0.85
- wake_info_bytes_per_active_parameter <= 0.1
- active_parameter_growth_per_task < 3000

SEEDS
42, 123, 456, 789, 1024

COMPUTE_SECONDS
1200

STOP_CONDITIONS
- regeneration_cost_vs_cold_retrain_ratio >= 0.9 for 3 consecutive seeds
- function_recovery_accuracy < 0.5 for 3 consecutive seeds
- compute_seconds > 1200
- all_seeds_completed

POSITIVE_MEANING
The lineage mechanism supports efficient functional regeneration with bounded wake information when all preregistered positive criteria are satisfied.

NEGATIVE_MEANING
The lineage mechanism does not enable efficient functional regeneration when the ratio is at least 0.5 or recovery accuracy is below 0.85.

MIXED_MEANING
A ratio below 0.5 with recovery accuracy below 0.85 indicates efficient structural regeneration without functional recovery.
