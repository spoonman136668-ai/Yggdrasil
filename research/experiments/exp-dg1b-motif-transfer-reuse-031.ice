{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-MOTIF-TRANSFER-REUSE-031",
  "question": "Can one bounded developmental motif behave like a reusable organ by accelerating regeneration on a second related task without providing the same benefit to an unrelated task?",
  "hypothesis": "Transferred 192-byte motif state reduces related-task updates-to-target by >=25% versus cold, preserves related specificity >=0.05, yields supporting-seed fraction >=0.75, while unrelated-task update reduction remains <=10% and collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": [
    {
      "experiment": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-026",
      "result_sha256": "59efb788f4180d6ded965e904d4c174ef31141c0ccb65663caa4bd0e00999eec"
    },
    {
      "experiment": "EXP-DG1B-REEXPOSURE-TRAJECTORY-COMPRESSION-028",
      "result_sha256": "0ee964b79623c2e29454e661154170d7dc11eb97711eba3cae603c75fb8a2d6f"
    }
  ],
  "changed_dimension": "task affinity only: related transfer versus unrelated transfer; persistent bytes and adaptation budgets fixed",
  "seeds": [
    117331,
    118343,
    119359,
    120371,
    121379,
    122389,
    123397,
    124409
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 192,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_updates": 128,
    "cold_updates": 512
  },
  "thresholds": {
    "median_related_update_reduction_gte": 0.25,
    "median_related_specificity_gte": 0.05,
    "supporting_seed_fraction_gte": 0.75,
    "median_unrelated_update_reduction_lte": 0.1,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
