TITLE: EXP-REGEN-MINSTATE-SWEEP-001
SCHEMA: ckb-plane.research-experiment.v1
EXPERIMENT: EXP-REGEN-MINSTATE-SWEEP-001
CANDIDATE: cand-regen-minstate-sweep
HARNESS: yggdrasil-isolated
TASK: permuted_mnist
ARCHITECTURE: DG-1A
GENOME_SIZE: 100K parameters
PHENOTYPE_SIZE: 1M parameters
REGENERATION_STEPS: 5000
RETAINED_STATE_RATIOS: [0.02, 0.04, 0.06, 0.08, 0.10]
SEEDS: [42, 123, 456, 789, 999]
METRICS: function_recovery_accuracy, regeneration_cost_vs_cold_retrain_ratio, retained_state_bytes_ratio
