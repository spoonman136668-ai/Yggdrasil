{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-DEMAND-ACTIVE-COMPUTE-040",
  "question": "For four retained related capabilities under a fixed request trace, can demand-driven wake/hibernate keep active parameter-time materially below an always-active phenotype bank while preserving bounded wake latency and task success?",
  "hypothesis": "Demand-driven execution retains >=0.75 capability success, median wake cost <=25% of cold retraining, and active-parameter-time per request <=0.40 of the always-active four-phenotype bank, with unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": [
    {
      "experiment": "EXP-DG1B-DEMAND-WAKE-LATENCY-027",
      "finding": "wake median 7 updates vs 41 cold"
    },
    {
      "experiment": "EXP-DG1B-HIBERNATION-HORIZON-033",
      "result_sha256": "4f404f3ca6d95dc32d1e37c6748f3a36394a2a01c69c5d4b55214510670b47bf"
    },
    {
      "experiment": "EXP-DG1B-CAPABILITY-SEQUENCE-SCALING-036",
      "result_sha256": "7f0db8f14d7a334cd062bdf4afa9628ae0bc8df32a9cd9a8978f53837928f85e"
    }
  ],
  "changed_dimension": "activation policy only: demand-driven one-active-phenotype wake/hibernate versus four always-active phenotypes",
  "seeds": [
    190159,
    191173,
    192181,
    193189,
    194201,
    195211,
    196219,
    197233
  ],
  "request_trace": {
    "requests": 64,
    "task_count": 4,
    "family": "deterministic round-robin/burst mixed trace frozen by seed"
  },
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameters_per_phenotype": 128,
    "shared_persistent_bytes": 192,
    "max_wake_updates": 128,
    "cold_updates": 512,
    "resident_byte_count": 1344
  },
  "thresholds": {
    "retained_capability_success_fraction_gte": 0.75,
    "median_wake_cost_fraction_of_cold_lte": 0.25,
    "active_parameter_time_ratio_vs_always_active_lte": 0.4,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
