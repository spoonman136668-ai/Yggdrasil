TITLE: EXP-REGEN-MINIMAL-001
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT: EXP-REGEN-MINIMAL-001
CANDIDATE: CAND-REGEN-MINIMAL-001
HARNESS: yggdrasil-isolated

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable with high fidelity and low developmental cost?

HYPOTHESIS
Functional regeneration from genome plus bounded retained state achieves retained_state_bytes_ratio <= 0.05, regeneration_development_steps_ratio <= 0.1, function_recovery_accuracy >= 0.95, and regeneration_cost_vs_cold_retrain_ratio < 0.3.

CONTROLS
- Cold retraining from scratch with identical architecture and data
- Regeneration with full phenotype state retained (upper bound)
- Regeneration with zero retained state (genome only, lower bound)
- Fixed random seeds for all stochastic operations
- Identical compute budget across conditions

FIXED PARAMETERS
- damage_pattern: random_module_removal
- development_step_budget: 500
- genome_size_bytes: 102400
- max_active_parameters: 500000
- memory_budget_bytes: 10485760
- population_budget: 100
- task_complexity: medium

METRICS
- retained_state_bytes_ratio <= 0.05
- regeneration_development_steps_ratio <= 0.1
- function_recovery_accuracy >= 0.95
- regeneration_cost_vs_cold_retrain_ratio < 0.3

SEEDS
42, 123, 456, 789, 101112

COMPUTE_SECONDS
1200

STOP_CONDITIONS
- All seed trials completed
- Any trial exceeds compute_seconds budget
- Regeneration development steps exceed 2x cold retraining steps
- Function recovery accuracy drops below 0.5 for any retained state level

POSITIVE_MEANING
Functional regeneration achieved under all preregistered metric thresholds.

NEGATIVE_MEANING
Minimal retained state exceeds 5% of active phenotype, regeneration development steps exceed 10% of cold retraining, or recovery accuracy is below 95%.

MIXED_MEANING
Regeneration succeeds on some metrics but fails on others; mechanism refinement is required.
