{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-MOTIF-AFFINITY-GRADIENT-034",
  "question": "Does reusable-motif acceleration scale with task affinity rather than acting as a nonspecific optimization when persistent bytes and adaptation budgets are fixed?",
  "hypothesis": "Median update reduction is monotone with source-feature overlap (3/4 > 2/4 > 1/4 > 0/4), the 3/4 condition reduces updates by >=25% with specificity >=0.05, the 0/4 condition reduces updates by <=10%, and unrelated collateral remains <=0.03.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-MOTIF-TRANSFER-REUSE-031",
    "result_sha256": "3aeffd127cf7d1567c8f9943b774b95df8873c34a5370823900d1d9e92ddbb85"
  },
  "changed_dimension": "task affinity only: 3/4, 2/4, 1/4, and 0/4 source-feature overlap; motif bytes and adaptation budgets fixed",
  "seeds": [
    141617,
    142631,
    143641,
    144659,
    145667,
    146681,
    147691,
    148711
  ],
  "overlap_levels": [
    0.75,
    0.5,
    0.25,
    0
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
    "monotone_median_update_reduction_required": true,
    "median_overlap075_update_reduction_gte": 0.25,
    "median_overlap075_specificity_gte": 0.05,
    "median_overlap000_update_reduction_lte": 0.1,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
