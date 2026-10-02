{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-026",
  "question": "How far can persistent informative motif state be reduced below the supported 256-byte condition while preserving four-cycle total-lesion regeneration?",
  "hypothesis": "A 192-byte informative motif in a byte-matched 320-byte container retains cycle-four specificity >=0.05, attenuation versus 256 bytes <=0.02, support fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-025",
    "result_sha256": "16a19741497bfc8a3591bc040ee6a6b78f2af423d24c6d22ce943dc7e279c25a"
  },
  "changed_dimension": "informative persistent-state size only: 256 vs 192 bytes; physical transfer container fixed at 320",
  "seeds": [
    71023,
    72047,
    73061,
    74071,
    75083,
    76091,
    77101,
    78121
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
    "median_192_cycle4_specificity_gte": 0.05,
    "median_256_minus_192_attenuation_lte": 0.02,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
