TITLE: EXP-DG1B Regeneration Timing
SCHEMA: ckb-plane.research-experiment.v1
EXPERIMENT_ID: EXP-DG1B-REGENERATION-TIMING-001
CANDIDATE_ID: CAND-DG1B-REGENERATION-TIMING-001
HARNESS: yggdrasil-isolated

QUESTION
Can hibernated phenotypes be woken on demand with acceptable latency and capability retention compared to cold retraining?

HYPOTHESIS
Hibernated phenotypes can be woken on demand with latency < 10x cold retraining and retained capability > 0.7.

CONTROLS
- cold_retraining_from_genome
- hibernated_phenotype_wake
- random_seed_variance

FIXED_PARAMETERS
- damage_type: none
- hibernation_duration_steps: 1000
- max_wake_latency_ms: 5000
- phenotype_size: 10000
- task_complexity: medium

METRICS
- regeneration_latency_ms < 5000
- retained_capability_after_regeneration > 0.7
- regeneration_cost_ratio < 0.1

SEEDS
42, 123, 456, 789, 101112, 131415, 161718, 192021

STOP_CONDITIONS
- max_compute_seconds_exceeded
- all_seeds_completed
- regeneration_latency_ms > 50000

POSITIVE_MEANING
Regeneration latency < 10x cold retraining and retained capability > 0.7; demand-driven phenotype activation is viable.

NEGATIVE_MEANING
Regeneration latency exceeds 10x cold retraining or retained capability < 0.7; demand-driven activation not viable with current mechanism.

MIXED_MEANING
Regeneration latency acceptable but capability retention marginal, or vice versa; requires further tuning of hibernation state size.
