TITLE: EXP-DG1B-MINSTATE-001
SCHEMA: ckb-plane.research-experiment-preregistration.v1
PROJECT: Yggdrasil
LANE: YGG-A
EXPERIMENT_ID: EXP-DG1B-MINSTATE-001
BASELINE_SHA: ed4bef967197f253718fe5445f3329dae99f4a4a
HARNESS: yggdrasil-isolated

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable?

HYPOTHESIS
A persistent state comprising genome plus bounded retained context (<5% of active phenotype size) enables phenotype regeneration with capability recovery >0.85 and regeneration cost ratio <0.55.

CONTROLS
- DG-1B baseline regeneration with full context (from YRE-0705837a9e2232d70cba26a318f38baa)
- Cold retraining from scratch for each task
- Regeneration with zero retained context (genome only)

FIXED_PARAMETERS
- damage_type: full_phenotype_discard
- genome_size: fixed_per_task
- memory_budget_mb: 512
- population_budget: 1000_modules
- retained_context_fractions: [0.0, 0.01, 0.02, 0.05, 0.10]
- task_sequence: 5_tasks_shared_substructure

METRICS
- capability_recovery_ratio >= 0.85
- regeneration_cost_ratio < 0.55
- retained_state_fraction <= 0.05
- regeneration_steps_ratio <= 0.6

SEEDS
42, 123, 456, 789, 1024, 2048, 4096, 8192

COMPUTE_SECONDS
1200

STOP_CONDITIONS
- All retained context fractions evaluated
- Any fraction meets both primary thresholds (early success)
- Compute budget exhausted
- Harness error or timeout

INTERPRETATION
Positive: at least one retained context fraction <=5% achieves capability recovery >=0.85 and regeneration cost ratio <0.55.
Negative: no retained context fraction achieves both primary thresholds.
Mixed: recovery and cost thresholds trade off across fractions.
