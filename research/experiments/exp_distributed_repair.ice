TITLE: Distributed Repair Experiment
EXPERIMENT: EXP-DIST-REPAIR-001
CANDIDATE: CAND-DEV-REPAIR-001
HARNESS: yggdrasil-isolated

QUESTION
Can distributed local repair operations recover function after targeted damage without global coordination, and at what cost relative to full retraining?

HYPOTHESIS
Local developmental repair operations can restore impaired function using surviving structure and bounded-neighborhood dynamics, achieving repair cost ratio < 0.5 and recovery accuracy > 0.85.

CONTROLS
- Cold retraining from random initialization
- Global retraining from checkpoint
- Sham repair (no repair operations, only continued training)

FIXED PARAMETERS
damage_patterns=targeted_ablation,random_ablation,structural_lesion
memory_budget_mb=512
neighborhood_radius=2
population_budget=1000
repair_budget_steps=500
task_suite=continual_learning_benchmark_v1

METRICS
repair_cost_ratio < 0.5
recovery_accuracy > 0.85
repair_steps < 500
active_parameter_growth_during_repair < 0.1

SEEDS
42, 123, 456, 789, 101112

STOP CONDITIONS
repair_steps >= 500
recovery_accuracy >= 0.95
repair_cost_ratio >= 1.0
population_budget_exceeded
memory_budget_exceeded

INTERPRETATION
Positive: Local repair operations achieve repair_cost_ratio < 0.5 and recovery_accuracy > 0.85 across multiple damage patterns, demonstrating distributed repair capability without global coordination.
Negative: Local repair operations cannot recover function cost-effectively (repair_cost_ratio >= 0.5 or recovery_accuracy <= 0.85), suggesting global coordination is necessary for functional restoration.
Mixed: Repair succeeds on some damage patterns but not others, or cost ratio improves for simple ablations but not complex lesions, indicating bounded applicability of local repair.
