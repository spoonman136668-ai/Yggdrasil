schema: ckb-plane.research-experiment-preregistration.v1
envelope_id: RYG-99a9903f65aba2896853c0d9693c3b50
experiment_id: EXP-REGEN-COST-001
candidate_id: REGEN-COST-001
harness_id: yggdrasil-isolated
controls:
  - cold_retrain_baseline
  - fixed_wake_info_budget
  - identical_task_distribution
fixed_parameters:
  memory_budget_mb: "512"
  population_budget: "10000"
  task_sequence_length: "5"
  wake_info_bytes_per_active_parameter: "0.1"
metrics:
  - name: regeneration_cost_vs_cold_retrain_ratio
    comparator: "<="
    threshold: 0.5
  - name: function_recovery_accuracy
    comparator: ">="
    threshold: 0.85
seeds: [42, 123, 456, 789, 101112, 131415, 161718, 192021]
compute_seconds: 1800
stop_conditions:
  - max_compute_seconds_exceeded
  - regeneration_cost_ratio_stable
  - all_seeds_completed
negative_result_valid: true
