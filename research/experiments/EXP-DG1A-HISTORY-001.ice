EXPERIMENT: EXP-DG1A-HISTORY-001
CANDIDATE: CAND-DG1A-HISTORY-001
HARNESS: yggdrasil-isolated

QUESTION
Does repeated developmental exposure compress future development trajectories?

HYPOTHESIS
Repeated developmental exposure compresses future development trajectories, reducing steps to functional phenotype.

CONTROLS
- fixed random seeds
- identical task sequence order
- baseline non-developmental learner

FIXED PARAMETERS
- development_budget_per_task: 1000
- memory_budget_mb: 512
- performance_threshold: 0.9
- population_cap: 50
- task_sequence_length: 5

METRICS
- development_steps_ratio_taskN_task1 < 0.8
- trajectory_compression_ratio > 1.2
- active_parameter_growth_per_task < 0.9

SEEDS
42, 123, 456, 789, 101112, 131415, 161718, 192021

COMPUTE_SECONDS
1200

STOP CONDITIONS
- development_steps_ratio >= 1.0 for 3 consecutive tasks
- compute_seconds > 1200
- population_cap reached

POSITIVE MEANING
Significant trajectory compression (>20% reduction in development steps); evidence for developmental history benefit.

NEGATIVE MEANING
No developmental trajectory compression; development steps per task remain constant or increase; North Star claim weakened.

MIXED MEANING
Partial compression observed but not statistically significant across seeds; developmental history effect inconclusive.
