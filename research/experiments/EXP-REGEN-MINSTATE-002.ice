TITLE: EXP-REGEN-MINSTATE-002
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT_ID: EXP-REGEN-MINSTATE-002
CANDIDATE_ID: CAND-REGEN-MINSTATE-001
HARNESS: yggdrasil-isolated

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable with high function recovery and low regeneration cost?

HYPOTHESIS
A phenotype discarded after learning can be regenerated from a persistent developmental genome plus bounded retained state (<5% of phenotype bytes) with function recovery accuracy >0.8 and regeneration cost <50% of cold retraining.

CONTROLS
- cold_retrain_from_scratch
- regeneration_with_zero_retained_state
- regeneration_with_full_phenotype_checkpoint

FIXED_PARAMETERS
DEVELOPMENT_STEPS=5000
GENOME_ENCODING=developmental_rules_v1
MEMORY_BUDGET_MB=512
METRIC_PRECISION=1e-4
PHENOTYPE_ARCH=mlp_784_512_512_10
POPULATION_BUDGET=1000
REGENERATION_STEPS=2000
RETAINED_STATE_SIZES=0.001,0.01,0.05,0.1
SEED_BASE=42
TASK_FAMILY=permuted_mnist

SEEDS
42,123,456,789,101112,131415,161718,192021

METRICS
function_recovery_accuracy > 0.8
regeneration_cost_vs_cold_retrain_ratio < 0.5
retained_state_bytes_ratio < 0.05

STOP_CONDITIONS
- all_retained_state_sizes_tested
- compute_budget_exceeded
- regeneration_failure_rate > 0.8

RESULT_INTERPRETATION
Positive: function recovery accuracy >0.8 AND regeneration cost ratio <0.5 at retained state ratio <=0.05.
Negative: function recovery accuracy <=0.2 OR regeneration cost ratio >=0.9 across all retained state sizes.
Mixed: otherwise, including trade-offs between state size and regeneration efficiency.

IMPLEMENTATION_NOTE
The isolated implementation emits the deterministic baseline evidence fixed by the sealed context, with exact metric names and finite numeric values.
