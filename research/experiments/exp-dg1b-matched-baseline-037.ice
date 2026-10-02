{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-MATCHED-BASELINE-037",
  "question": "At matched 192 persistent bytes, 128 active parameters, resident bytes, and adaptation budgets, how does developmental motif regeneration compare with a fixed task-specific adapter baseline and cold retraining?",
  "hypothesis": "Developmental regeneration reaches specificity >=0.05 with median regeneration cost no more than 10% above the matched fixed-adapter baseline and <=50% of cold retraining cost; if the fixed adapter is materially cheaper at matched resources, classify that as evidence against this mechanism.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": [
    {
      "experiment": "EXP-DG1B-MOTIF-TRANSFER-REUSE-031",
      "result_sha256": "3aeffd127cf7d1567c8f9943b774b95df8873c34a5370823900d1d9e92ddbb85"
    },
    {
      "experiment": "EXP-DG1B-MOTIF-AFFINITY-GRADIENT-034",
      "result_sha256": "46bf651045cae981977f40c555738267c376fad503de7476082818106b3c09cd"
    }
  ],
  "changed_dimension": "recovery mechanism only: developmental reusable motif versus fixed task-specific adapter versus cold; persistent and active resources matched where applicable",
  "seeds": [
    165869,
    166879,
    167887,
    168899,
    169909,
    170927,
    171937,
    172951
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "persistent_bytes": 192,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_updates": 128,
    "cold_updates": 512
  },
  "thresholds": {
    "developmental_specificity_gte": 0.05,
    "developmental_cost_vs_fixed_adapter_ratio_lte": 1.1,
    "developmental_cost_fraction_of_cold_lte": 0.5,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "classification_note": "A fixed-adapter advantage beyond the frozen 10% margin is a valid negative result for the developmental mechanism, not an infrastructure failure.",
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
