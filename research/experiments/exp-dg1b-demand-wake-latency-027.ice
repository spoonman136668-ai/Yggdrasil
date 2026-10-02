{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-DEMAND-WAKE-LATENCY-027",
  "question": "Can a capability hibernated into the supported 256-byte persistent motif be reactivated on demand with bounded cold-start latency materially below cold retraining, without increasing persistent or active capacity?",
  "hypothesis": "Median wake-to-target cost is <=25% of cold retraining, recovered specificity >=0.05, wake success >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-025",
    "result_sha256": "16a19741497bfc8a3591bc040ee6a6b78f2af423d24c6d22ce943dc7e279c25a"
  },
  "changed_dimension": "activation mode only: always-active versus hibernate/wake from fixed 256-byte motif",
  "seeds": [
    81031,
    82037,
    83047,
    84053,
    85061,
    86069,
    87083,
    88093
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 256,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_wake_updates": 128,
    "cold_retraining_updates": 512
  },
  "thresholds": {
    "median_wake_cost_fraction_of_cold_lte": 0.25,
    "recovered_specificity_gte": 0.05,
    "wake_success_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
