TITLE: EXP-REGEN-MINSTATE-001
SCHEMA: yggdrasil.research-experiment.v1
EXPERIMENT: EXP-REGEN-MINSTATE-001
CANDIDATE: cand-minstate-001
HARNESS: yggdrasil-isolated

QUESTION
What is the smallest persistent state that enables functional regeneration with cost < 0.4x cold retrain?

HYPOTHESIS
A compressed developmental summary of 2% phenotype bytes suffices for >90% function recovery and regeneration cost < 0.4x cold retrain.

CONTROLS
- no-compression baseline (100% state)
- random compression baseline
- cold retrain from scratch

FIXED PARAMETERS
compression_method: learned developmental summary
phenotype_size: 1M parameters
regeneration_budget_steps: 10000
task_sequence: 5 diverse tasks

METRICS
- function_recovery_accuracy >= 0.9
- regeneration_cost_vs_cold_retrain_ratio < 0.4
- retained_state_bytes_ratio <= 0.02

SEEDS
42, 123, 456, 789, 101112

COMPUTE_SECONDS
1200

STOP_CONDITIONS
- all compression ratios evaluated
- compute budget exceeded
- regeneration fails for all seeds at a given ratio

POSITIVE_MEANING
At least one compression ratio <=2% achieves both thresholds; supports that compact developmental information enables low-cost regeneration.

NEGATIVE_MEANING
No compression ratio <=2% achieves both thresholds; minimal persistent state is larger than hypothesized, weakening the developmental thesis.

MIXED_MEANING
Some compression ratios meet one threshold but not both; indicates trade-off curve needing further exploration.
