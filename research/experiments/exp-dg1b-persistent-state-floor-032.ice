{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-PERSISTENT-STATE-FLOOR-032",
  "question": "Does four-cycle total-lesion regeneration remain supported when informative persistent motif state is reduced from the supported 128 bytes to 64 bytes while the physical 320-byte container and all active resources remain fixed?",
  "hypothesis": "The 64-byte condition retains cycle-four specificity >=0.05, median attenuation versus 128 bytes <=0.02, supporting-seed fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-PERSISTENT-STATE-FLOOR-029",
    "result_sha256": "da3bcfe4cab54752c4b661ff344c7b479ad3cbc1879daff7445d04a651e6bb1f"
  },
  "changed_dimension": "informative persistent-state size only: 128 bytes versus 64 bytes; physical container fixed at 320 bytes",
  "seeds": [
    125419,
    126433,
    127447,
    128461,
    129469,
    130483,
    131497,
    132509
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
    "median_64_cycle4_specificity_gte": 0.05,
    "median_128_minus_64_attenuation_lte": 0.02,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
