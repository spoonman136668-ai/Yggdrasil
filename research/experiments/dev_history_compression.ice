TITLE: Developmental History Compression
EXPERIMENT_ID: EXP-DEV-HIST-COMPRESSION-001
CANDIDATE_ID: CAND-DEV-HIST-COMPRESSION
HARNESS: yggdrasil-isolated

QUESTION
Does repeated exposure to related tasks compress future developmental trajectories, measured as reduced developmental steps to acquire new capabilities?

HYPOTHESIS
Repeated exposure to related tasks compresses future developmental trajectories, reducing the number of developmental steps needed to acquire new capabilities.

FALSIFIER
If developmental steps for new tasks after sequence learning do not decrease significantly compared to learning from scratch (p > 0.05, effect size < 0.2), the compression hypothesis is falsified.

CONTROLS
- scratch_learning_control: learn 6th task from scratch without prior sequence
- random_sequence_control: learn 5 unrelated tasks before 6th target task
- fixed_architecture_control: same architecture without developmental operations

FIXED_PARAMETERS
- development_budget_per_task: 1000_steps
- memory_budget_mb: 512
- population_budget: 100_modules
- relatedness_metric: permutation_distance
- target_accuracy: 0.9
- task_family: permuted_mnist_sequence

METRICS
- developmental_steps_ratio < 0.8
- compression_effect_size > 0.5
- final_accuracy >= 0.9

SEEDS
42, 123, 456, 789, 101112, 131415, 161718, 192021

COMPUTE_SECONDS: 1200
STOP_CONDITIONS
- max_compute_seconds_exceeded
- all_seeds_completed
- statistical_significance_reached_p_0.05

POSITIVE_MEANING
Statistically significant reduction in developmental steps for new tasks after related task sequence, with effect size >0.5. Supports North Star claim that accumulated capability grows faster than permanent structure.

NEGATIVE_MEANING
No significant reduction in developmental steps for new tasks after sequence learning. Developmental history does not compress future trajectories under tested conditions.

MIXED_MEANING
Partial compression observed but not statistically significant, or compression only for highly similar tasks. Suggests developmental history helps only in narrow regimes.
