EXPERIMENT_ID: EXP-DG1A-HISTORY-COMPRESSION-001
CANDIDATE_ID: CAND-DG1A-HISTORY-COMPRESSION
HARNESS_ID: yggdrasil-isolated

CONTROLS:
- fixed task similarity matrix
- identical initial genome across seeds
- fixed resource budgets per task
- baseline: independent training per task without developmental history

FIXED_PARAMETERS:
- genome_size: 1024
- max_modules: 64
- resource_budget_per_task: 10000
- similarity_levels: 3
- task_sequence_length: 10

METRICS:
- development_steps_ratio_subsequent_vs_first < 0.7
- active_parameter_growth_per_task < 0.3
- retained_capability_after_sequence > 0.75

SEEDS: 42, 123, 456, 789, 101112, 131415, 161718, 192021
COMPUTE_SECONDS: 1200

STOP_CONDITIONS:
- all seeds complete
- compute budget exhausted
- divergence detected in resource accounting

POSITIVE_MEANING: Statistically significant compression of development trajectories with repeated exposure; reusable developmental motifs demonstrated; supports North Star claim that capability grows faster than permanent structure.
NEGATIVE_MEANING: No measurable compression of development trajectories; repeated exposure does not create reusable motifs; Open Question 3 answered negatively for current mechanism.
MIXED_MEANING: Partial compression observed but not statistically significant across all similarity levels; suggests developmental history helps only for highly similar tasks.
