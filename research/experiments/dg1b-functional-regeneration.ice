TITLE: DG-1B Functional Regeneration
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT: YGG-A74-DG1B-REGENERATION
HARNESS: yggdrasil-isolated
BASELINE_SHA: 5e9092ba28ec20a5adeedc8b3fb8e7294e566f6b

QUESTION
Can discarded phenotype be functionally regenerated from genome plus bounded retained state at materially lower cost than cold retraining?

HYPOTHESIS
Local REPAIR operations using surviving structure and developmental dynamics can restore >80% function at <50% cold-retraining cost for targeted ablations.

CONTROLS
- Cold retraining from scratch with identical architecture and data
- Fixed-topology baseline with matched parameter count
- Sham regeneration (genome present but REGENERATE disabled)

FIXED_PARAMETERS
- genome_compression: lz4
- memory_budget_mb: 512
- population_cap: 100
- prune_fraction: 0.3
- retained_state_budget_bytes: 1048576
- seed: 42
- task_family: omniglot_split

METRICS
- regeneration_cost_ratio < 0.5
- capability_recovery_fraction > 0.8
- persistent_bytes_per_capability < 1000000
- development_steps_to_recovery < 1000

SEEDS
42, 123, 456, 789, 101112

COMPUTE_SECONDS
1800

STOP_CONDITIONS
- Regeneration completes (capability_recovery_fraction >= 0.95 or plateau > 50 steps)
- Development steps exceed 2000
- Persistent bytes exceed 2x budget
- Infrastructure failure detected

INTERPRETATION
Positive: all four metric thresholds pass.
Negative: regeneration cost ratio >= 0.5 or capability recovery fraction <= 0.5.
Mixed: capability recovery fraction 0.5-0.8 with cost ratio < 0.5.

SAFETY
- preregister_before_run: true
- no_post_result_tuning: true
- negative_result_valid: true
- activation_authorized: false
- execution_authorized: false
- repository_mutation_authorized: false
- requires_human_review: false
