TITLE: EXP-DG1B-REGENERATION-BASELINE-001
STATUS: PREREGISTERED
CANDIDATE: CAND-DG1B-REGENERATION-BASELINE
HARNESS: yggdrasil-isolated

QUESTION
What is the regeneration cost and capability recovery for discarded phenotypes, and can activation be demand-driven?

HYPOTHESIS
Discarded phenotypes can be regenerated from genome plus bounded retained state at <50% cold retraining cost with >80% capability recovery, enabling demand-driven activation without catastrophic latency.

PARAMETERS
development_budget_steps=5000
genome_size_bytes=102400
hibernation_durations=[0,100,1000,10000]
max_active_parameters=500000
max_resident_bytes=2000000
population_budget_cells=1000
regeneration_budget_steps=2500
task_family=sequential_mnist_permuted
wake_state_bytes_budget=5120

METRICS
regeneration_cost_ratio < 0.5
capability_recovery_ratio > 0.8
retained_state_bytes_ratio < 0.1
cold_start_latency_ratio < 2

SEEDS
42,123,456,789,1024,2048,4096,8192

STOP CONDITIONS
regeneration_budget_steps_exceeded
capability_recovery_plateau_100_steps
active_parameters_exceed_budget
communication_volume_exceeds_task_compute_2x

CONTROLS
cold_retraining_from_scratch_same_architecture
regeneration_with_full_optimizer_state_retained
regeneration_with_zero_retained_state
fixed_architecture_baseline_no_development
