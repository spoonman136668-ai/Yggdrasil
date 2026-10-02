{
  "schema": "yggdrasil.research-preregistration.v1",
  "status": "frozen-prereg-only",
  "experiment_id": "EXP-DG1B-CAPABILITY-SEQUENCE-SCALING-036",
  "question": "Can one fixed 192-byte reusable developmental motif retain regenerability across a sequence of 1, 2, and 4 related task phenotypes without increasing active parameters or persistent motif bytes per added task?",
  "hypothesis": "At four tasks, retained-capability fraction is >=0.75, median regeneration-cost fraction versus cold is <=0.50, active parameters remain fixed at 128, persistent motif bytes remain 192, and unrelated collateral remains <=0.03.",
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
  "changed_dimension": "number of related capabilities in the learned sequence only: 1 versus 2 versus 4; one shared 192-byte motif and active resources fixed",
  "seeds": [
    157799,
    158807,
    159811,
    160817,
    161831,
    162841,
    163847,
    164861
  ],
  "task_family": {
    "source_features": [
      0,
      1,
      2,
      3
    ],
    "related_variants": [
      [
        0,
        1,
        2,
        4
      ],
      [
        0,
        1,
        3,
        5
      ],
      [
        0,
        2,
        3,
        6
      ],
      [
        1,
        2,
        3,
        7
      ]
    ],
    "task_identity_context": "benchmark-provided task identifier only; no learned task-specific persistent state"
  },
  "budgets": {
    "timeout_seconds": 1800,
    "active_parameter_count": 128,
    "informative_persistent_bytes": 192,
    "transfer_container_bytes": 320,
    "resident_byte_count": 1344,
    "max_regeneration_updates": 128,
    "cold_updates": 512
  },
  "thresholds": {
    "four_task_retained_capability_fraction_gte": 0.75,
    "four_task_median_regeneration_cost_fraction_of_cold_lte": 0.5,
    "max_active_parameter_growth": 0,
    "max_persistent_motif_byte_growth": 0,
    "max_abs_unrelated_collateral_lte": 0.03
  },
  "authority": "synthetic computational research only; research-only",
  "no_post_result_tuning": true
}
