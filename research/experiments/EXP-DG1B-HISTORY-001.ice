schema: ckb-plane.research-experiment-preregistration.v1
experiment_id: EXP-DG1B-HISTORY-001
candidate_id: CAND-DG1B-HISTORY-001
harness_id: yggdrasil-isolated
controls:
  - DG-1B baseline from YRE-ac3ea09dea328baff099fe9a6c27bd48 (no history retention)
  - Full-lineage regeneration (100% history retained)
  - Random initialization regeneration (0% history)
fixed_parameters:
  history_retention_fractions: "[1.0, 0.5, 0.25, 0.1, 0.0]"
  memory_budget_mb: "512"
  population_budget: "1000"
  regeneration_steps: "5000"
  task_suite: dg1b_standard
metrics:
  - name: regeneration_cost_ratio
    comparator: "<"
    threshold: 0.5
  - name: capability_recovery_ratio
    comparator: ">"
    threshold: 0.85
  - name: regeneration_steps_ratio
    comparator: "<"
    threshold: 0.6
  - name: transfer_capability_retention
    comparator: ">"
    threshold: 0.8
seeds: [42, 123, 456, 789, 1024, 2048, 4096, 8192]
compute_seconds: 1200
stop_conditions:
  - regeneration_cost_ratio > 0.9 for 3 consecutive retention fractions
  - capability_recovery_ratio < 0.7 for any retention fraction
  - compute_seconds > 1200
  - all retention fractions evaluated
positive_meaning: At least one history retention fraction achieves regeneration_cost_ratio < 0.5 and capability_recovery_ratio > 0.85.
negative_meaning: No history retention fraction achieves both regeneration_cost_ratio < 0.5 and capability_recovery_ratio > 0.85.
mixed_meaning: Regeneration cost ratio < 0.5 achieved but capability recovery < 0.85, or vice versa.
