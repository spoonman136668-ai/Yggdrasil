{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-PERSISTENT-STATE-GEOMETRY-030",
  "question": "At the supported 192-byte persistent-state budget, does distributing retained motif values across all five source cells preserve regeneration relative to a contiguous three-cell 192-byte motif?",
  "hypothesis": "The distributed 192-byte motif retains cycle-four specificity >=0.05, attenuation versus contiguous 192 bytes <=0.02, support fraction >=0.75, and unrelated collateral <=0.03.",
  "exact_parent_sha": "7f05b892f9448891d929339dbddb357b025f98dd",
  "north_star_sha256": "3cd3b3d2fdbbb5b3541d433a527231b38fc441699cd0353fa86f0c3be6f0a905",
  "prior_evidence": {
    "experiment": "EXP-DG1B-PERSISTENT-STATE-MINIMUM-026",
    "result_sha256": "59efb788f4180d6ded965e904d4c174ef31141c0ccb65663caa4bd0e00999eec",
    "classification": "supported"
  },
  "changed_dimension": "selection geometry only at exactly 24 float64 values / 192 informative bytes",
  "conditions": {
    "contiguous192_indices": "0..23",
    "distributed192_indices": [
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      10,
      12,
      14,
      16,
      18,
      20,
      22,
      24,
      26,
      28,
      30,
      32,
      34,
      36,
      38
    ]
  },
  "seeds": [
    121021,
    122027,
    123037,
    124067,
    125069,
    126079,
    127081,
    128093
  ],
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 192,
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
    "median_distributed_cycle4_specificity_gte": 0.05,
    "median_contiguous_minus_distributed_attenuation_lte": 0.02,
    "supporting_seed_fraction_gte": 0.75,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
