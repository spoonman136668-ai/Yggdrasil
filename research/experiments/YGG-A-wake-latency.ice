TITLE: YGG-A Wake Latency
EXPERIMENT_ID: YGG-A-WAKE-LATENCY-001
CANDIDATE: cand-001
HARNESS: yggdrasil-isolated

QUESTION
Can phenotype activation become demand-driven without catastrophic cold-start latency?

CONTROLS
- always-active baseline (no hibernate/wake)
- cold-start baseline (full regeneration from genome)
- sham hibernate (state retained but marked inactive)

FIXED PARAMETERS
hibernate_duration_steps=1000
memory_budget_mb=2048
population_budget=500
similarity_threshold=0.7
task_families=3
wake_timeout_steps=5000

METRICS
wake_latency_ratio < 2
active_compute_per_task_ratio < 0.5
capability_recovery_fraction > 0.8
regeneration_cost_ratio < 0.5

SEEDS
42, 123, 456, 789, 101112, 131415, 161718, 192021

STOP CONDITIONS
wake_latency_ratio > 3.0 for any seed
capability_recovery_fraction < 0.5 for any seed
compute_seconds > 1800
development_steps > 10000
