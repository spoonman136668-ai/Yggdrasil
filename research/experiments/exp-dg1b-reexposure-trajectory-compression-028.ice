{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-REEXPOSURE-TRAJECTORY-COMPRESSION-028",
  "question": "Does repeated exposure compress future developmental trajectories so the same bounded persistent motif reaches a fixed regeneration target in fewer development updates without added capacity?",
  "hypothesis": "By exposure four, median updates-to-target are >=25% lower than exposure one while specificity remains >=0.05, capacity is unchanged, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-025",
    "result_sha256": "16a19741497bfc8a3591bc040ee6a6b78f2af423d24c6d22ce943dc7e279c25a"
  },
  "changed_dimension": "exposure count only: first versus fourth trajectory using identical 256-byte motif and matched resources",
  "seeds": [
    91009,
    92033,
    93047,
    94057,
    95071,
    96079,
    97081,
    98101
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 256,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_updates_per_exposure": 128,
    "exposures": 4
  },
  "thresholds": {
    "median_update_reduction_fraction_exposure4_vs1_gte": 0.25,
    "exposure4_specificity_gte": 0.05,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
