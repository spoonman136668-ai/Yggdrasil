EXPERIMENT: EXP-DG1A-DEVHIST-001
CANDIDATE: cand-devhist-001
HARNESS: yggdrasil-isolated
BASELINE: 1583ee7d6b179a98085186fd7ba7e7ee9d456795

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable?

HYPOTHESIS
A bounded developmental-history log enables phenotype regeneration at less than 50% cold-retraining cost while retaining more than 80% capability after 10 task switches.

CONTROLS
- Cold retraining from random initialization (same architecture, same compute budget)
- Fixed-architecture baseline with full parameter retention
- Random lineage log ablation (shuffle operation order)

FIXED PARAMETERS
max_lineage_ops=5000
memory_budget_mb=512
population_budget=1000
regeneration_trials=5
task_sequence_length=10

METRICS
regeneration_cost_ratio < 0.5
retained_capability_ratio > 0.8
genome_size_bytes_per_capability < 10000

SEEDS
42, 123, 456, 789, 999

COMPUTE_SECONDS
1200

STOP CONDITIONS
- regeneration_cost_ratio >= 0.95 for 3 consecutive seeds
- retained_capability_ratio < 0.5 for any seed
- genome_size_bytes_per_capability > 50000
- wall_time_exceeds_1200s

POSITIVE_MEANING
Regeneration cost ratio < 0.5 and retained capability ratio > 0.8; developmental-history enables compact phenotype regeneration.

NEGATIVE_MEANING
Regeneration cost ratio >= 0.5 or retained capability ratio <= 0.8; developmental-history does not provide compact recoverable capability.

MIXED_MEANING
Regeneration cost reduced but capability retention marginal (0.5-0.8); investigate which developmental operations contribute most to recoverable function.
