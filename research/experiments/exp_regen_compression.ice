schema: ckb-plane.research-experiment-preregistration.v1
experiment_id: EXP-DG1B-REGEN-COMPRESSION-001
candidate_id: CAND-REGEN-COMPRESSION
envelope_id: RYG-b87897df39a9b30054bbedbb0d883524
project: Yggdrasil
lane: YGG-A
baseline_sha: 713e0bf6e8b44c7e0ae4f6f183f8628314776c5b
proposal_sha256: 7b85a3afe47cda46ba9129e89d9cd571592608ff9eff8620c35fb3efe3467ea1
harness_id: yggdrasil-isolated

controls:
  - cold_retraining_baseline_per_task
  - uncompressed_genome_regeneration
  - random_initialization_baseline

fixed_parameters:
  development_budget_steps: 2000
  genome_compression_ratios: [1.0, 2.0, 5.0, 10.0]
  memory_budget_mb: 512
  num_tasks: 5
  population_budget: 100
  retention_state_budget_bytes: 8192
  task_sequence: permuted_mnist_5

metrics:
  - name: regeneration_cost_ratio
    comparator: <
    threshold: 0.5
  - name: retained_capability_ratio
    comparator: '>'
    threshold: 0.8
  - name: genome_size_bytes_per_capability
    comparator: <
    threshold: 8192

seeds: [42, 123, 456, 789, 1024, 2048, 4096, 8192]
compute_seconds: 1800
stop_conditions:
  - regeneration_cost_ratio > 1.5 for any compression level
  - retained_capability_ratio < 0.3 for any compression level
  - development_steps_exceed_budget
  - memory_budget_exceeded

positive_meaning: Regeneration cost ratio < 0.5 AND retained capability ratio > 0.8 across all tested compression levels (1x, 2x, 5x, 10x), confirming that genome compression preserves regenerable phenotypes with cost advantage over cold retraining
negative_meaning: Regeneration cost ratio >= 1.0 or retained capability ratio <= 0.5 at any compression level, falsifying the hypothesis that compact developmental information enables efficient phenotype recovery
mixed_meaning: Regeneration cost ratio < 0.5 for some compression levels but not others, or retained capability ratio between 0.5-0.8, indicating compression-level-dependent tradeoffs requiring further investigation

preregistration_path: research/experiments/exp_regen_compression.ice
test_script_path: research/applications/plane/exp_regen_compression.py
