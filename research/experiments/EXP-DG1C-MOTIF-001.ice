TITLE: EXP-DG1C-MOTIF-001
SCHEMA: ckb-plane.research-experiment-preregistration.v1
EXPERIMENT: EXP-DG1C-MOTIF-001
CANDIDATE: cand-motif-transfer
HARNESS: yggdrasil-isolated

QUESTION
Can developmental lineage encode reusable motifs analogous to organs rather than task-specific copies?

HYPOTHESIS
Developmental lineage encodes reusable motifs analogous to organs rather than task-specific copies, enabling cross-task transfer that exceeds what task similarity alone predicts.

FALSIFIER
If cross-task motif transfer ratio remains below 0.3 and structural reuse is negligible after controlling for task similarity, the organ-like motif hypothesis is falsified.

CONTROLS
- random initialization baseline
- task-similarity matched baseline
- fixed hypernetwork baseline
- adapter baseline

FIXED PARAMETERS
- developmental budget: 10000 steps
- memory budget: 512 MB
- population limit: 100 modules
- seed: 42
- sequence length: 5 tasks
- task families: vision, language, control

METRICS
- cross_task_motif_transfer_ratio > 0.3
- structural_reuse_ratio > 0.25
- active_parameter_growth_per_task < 0.15
- capability_recovery_ratio > 0.85

SEEDS
42, 123, 456, 789, 101112

COMPUTE_SECONDS
1800

STOP_CONDITIONS
- developmental budget exhausted
- capability recovery ratio < 0.5 for 3 consecutive tasks
- active parameter growth exceeds 2x baseline

POSITIVE_MEANING
Cross-task motif transfer ratio > 0.3 and structural reuse ratio > 0.25 with capability recovery > 0.85 demonstrates developmental lineage encodes reusable motifs that transfer across task families, supporting the North Star claim that capability can grow faster than permanent structure.

NEGATIVE_MEANING
Cross-task motif transfer ratio <= 0.3 and structural reuse ratio <= 0.25 indicates developmental lineage does not encode reusable organ-like motifs; transfer is task-specific or explained by task similarity alone.

MIXED_MEANING
Partial motif transfer with high structural reuse but low capability recovery suggests motifs capture structure but not function; high capability recovery with low structural reuse suggests functional convergence without developmental reuse.
