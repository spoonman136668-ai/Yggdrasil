TITLE: EXP-HIBERNATE-STATE-SCALING-001
EXPERIMENT_ID: EXP-HIBERNATE-STATE-SCALING-001
STATUS: PREREGISTERED
HARNESS: yggdrasil-isolated

QUESTION
What is the minimum retained state fraction that enables functional regeneration with regeneration_cost_vs_cold_retrain_ratio < 1.0?

FIXED PARAMETERS
development_steps_per_task=200
memory_budget_mb=512
num_tasks=5
population_budget=100
retention_ratios=[0.01,0.02,0.05,0.1]
task_family=permuted_mnist

CONTROLS
- fixed task sequence (permuted MNIST 5 tasks)
- fixed developmental operation set (HIBERNATE, WAKE, REGENERATE)
- fixed population and memory budgets
- fixed random seeds per condition

METRICS
- function_recovery_accuracy >= 0.5
- regeneration_cost_vs_cold_retrain_ratio < 1
- active_parameter_growth_per_task <= 5000

SEEDS
42,123,456,789,101112,131415,161718,192021

STOP CONDITIONS
- all retention ratios evaluated
- compute_seconds >= 1800
- any single condition exceeds 450 seconds

POSITIVE MEANING
At least one retention ratio achieves function_recovery_accuracy >= 0.5 and regeneration_cost_vs_cold_retrain_ratio < 1.0, with monotonic improvement.

NEGATIVE MEANING
No retention ratio up to 0.1 achieves function_recovery_accuracy >= 0.5 or regeneration_cost_vs_cold_retrain_ratio < 1.0.

MIXED MEANING
Some retention ratios show improvement but not monotonic, or improvement only at the highest retention ratio.
