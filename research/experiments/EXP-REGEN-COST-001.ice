TITLE: EXP-REGEN-COST-001
SCHEMA: yggdrasil.research-experiment.v1
EXPERIMENT: EXP-REGEN-COST-001
CANDIDATE: CAND-REGEN-COST-001
HARNESS: yggdrasil-isolated

QUESTION
Does developmental regeneration achieve <50% cold retraining cost with >95% functional recovery?

HYPOTHESIS
Regeneration from genome plus bounded retained state recovers task capability at <50% of cold retraining compute cost while maintaining >95% accuracy.

CONTROLS
- cold_retraining_from_scratch
- fixed_architecture_baseline
- hypernetwork_adapter_baseline

FIXED PARAMETERS
- hibernation_policy: lru_wake_state_10%
- memory_budget_mb: 4096
- population_budget: 2000
- regeneration_trigger: accuracy_drop_below_90%
- task_sequence: permuted_mnist_5_tasks

METRICS
- regeneration_cost_ratio < 0.5
- regeneration_accuracy > 0.95
- wake_latency_ratio < 1.5

SEEDS
42, 123, 456, 789, 101112, 131415, 161718, 192021

COMPUTE_SECONDS
1200

STOP CONDITIONS
- regeneration_cost_ratio >= 0.95 for 3 consecutive seeds
- total_compute_exceeds_1200s
- accuracy_collapse_below_50%

POSITIVE MEANING
Regeneration cost <50% of cold retraining and accuracy >95% supports the North Star claim that capability grows faster than permanent structure.

NEGATIVE MEANING
Regeneration cost >=50% of cold retraining or accuracy <=95% falsifies the hypothesis that developmental regeneration is substantially cheaper than retraining.

MIXED MEANING
Cost <50% but accuracy <95%, or cost 50-80% with accuracy >95%, indicates partial success requiring mechanism refinement.
