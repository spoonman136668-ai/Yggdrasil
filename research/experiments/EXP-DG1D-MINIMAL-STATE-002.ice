TITLE: EXP-DG1D-MINIMAL-STATE-002
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT_ID: EXP-DG1D-MINIMAL-STATE-002
CANDIDATE_ID: CAND-DG1D-MINIMAL-STATE
HARNESS: yggdrasil-isolated
BASELINE_SHA: 32ee4e5f5963af0e9d16e69888525807c55292b1

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable, as measured by capability recovery ratio and regeneration cost ratio?

HYPOTHESIS
A retained state of <=5% of phenotype bytes is sufficient for regeneration with capability recovery ratio >=0.8 and regeneration cost ratio <=0.5.

FIXED_PARAMETERS
- evaluation_metric: capability_recovery_ratio on held-out test set
- hibernation_protocol: PRUNE active modules, retain only specified state bytes
- phenotype_architecture: DG-1A baseline from commit 32ee4e5f
- regeneration_protocol: REGENERATE from retained state using developmental dynamics
- task_sequence: 5-task continual learning benchmark

METRICS
- capability_recovery_ratio >= 0.8
- regeneration_cost_ratio <= 0.5
- retained_state_bytes_ratio <= 0.05

SEEDS
42, 123, 456, 789, 101112

CONTROLS
- Fixed random seeds for reproducibility
- Identical initial phenotype across all retained state conditions
- Same task sequence and evaluation protocol as EXP-DG1D-MINIMAL-STATE-001
- Cold retraining baseline with full phenotype from scratch

STOP_CONDITIONS
- All retained state conditions evaluated across all seeds
- Compute budget (1800 seconds) exhausted
- Capability recovery ratio <0.5 at lowest retained state level for 3+ consecutive seeds

POSITIVE_MEANING
Capability recovery ratio >=0.8 AND regeneration cost ratio <=0.5 at retained_state_bytes_ratio <=0.05.

NEGATIVE_MEANING
Capability recovery ratio <0.8 at all retained state bytes ratios <0.1, OR regeneration cost ratio >0.5 at all levels.

MIXED_MEANING
Capability recovery ratio >=0.8 at some retained state levels but not others, or regeneration cost ratio <=0.5 only at higher retained state levels.
