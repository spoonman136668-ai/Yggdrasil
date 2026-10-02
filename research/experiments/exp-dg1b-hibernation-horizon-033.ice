{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-HIBERNATION-HORIZON-033",
  "question": "How far can synthetic inactivity be extended beyond the supported 64-step interval before the fixed 256-byte wake state loses bounded reactivation cost?",
  "hypothesis": "Across intervals 64, 256, and 1024, median wake-cost inflation at interval 1024 versus 64 is <=25%, interval-1024 specificity remains >=0.05, supporting-seed fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-HIBERNATION-RETENTION-030",
    "result_sha256": "9c88ec08cf2cddb59190581082c66ffa1b1366f7551a89e56d38f57d80690ea0"
  },
  "changed_dimension": "inactive interval length only: 64 versus 256 versus 1024; persistent bytes, active parameters, wake rule, target, and budgets fixed",
  "seeds": [
    133519,
    134537,
    135547,
    136559,
    137573,
    138581,
    139597,
    140603
  ],
  "intervals": [
    64,
    256,
    1024
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 256,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_wake_updates": 128
  },
  "thresholds": {
    "median_interval1024_vs64_wake_cost_inflation_lte": 0.25,
    "median_interval1024_specificity_gte": 0.05,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
