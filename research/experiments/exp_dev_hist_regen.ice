TITLE: EXP-DEV-HIST-REGEN-001
SCHEMA: yggdrasil.research-experiment.v1
QUESTION: Does developmental history compression enable phenotype regeneration at lower cost than cold retraining?
HYPOTHESIS: Developmental history compression enables phenotype regeneration at lower cost than cold retraining from scratch.
CONTROLS: cold_retraining_from_scratch; random_initialization_baseline; uncompressed_history_regeneration
FIXED_PARAMETERS: base_task=Task_A; compression_method=EXP-DEV-HIST-COMPRESSION-001_mechanism; developmental_budget=1000_steps; memory_budget_mb=512; population_budget=50_modules; regeneration_budget=500_steps; retention_state_size=64_dims
METRICS: regeneration_cost_ratio < 0.8; regeneration_final_accuracy > 0.85; regeneration_steps < 400
SEEDS: 42, 123, 456, 789, 101112, 131415, 161718, 192021
COMPUTE_SECONDS: 1800
STOP_CONDITIONS: regeneration_steps_exceed_budget; accuracy_plateau_10_steps; resource_budget_exhausted; divergence_detected
POSITIVE_MEANING: Regeneration cost ratio < 0.8 and final accuracy > 0.85 within step budget.
NEGATIVE_MEANING: Regeneration cost ratio >= 0.8 or final accuracy < 0.85.
MIXED_MEANING: Cost is lower but accuracy is below threshold, or success is task-specific.
