schema: ckb-plane.research-experiment-preregistration.v1
experiment_id: EXP-DEVHIST-001
candidate_id: cand-devhist-001
harness_id: yggdrasil-isolated
controls:
  - DG-1A baseline without lineage tracking
  - Full-checkpoint regeneration baseline
  - Random-lineage regeneration control
fixed_parameters:
  damage_fraction: "0.0"
  lineage_compression_ratio: "0.1"
  max_lineage_checkpoints: "100"
  population_budget: "1000"
  regeneration_budget_steps: "2000"
  task_sequence_length: "5"
metrics:
  - name: lineage_size_ratio
    comparator: "<="
    threshold: 0.1
  - name: regeneration_cost_ratio
    comparator: "<="
    threshold: 2
  - name: regeneration_accuracy
    comparator: ">="
    threshold: 0.9
  - name: wake_latency_ratio
    comparator: "<="
    threshold: 5
seeds:
  - 42
  - 123
  - 456
  - 789
compute_seconds: 1200
stop_conditions:
  - regeneration_cost_ratio > 3.0 for 3 consecutive seeds
  - lineage_size_ratio > 0.2
  - compute_seconds > 1200
