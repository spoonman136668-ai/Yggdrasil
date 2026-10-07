{
  "schema": "yggdrasil.consolidation-consumer-key-coupling-diagnosis.v1",
  "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-CONSUMER-KEY-COUPLING-DIAGNOSIS-094",
  "parent_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-COMPONENT-ATTRIBUTION-093",
  "parent_sha": "3bd913bd4057f3780367e3687e1fa83adfc9f46a",
  "hypothesis": "Y093 was a valid negative: target-local best/map_best component overrides did not recover either sealed context, while Y092 already showed that continuous consumer fields are downstream-inert when (key,best,map_best) is fixed. If the remaining failure is caused by consolidation-consumer coupling through retained-key addressing, then substituting one predeclared historical representative key while keeping target best/map_best, retained continuous fields, capacity, and budgets fixed should improve sealed-context behavior without partner collateral failure.",
  "y093_frozen_observation": {
    "classification": "negative",
    "validity_pass": true,
    "best_component_ablation": "retain-map-best",
    "improved_context_count": 0,
    "partner_collateral_failure_count": 0
  },
  "diagnostic_arms": {
    "count": 4,
    "arms": [
      {
        "id": "retrieved-key",
        "key_source": "normal retrieve_full result"
      },
      {
        "id": "transfer-key",
        "key_source": "local_rank-best state from frozen transfer historical pool"
      },
      {
        "id": "third-key",
        "key_source": "local_rank-best state from frozen third historical pool"
      },
      {
        "id": "fourth-key",
        "key_source": "local_rank-best state from frozen fourth historical pool"
      }
    ]
  },
  "fixed_interface": {
    "capacity": "16 total / 7 active / 9 retained",
    "best_map_best": "always target-local and identical across arms",
    "continuous_fields": "always from normally retrieved retained state and identical across arms",
    "only_manipulated_boundary": "retained key addressing source",
    "learned_scalars": 0,
    "persistent_state_growth": false,
    "external_model_calls": 0
  },
  "fit_and_evaluation": {
    "historical_sources": "exact Y093 transfer/third/fourth identities",
    "sealed_unseen": [
      "fifteenth",
      "sixteenth"
    ],
    "arm_set_frozen_before_y094_execution": true,
    "no_heldout_outcome_use_before_arm_freeze": true
  },
  "frozen_evaluation": {
    "supported": "valid; exactly one nonbaseline key-source arm improves both sealed contexts over retrieved-key, loses no clean rescue relative to the Y091 alpha-0.5 reference, has zero partner collateral failure, and exceeds every other nonbaseline arm by at least one improved context",
    "mixed": "valid; support false; best nonbaseline arm improves exactly one sealed context with no lost Y091 clean rescue or partner collateral failure, or multiple nonbaseline arms improve both contexts without a unique winner",
    "negative": "valid and neither supported nor mixed",
    "invalid": "identity/capacity/16-7-9/arm-set/field-isolation/heldout/provenance/determinism/persistence/resource-accounting failure"
  },
  "manifest_sha256": "469a414a41ab93876b14298aa04e09704a2a28eb38742536d709d1c5ad4e0881",
  "governance": {
    "no_post_result_tuning": true,
    "no_capacity_growth": true,
    "sealed_negatives": true,
    "deterministic_replay": true,
    "no_oracle_or_label_leakage": true,
    "no_accepted_ref_mutation": true,
    "no_live_or_production_authority": true,
    "broad_continual_training": false,
    "positive_diagnosis_requires_fresh_replication_before_promotion": true
  }
}
