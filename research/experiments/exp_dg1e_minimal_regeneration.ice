TITLE: EXP-DG1E Minimal Regeneration
EXPERIMENT_ID: EXP-DG1E-MINIMAL-REGENERATION-001
STATUS: PREREGISTERED
HARNESS: yggdrasil-isolated
DAMAGE_TYPE: complete_prune
HIBERNATION_DURATION: 0
MAX_DEVELOPMENT_STEPS: 5000
MEMORY_BUDGET_MB: 512
POPULATION_BUDGET: 1000
TASK_COMPLEXITY: medium
TASK_COUNT: 5
WAKE_SIGNAL_BUDGET: 0.05
CONTROLS: cold_retraining_baseline, fixed_architecture_baseline, hypernetwork_baseline, adapter_baseline, random_retained_state_baseline
METRICS: regeneration_cost_ratio_vs_retrain < 0.3; functional_recovery_ratio > 0.8; active_parameter_growth_ratio < 0.3; resident_byte_growth_ratio < 0.2; global_signal_fraction < 0.05
SEEDS: 42, 123, 456, 789, 1024, 2048, 4096, 8192
COMPUTE_SECONDS: 1800
STOP_CONDITIONS: regeneration_cost_ratio_vs_retrain > 1.0 for all configurations; functional_recovery_ratio < 0.5 for all configurations; development_steps > 5000 for any configuration; global_signal_fraction > 0.1 for any configuration; compute_seconds > 1800
POSITIVE_MEANING: At least one retained state configuration achieves functional recovery > 0.8 and regeneration cost ratio < 0.3.
NEGATIVE_MEANING: No retained state configuration achieves both functional recovery > 0.8 and regeneration cost ratio < 0.3.
MIXED_MEANING: Some retained state configurations meet cost threshold but not recovery threshold, or vice versa.
