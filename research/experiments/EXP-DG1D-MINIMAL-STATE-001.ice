TITLE: EXP-DG1D-MINIMAL-STATE-001
SCHEMA: ckb-plane.research-experiment.v1
EXPERIMENT: EXP-DG1D-MINIMAL-STATE-001
CANDIDATE: CAND-DG1D-MINIMAL-STATE-001
HARNESS: yggdrasil-isolated

FIXED PARAMETERS
- damage_pattern: none
- development_step_budget: 5000
- genome_size_bytes: 102400
- memory_budget_mb: 512
- population_budget: 1000
- retention_schedule: geometric_0.1_to_10_percent
- task_family: sequential_mnist_permuted

METRICS
- capability_recovery_ratio >= 0.7
- retained_state_bytes_ratio <= 0.05
- regeneration_cost_ratio <= 0.5
- retained_capability_after_sequence >= 0.6

SEEDS
42, 123, 456, 789, 1024, 2048, 4096, 8192

CONTROLS
- Cold retraining from scratch with same compute budget
- Full phenotype retention (upper bound)
- Random initialization with same genome (lower bound)
- Fixed hypernetwork baseline with equivalent persistent storage

STOP CONDITIONS
- All retention levels evaluated
- Compute budget exhausted
- Capability recovery ratio <0.3 for 3 consecutive retention levels
- Regeneration cost ratio >1.0 for any retention level

POSITIVE MEANING
Capability recovery ratio >=0.7 achieved at retained_state_bytes_ratio <=0.05 with regeneration_cost_ratio <=0.5, demonstrating a viable minimal persistent state for regeneration.

NEGATIVE MEANING
Capability recovery ratio remains below 0.7 for all retained_state_bytes_ratio <=0.05, indicating no useful minimal persistent state exists for functional regeneration on this task family.

MIXED MEANING
Capability recovery >0.7 at <5% retained state but regeneration cost ratio >0.5 indicates viable minimal state with inefficient regeneration; recovery <0.7 at all retention levels falsifies minimal state hypothesis for this task family.
