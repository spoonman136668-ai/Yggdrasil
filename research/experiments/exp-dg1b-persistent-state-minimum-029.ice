{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-029",
  "question": "Can the supported 192-byte informative persistent motif be reduced to 128 bytes while preserving four-cycle total-lesion regeneration?",
  "hypothesis": "A 128-byte informative motif in the same 320-byte container retains cycle-four specificity >=0.05, attenuation versus 192 bytes <=0.02, support fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "7f05b892f9448891d929339dbddb357b025f98dd",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-026",
    "result_sha256": "59efb788f4180d6ded965e904d4c174ef31141c0ccb65663caa4bd0e00999eec",
    "classification": "supported"
  },
  "changed_dimension": "informative persistent-state size only: 192 bytes versus 128 bytes; physical transfer container remains 320 bytes",
  "seeds": [
    111013,
    112019,
    113029,
    114041,
    115049,
    116059,
    117071,
    118081
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 512,
    "matched_block_count": 128,
    "resource_record_count": 512,
    "updates_per_cycle": 128,
    "cycles": [
      1,
      2,
      3,
      4
    ]
  },
  "thresholds": {
    "median_128_cycle4_specificity_gte": 0.05,
    "median_192_minus_128_attenuation_lte": 0.02,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
