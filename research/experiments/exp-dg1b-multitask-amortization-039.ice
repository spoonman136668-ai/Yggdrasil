{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-MULTITASK-AMORTIZATION-039",
  "question": "Across four related capabilities, does a single reusable 192-byte developmental motif amortize persistent capacity enough to offset its slower matched single-task regeneration relative to task-specific fixed adapters?",
  "hypothesis": "Both mechanisms retain >=0.75 of four capabilities; developmental median regeneration cost is <=1.50x fixed-adapter cost while developmental persistent bytes remain 192 versus 768 for four 192-byte task-specific adapters, yielding >=3x retained-capability-per-persistent-byte efficiency.",
  "exact_parent_sha": "104963c7522ad22d6e5cacdc5814cbef581b5320",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": [
    {
      "experiment": "EXP-DG1B-CAPABILITY-SEQUENCE-SCALING-036",
      "result_sha256": "7f0db8f14d7a334cd062bdf4afa9628ae0bc8df32a9cd9a8978f53837928f85e"
    },
    {
      "experiment": "EXP-DG1B-MATCHED-BASELINE-037",
      "result_sha256": "3d8818133adabd3dabcd4069872157309d0612615c04a5f6a0a553848d7547c3",
      "finding": "developmental/fixed regeneration cost ratio 1.4167 on one task"
    }
  ],
  "changed_dimension": "retained capability count only: four related tasks compared across one shared developmental motif versus four task-specific fixed adapters",
  "seeds": [
    182069,
    183089,
    184111,
    185117,
    186131,
    187139,
    188147,
    189151
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "developmental_persistent_bytes": 192,
    "fixed_adapter_bytes_per_task": 192,
    "task_count": 4,
    "max_updates": 128,
    "cold_updates": 512,
    "resident_byte_count": 1344
  },
  "thresholds": {
    "developmental_retained_capability_fraction_gte": 0.75,
    "fixed_retained_capability_fraction_gte": 0.75,
    "developmental_cost_vs_fixed_ratio_lte": 1.5,
    "capability_per_persistent_byte_efficiency_ratio_gte": 3,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
