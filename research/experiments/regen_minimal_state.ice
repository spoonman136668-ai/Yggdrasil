EXPERIMENT_ID: YGG-A75-REGEN-MINIMAL-STATE
CANDIDATE_ID: cand-regen-minimal-state
HARNESS: yggdrasil-isolated

CONTROLS:
- Cold retraining from identical initialization for each task
- Fixed random seeds for all stochastic operations
- Identical task sequence and data splits across conditions
- Fixed compute budget per regeneration attempt

FIXED_PARAMETERS:
- development_step_budget: 2000
- memory_budget_mb: 512
- population_budget: 1000
- regeneration_step_budget: 1500
- retained_state_conditions: genome_only,genome_wake_vectors,genome_activation_stats,full_checkpoint
- task_sequence_length: 5

METRICS:
- regeneration_cost_ratio < 0.5
- capability_recovery_fraction > 0.7
- persistent_bytes_per_capability < 400000
- development_steps_to_recovery < 800

SEEDS: 42,123,456,789,1024,2048,4096,8192
COMPUTE_SECONDS: 1800

STOP_CONDITIONS:
- Regeneration step budget exceeded
- Capability recovery fraction plateaus for 100 consecutive steps
- Active parameter count exceeds population budget
- Resident memory exceeds memory budget
