TITLE: EXP-REGEN-STATE-001
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT: EXP-REGEN-STATE-001
CANDIDATE: CAND-REGEN-STATE-001
ENVELOPE: RYG-680373ee83c82f276a779308a67443f6
HARNESS: yggdrasil-isolated
BASELINE: b3b89916bd28e7c23ba6b9ca2242b0320fa21377

QUESTION
What is the minimal retained state enabling regeneration at <50% cold-retraining cost and <1.5x wake latency?

HYPOTHESIS
Regeneration cost and wake latency decrease monotonically with retained state size; a sweet spot exists at 5-15% of active phenotype bytes where regeneration_cost_ratio < 0.5 and wake_latency_ratio < 1.5.

CONTROLS
- cold_retraining_from_scratch_same_architecture
- fixed_architecture_fine_tuning_baseline
- random_retained_state_same_size_control

FIXED PARAMETERS
- architecture: yggdrasil-dg1a
- development_steps_per_regeneration: 1000
- memory_budget_mb: 512
- population_budget: 10000
- retained_state_fractions: [0.01, 0.05, 0.10, 0.15, 0.25, 0.50]
- seed: 42
- task_suite: continual-mnist-permuted-5

METRICS
- regeneration_cost_ratio < 0.5
- wake_latency_ratio < 1.5
- regeneration_accuracy >= 0.9

SEEDS
[42, 123, 456, 789, 101112, 131415, 161718, 192021]

COMPUTE_SECONDS: 1800
STOP_CONDITIONS
- regeneration_cost_ratio > 1.0 for any condition
- wake_latency_ratio > 3.0 for any condition
- development_steps_exceeded
- memory_budget_exceeded
- all_seeds_completed

POSITIVE_MEANING
Exists retained state fraction in [5%, 15%] where regeneration_cost_ratio < 0.5, wake_latency_ratio < 1.5, and regeneration_accuracy >= 0.9.

NEGATIVE_MEANING
For all retained state fractions <= 25%, either regeneration_cost_ratio >= 0.5 or wake_latency_ratio >= 1.5 or regeneration_accuracy < 0.9.

MIXED_MEANING
Regeneration cost decreases with retained state but wake latency plateaus above 1.5x, or accuracy target is met only above 25% retained state.
