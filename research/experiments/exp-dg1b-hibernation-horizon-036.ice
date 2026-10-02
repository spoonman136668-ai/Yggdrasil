{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-HIBERNATION-HORIZON-036",
  "question": "How far can synthetic inactivity extend beyond the supported 1024-step horizon before the fixed 256-byte wake state loses bounded reactivation cost?",
  "hypothesis": "Across intervals 1024, 4096, and 16384, median wake-cost inflation at 16384 versus 1024 is <=25%, interval-16384 specificity remains >=0.05, supporting-seed fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-HIBERNATION-HORIZON-033",
    "result_sha256": "4f404f3ca6d95dc32d1e37c6748f3a36394a2a01c69c5d4b55214510670b47bf"
  },
  "changed_dimension": "inactive interval length only: 1024 versus 4096 versus 16384; persistent bytes, active parameters, wake rule, target, and budgets fixed",
  "seeds": [
    157793,
    158803,
    159809,
    160813,
    161827,
    162833,
    163841,
    164849
  ],
  "intervals": [
    1024,
    4096,
    16384
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
    "median_interval16384_vs1024_wake_cost_inflation_lte": 0.25,
    "median_interval16384_specificity_gte": 0.05,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
