{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-SHARED-MOTIF-REUSE-031",
  "question": "Can one fixed 192-byte persistent motif regenerate useful function for two distinct related tasks after total lesion without increasing persistent or active capacity?",
  "hypothesis": "The same 192-byte motif yields cycle-four specificity >=0.04 on both related tasks, both-task supporting-seed fraction >=0.75, unrelated collateral <=0.03, and persistent bytes per demonstrated related task <=96.",
  "exact_parent_sha": "7f05b892f9448891d929339dbddb357b025f98dd",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-026",
    "result_sha256": "59efb788f4180d6ded965e904d4c174ef31141c0ccb65663caa4bd0e00999eec",
    "classification": "supported"
  },
  "changed_dimension": "number of related capabilities demonstrated from the same fixed 192-byte persistent motif: one versus two; no persistent or active capacity growth",
  "tasks": {
    "source": "x0+x1+x2+x3 >= 0",
    "related_a": "x0+x1+x2+x4 >= 0",
    "related_b": "x0+x1+x3+x4 >= 0",
    "unrelated": "x8+x9+x10+x11 >= 0"
  },
  "seeds": [
    131009,
    132017,
    133033,
    134039,
    135053,
    136063,
    137081,
    138091
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 192,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "cycles": [
      1,
      2,
      3,
      4
    ],
    "updates_per_cycle": 128
  },
  "thresholds": {
    "median_task_a_cycle4_specificity_gte": 0.04,
    "median_task_b_cycle4_specificity_gte": 0.04,
    "both_task_supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03,
    "persistent_bytes_per_demonstrated_related_task_lte": 96
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
