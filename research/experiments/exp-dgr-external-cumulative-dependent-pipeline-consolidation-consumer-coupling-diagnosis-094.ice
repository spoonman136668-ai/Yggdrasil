{
  "schema": "yggdrasil.rsi-consolidation-consumer-coupling-diagnosis.v1",
  "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-CONSUMER-COUPLING-DIAGNOSIS-094",
  "parent_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-COMPONENT-ATTRIBUTION-093",
  "parent_sha": "3bd913bd4057f3780367e3687e1fa83adfc9f46a",
  "hypothesis": "Y093 was a valid negative: best/map_best component ablations were behaviorally inert on both diagnostic contexts. The remaining failure may lie in coupling between retrieved consolidated payload and target-local continuous payload. A fixed four-arm coupling decomposition can localize that boundary without changing addressing or 16 total / 7 active / 9 retained capacity.",
  "y093_frozen_observation": {
    "classification": "negative",
    "validity_pass": true,
    "best_component_ablation": "retain-map-best",
    "all_component_improved_context_counts": 0,
    "addressing_change_count": 0,
    "capacity_growth_event_count": 0
  },
  "fixed_interface": {
    "signature": "cognition_consumer(retained_state, local_state) -> decision_state",
    "capacity": "16 total / 7 active / 9 retained",
    "key_addressing": "unchanged retained key/retrieval path in every arm",
    "persistent_write": false
  },
  "coupling_arms": {
    "count": 4,
    "arms": [
      {
        "id": "retained-continuous_target-discrete",
        "continuous": "retained",
        "best_map_best": "target",
        "description": "Y092/Y093 baseline coupling"
      },
      {
        "id": "target-continuous_target-discrete",
        "continuous": "target",
        "best_map_best": "target",
        "description": "local payload with retained addressing"
      },
      {
        "id": "target-continuous_retained-discrete",
        "continuous": "target",
        "best_map_best": "retained",
        "description": "local continuous payload with retained discrete selectors"
      },
      {
        "id": "retained-continuous_retained-discrete",
        "continuous": "retained",
        "best_map_best": "retained",
        "description": "fully retained payload under unchanged addressing"
      }
    ]
  },
  "fit_and_evaluation": {
    "candidate_learning": "none; all four coupling arms frozen before execution",
    "sealed_diagnostic_contexts": [
      "fifteenth",
      "sixteenth"
    ],
    "context_reuse": "exact Y093 sealed contexts reused only to diagnose the Y093 negative; no generalization claim",
    "no_heldout_outcome_use_in_arm_definition": true
  },
  "resource_envelope": {
    "capacity": "16 total / 7 active / 9 retained",
    "coupling_arm_count": 4,
    "learned_scalars": 0,
    "external_model_calls": 0,
    "hidden_memory_growth": false,
    "persistent_state_growth": false,
    "gpu_required": false
  },
  "frozen_evaluation": {
    "supported": "valid; exactly one nonbaseline coupling arm improves both contexts with no lost Y091 clean rescue and no partner collateral failure",
    "mixed": "valid; support false; at least one nonbaseline arm improves exactly one context without collateral, or multiple nonbaseline arms improve both contexts",
    "negative": "valid and neither supported nor mixed",
    "invalid": "identity/capacity/16-7-9/addressing/arm-set/heldout/provenance/determinism/persistence/resource-accounting failure"
  },
  "manifest_sha256": "c2a8fa4e55290dc8f386b5168e171b09a8db9bda89a748cfa6532ee86fb38421",
  "governance": {
    "no_post_result_tuning": true,
    "no_hidden_memory_or_capacity_growth": true,
    "deterministic_replay": true,
    "no_oracle_or_label_leakage": true,
    "no_accepted_ref_mutation": true,
    "no_live_or_production_authority": true,
    "broad_continual_training": false
  },
  "successor_policy": {
    "supported": "fresh disjoint coupling replication required before any promotion",
    "mixed": "bounded coupling interaction attribution required",
    "negative": "return to consolidation representation/retrieval diagnosis while preserving 16/7/9"
  }
}
