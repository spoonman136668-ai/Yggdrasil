TITLE: DG-1B Functional Regeneration Baseline
EXPERIMENT: EXP-DG1B-REGEN-001
CANDIDATE: CAND-DG1B-REGEN-001
HARNESS: yggdrasil-isolated

QUESTION
What is the smallest useful persistent state that makes a discarded phenotype regenerable with cost and accuracy advantages over cold retraining?

HYPOTHESIS
A phenotype discarded after learning a task sequence can be functionally regenerated from its developmental genome plus bounded retained state at <50% of cold retraining cost with >90% accuracy and >90% wake latency.

CONTROLS
- cold_retraining_baseline
- fixed_routing_baseline
- hypernetwork_baseline

FIXED PARAMETERS
memory_budget_mb: 512
population_budget: 1000
regeneration_trials: 10
task_sequence_length: 5

METRICS
- regeneration_cost_ratio < 0.5
- regeneration_accuracy >= 0.9
- wake_latency_ratio < 0.9
- retained_capability_ratio >= 0.85

SEEDS
42, 123, 456, 789, 999, 111, 222, 333

COMPUTE_SECONDS
1800

STOP CONDITIONS
- regeneration_cost_ratio >= 0.8 for 3 consecutive seeds
- regeneration_accuracy < 0.7 for any seed
- compute_seconds exceeded

POSITIVE MEANING
Functional regeneration from genome plus retained state costs <50% of cold retraining with >90% accuracy and <90% wake latency, confirming DG-1B baseline viability.

NEGATIVE MEANING
Regeneration cost approaches or exceeds cold retraining, or accuracy drops below 90%, indicating developmental thesis weakening per falsifiable failure modes.

MIXED MEANING
Regeneration cost between 50-80% of cold retraining with acceptable accuracy but high latency, suggesting need for optimization before open-ended structural operations.
