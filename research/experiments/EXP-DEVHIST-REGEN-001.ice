schema: ckb-plane.research-experiment.v1
experiment_id: EXP-DEVHIST-REGEN-001
candidate_id: CAND-DEVHIST-REGEN-001
harness_id: yggdrasil-isolated
lane: YGG-A
controls:
  - random_reinitialization_baseline
  - full_retraining_baseline
  - fixed_architecture_baseline
  - shuffled_lineage_control
fixed_parameters:
  development_steps_per_task: "5000"
  dormancy_steps: "5000"
  genome_encoding: lineage_checkpoints
  population_size: "256"
  regeneration_budget_steps: "2000"
  task_sequence: omniglot,miniimagenet,cifar100
metrics:
  - name: regeneration_cost_ratio
    comparator: <
    threshold: 0.6
  - name: capability_recovery_ratio
    comparator: >
    threshold: 0.8
  - name: lineage_advantage_ratio
    comparator: <
    threshold: 0.8
seeds: [42, 123, 456, 789, 1024, 2048, 4096, 8192]
compute_seconds: 1800
stop_conditions:
  - regeneration_cost_ratio > 0.9 for 3 consecutive seeds
  - capability_recovery_ratio < 0.5 for any seed
  - compute_seconds > 1800
  - all_seeds_completed
negative_result_valid: true
no_post_result_tuning: true
