TITLE: Developmental History Compression
EXPERIMENT: EXP-DEV-HIST-COMPRESSION-001
CANDIDATE: CAND-DEV-HIST-COMPRESSION-001
HARNESS: yggdrasil-isolated

QUESTION
Does repeated task exposure compress future developmental trajectories as measured by development steps, active parameters, and resident bytes?

HYPOTHESIS
Repeated task exposure compresses future developmental trajectories, reducing development steps and resource consumption for structurally similar tasks.

CONTROLS
- single-task baseline (no sequence)
- shuffled task order control
- fixed-architecture baseline (no developmental operations)
- random seed control

FIXED PARAMETERS
development_step_budget=10000
memory_budget_mb=512
population_budget=1000
regeneration_threshold=0.95
task_sequence_length=5
task_similarity=structured_variation

METRICS
development_steps_ratio_taskN_task1 < 0.8
active_parameters_ratio_taskN_task1 < 0.85
resident_bytes_ratio_taskN_task1 < 0.85
capability_recovery_fraction >= 0.95

SEEDS
42, 123, 456, 789, 1024, 2048, 4096, 8192

STOP CONDITIONS
- all seeds complete
- compute_seconds exceeded
- capability_recovery_fraction < 0.5 for any seed
- development_step_budget exceeded for any seed
