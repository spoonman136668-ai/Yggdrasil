{
  "schema": "ckb-plane.research-experiment-registration.v1",
  "experiment_id": "EXP-REGEN-MINSTATE-SWEEP-002",
  "candidate_id": "CAND-REGEN-MINSTATE-001",
  "harness_id": "yggdrasil-isolated",
  "controls": [
    "cold_retrain_baseline",
    "random_init_baseline",
    "full_phenotype_retained_baseline"
  ],
  "fixed_parameters": {
    "architecture": "yggdrasil-dg1a",
    "development_step_budget": "10000",
    "memory_budget_mb": "512",
    "population_budget": "1000",
    "retained_state_sweep": "0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.20",
    "task": "mnist-continual"
  },
  "metrics": [
    {
      "name": "function_recovery_accuracy",
      "comparator": ">",
      "threshold": 0.5
    },
    {
      "name": "regeneration_cost_vs_cold_retrain_ratio",
      "comparator": "<",
      "threshold": 0.5
    },
    {
      "name": "retained_state_bytes_ratio",
      "comparator": "<=",
      "threshold": 0.1
    }
  ],
  "seeds": [42, 123, 456, 789, 101112, 131415, 161718, 192021],
  "compute_seconds": 1800,
  "stop_conditions": [
    "all_sweep_points_completed",
    "compute_seconds_exceeded",
    "harness_error"
  ]
}
