EXPERIMENT_ID: EXP-DG1B-REGEN-COST-001
CANDIDATE_ID: cand-regen-cost-001
HARNESS: yggdrasil-isolated
ARCHITECTURE: DG-1B

QUESTION
Does phenotype regeneration from developmental information cost materially less than cold retraining while preserving capability?

HYPOTHESIS
Regenerating a discarded phenotype from genome plus bounded retained state costs < 50% of cold retraining from scratch while recovering > 80% capability.

CONTROLS
- cold_retraining_from_scratch_same_seed
- fixed_genome_capacity_across_conditions
- identical_task_data_order
- fixed_wake_state_budget

FIXED_PARAMETERS
architecture=DG-1B
genome_capacity_mb=50
harness=yggdrasil-isolated
seed=42
task_sequence=A,B,C
wake_state_budget_mb=5

METRICS
regeneration_cost_ratio < 0.5
capability_recovery_ratio > 0.8
active_parameter_growth_per_task < 0.3
retained_capability_after_sequence > 0.75

SEEDS
42,123,456

COMPUTE_SECONDS
1800

STOP_CONDITIONS
- regeneration_cost_ratio >= 0.9 for 2 consecutive tasks
- capability_recovery_ratio < 0.6 for any task
- compute_seconds > 1800
- active_parameter_growth_per_task > 0.5

POSITIVE_MEANING
Regeneration cost < 50% cold retraining and capability recovery > 80% for 3+ sequential tasks; supports North Star claim that capability grows faster than active structure.

NEGATIVE_MEANING
Regeneration cost >= cold retraining cost or capability recovery < 80% across 3+ tasks; weakens developmental thesis, suggests genome encoding insufficient for regeneration.

MIXED_MEANING
Regeneration cheaper than retraining but capability recovery insufficient, or vice versa; requires architectural revision of genome/wake state encoding.
