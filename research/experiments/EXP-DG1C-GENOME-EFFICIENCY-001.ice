SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT: EXP-DG1C-GENOME-EFFICIENCY-001
CANDIDATE: CAND-DG1C-GENOME-EFFICIENCY
HARNESS: yggdrasil-isolated

QUESTION: Does developmental history compression yield sublinear genome growth with high capability retention across task sequences?
HYPOTHESIS: Developmental history can be compressed into a genome that grows sublinearly with task count while maintaining >0.85 retained capability ratio after 5-task sequences.
FALSIFIER: If genome size grows linearly with task count while retained capability drops below 0.7, the compression hypothesis fails.

CONTROLS:
- cold-retraining baseline per task
- fixed-genome-size ablation
- random-genome initialization

FIXED_PARAMETERS:
- development_steps_per_task: 1000
- genome_checkpoint_interval: 200
- memory_budget_mb: 512
- population_budget: 1000
- task_sequence_length: 5

METRICS:
- genome_size_bytes_per_capability < 5000
- retained_capability_ratio > 0.85
- regeneration_cost_ratio < 0.5

SEEDS: 42, 123, 456, 789, 1024, 2048, 4096, 8192
COMPUTE_SECONDS: 1200
STOP_CONDITIONS:
- genome_size_bytes_per_capability > 10000 for 3 consecutive tasks
- retained_capability_ratio < 0.5 at any checkpoint
- compute_seconds > 1200
- development_steps > 5000 total

POSITIVE_MEANING: Genome size per capability <5000 bytes AND retained capability ratio >0.85 AND regeneration cost ratio <0.5. Sublinear compression with high fidelity confirmed.
NEGATIVE_MEANING: Genome grows linearly with tasks OR retained capability ratio <0.7 OR regeneration cost ratio >0.5. Compression hypothesis falsified.
MIXED_MEANING: Sublinear genome growth achieved but capability retention marginal (0.7-0.85), or high retention but linear genome growth. Requires mechanism refinement.
