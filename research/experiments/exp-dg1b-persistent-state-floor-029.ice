{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-PERSISTENT-STATE-FLOOR-029",
  "question": "Does four-cycle total-lesion regeneration remain supported when informative persistent state is reduced from the supported 192 bytes to 128 bytes while the physical transfer container remains 320 bytes?",
  "hypothesis": "The 128-byte condition retains cycle-four specificity >=0.05, median attenuation versus 192 bytes <=0.02, supporting-seed fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-026",
    "result_sha256": "59efb788f4180d6ded965e904d4c174ef31141c0ccb65663caa4bd0e00999eec"
  },
  "changed_dimension": "informative persistent-state size only: 192 versus 128 bytes; transfer container fixed at 320",
  "seeds": [
    101111,
    102121,
    103123,
    104147,
    105173,
    106189,
    107197,
    108217
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "trial_count": 512,
    "matched_block_count": 128,
    "resource_record_count": 512,
    "updates_per_cycle": 128
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
