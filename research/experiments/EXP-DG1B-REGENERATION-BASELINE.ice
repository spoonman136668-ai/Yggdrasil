TITLE: DG-1B Functional-Regeneration Baseline
EXPERIMENT_ID: EXP-DG1B-REGENERATION-BASELINE-001
STATUS: PREREGISTERED
HARNESS: yggdrasil-isolated

QUESTION
Does the DG-1B functional-regeneration baseline achieve the North Star targets for regeneration cost ratio, retained capability ratio, and genome efficiency?

HYPOTHESIS
REGENERATE from genome plus bounded retained state achieves >85% capability recovery at <40% cold retraining cost for all archived tasks, with genome size <6KB per capability.

FIXED PARAMETERS
archive_retention_policy = genome_plus_1kb_wake_per_module
damage_pattern = sequential_task_archive_after_5_tasks
genome_budget_bytes_per_capability = 6144
max_tasks = 15
population_budget_modules = 128
regeneration_trigger = explicit_task_demand

CONTROLS
cold_retrain_from_scratch_same_architecture
fixed_router_baseline_same_parameter_budget
hypernetwork_baseline_same_genome_budget

METRICS
regeneration_cost_ratio < 0.4
retained_capability_ratio >= 0.85
genome_size_bytes_per_capability < 6144
wake_latency_ratio < 5

SEEDS
42, 123, 456, 789, 1024, 2048, 4096, 8192

STOP CONDITIONS
all_15_tasks_archived_and_regenerated
compute_seconds_exceeded
any_single_regeneration_cost_ratio_exceeds_0.8
genome_size_exceeds_8192_bytes_per_capability

POSITIVE MEANING
All four North Star ratios met; DG-1B baseline established, ready for DG-1C open-ended structural operations.

NEGATIVE MEANING
Regeneration cost ratio >= 0.4 or retained capability ratio < 0.85 or genome size >= 6KB/capability; DG-1B baseline fails, requiring architectural revision before proceeding.

MIXED MEANING
Some North Star ratios met but others missed; indicates partial validation requiring mechanism refinement before DG-1C open-ended operations.
