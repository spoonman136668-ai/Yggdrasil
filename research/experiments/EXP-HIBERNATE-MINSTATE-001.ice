TITLE: EXP-HIBERNATE-MINSTATE-001
EXPERIMENT: EXP-HIBERNATE-MINSTATE-001
CANDIDATE: CAND-HIBERNATE-MINSTATE-001
HARNESS: yggdrasil-isolated

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable with function_recovery_accuracy > 0.5 and regeneration_cost_vs_cold_retrain_ratio < 0.5?

HYPOTHESIS
There exists a retained_state_bytes_ratio between 0.01 and 0.1 that yields function_recovery_accuracy > 0.5 and regeneration_cost_vs_cold_retrain_ratio < 0.5.

FIXED PARAMETERS
development_steps_per_task=1000
hibernate_wake_cycles=1
memory_budget_mb=512
population_budget=1000
retained_state_composition=lineage_connectivity_paramstats
task=permuted_mnist_continual

METRICS
function_recovery_accuracy > 0.5
regeneration_cost_vs_cold_retrain_ratio < 0.5
retained_state_bytes_ratio <= 0.1
active_parameter_growth_per_task < 10000

SEEDS
42, 123, 456, 789, 1024, 2048, 4096, 8192

CONTROLS
Cold retrain from scratch with same compute budget
Random initialization with same retained state size (shuffled)
Fixed architecture baseline (no HIBERNATE/WAKE)
Varying random seeds for statistical robustness

STOP CONDITIONS
All retained_state_bytes_ratio conditions completed
Compute budget exhausted
Function recovery accuracy converges across seeds
Safety violation detected

POSITIVE MEANING
Exists retained_state_bytes_ratio <= 0.1 achieving function_recovery_accuracy > 0.5 and regeneration_cost_vs_cold_retrain_ratio < 0.5.

NEGATIVE MEANING
No retained state size up to 10% yields both target conditions.

MIXED MEANING
Partial recovery or moderate cost reduction suggests retained state composition matters but the current formulation is insufficient.
