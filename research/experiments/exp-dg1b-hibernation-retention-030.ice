{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-HIBERNATION-RETENTION-030",
  "question": "Does the supported 256-byte wake state retain bounded reactivation cost after progressively longer synthetic inactive intervals without refresh?",
  "hypothesis": "Across inactive intervals 1, 16, and 64, median wake-cost inflation at interval 64 versus interval 1 is <=25%, interval-64 specificity remains >=0.05, supporting-seed fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-DEMAND-WAKE-LATENCY-027",
    "result_sha256": "c6d71850a219e47b6ea3021abcbefc3db166c64462ddc7f16de02e98449a40e1"
  },
  "changed_dimension": "inactive interval length only; persistent bytes, active parameters, wake rule, target, and budgets fixed",
  "seeds": [
    109229,
    110233,
    111253,
    112267,
    113279,
    114299,
    115303,
    116329
  ],
  "intervals": [
    1,
    16,
    64
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
    "median_interval64_vs1_wake_cost_inflation_lte": 0.25,
    "median_interval64_specificity_gte": 0.05,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
