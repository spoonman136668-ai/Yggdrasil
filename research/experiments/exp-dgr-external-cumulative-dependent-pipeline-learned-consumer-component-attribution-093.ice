{
  "schema": "yggdrasil.rsi-consumer-component-attribution.v1",
  "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-COMPONENT-ATTRIBUTION-093",
  "parent_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-ARCHITECTURE-092",
  "parent_sha": "dded982e3fc9d3bb147af3b7577915e1fd72db3d",
  "hypothesis": "Y092 was a valid negative with the resource-eligible shared-alpha candidate frozen at alpha=0.0. Because the downstream active map is sensitive to discrete best/map_best state rather than the learned continuous fields, a fixed component ablation can determine whether forcing either target-local discrete field suppresses rescue while preserving memory addressing and 16 total / 7 active / 9 retained.",
  "y092_frozen_observation": {
    "classification": "negative",
    "validity_pass": true,
    "selected_candidate": "shared-alpha",
    "selected_params": [
      0
    ],
    "selected_effective_consumer_scalars": 1,
    "selected_resource_eligible": true,
    "continuous_fields": [
      "total",
      "best_count",
      "consistency",
      "utility"
    ]
  },
  "fixed_interface": {
    "signature": "cognition_consumer(retained_state, local_state) -> decision_state",
    "capacity": "16 total / 7 active / 9 retained",
    "key_addressing": "unchanged retained key and retrieval path for every arm",
    "continuous_fields": "exact retained values in every attribution arm; no learned scalar search",
    "persistent_write": false
  },
  "attribution_arms": {
    "count": 4,
    "baseline": "y092-selected",
    "arms": [
      {
        "id": "y092-selected",
        "best": "target",
        "map_best": "target",
        "change": "none"
      },
      {
        "id": "retain-best",
        "best": "retained",
        "map_best": "target",
        "change": "remove target override for best only"
      },
      {
        "id": "retain-map-best",
        "best": "target",
        "map_best": "retained",
        "change": "remove target override for map_best only"
      },
      {
        "id": "retain-both",
        "best": "retained",
        "map_best": "retained",
        "change": "remove both target-local discrete overrides"
      }
    ],
    "nonclassifying_reference": {
      "id": "y091-alpha-0.5",
      "description": "frozen Y091 hand-designed consumer comparator"
    }
  },
  "fit_and_evaluation": {
    "historical_contexts": [
      "transfer",
      "third",
      "fourth"
    ],
    "candidate_learning": "none; all four component arms are fixed before Y093 execution",
    "sealed_attribution_contexts": [
      "fifteenth",
      "sixteenth"
    ],
    "attribution_context_reuse": "exact Y092 sealed contexts reused only to explain the already-observed Y092 negative; no fresh generalization claim",
    "no_heldout_outcome_use_in_arm_definition": true
  },
  "resource_envelope": {
    "capacity": "16 total / 7 active / 9 retained",
    "attribution_arm_count": 4,
    "learned_scalars": 0,
    "external_model_calls": 0,
    "hidden_memory_growth": false,
    "persistent_state_growth": false,
    "gpu_required": false,
    "no_material_ram_vram_model_context_agent_compute_growth": true
  },
  "frozen_evaluation": {
    "supported": "valid; exactly one component ablation improves over y092-selected on both attribution contexts, has no lost clean rescue relative to y091-alpha-0.5, no partner collateral failure, and exceeds the second-best ablation by at least one improved context",
    "mixed": "valid; support false; best component ablation improves exactly one attribution context with no lost clean rescue or partner collateral, or multiple component ablations improve both contexts without a unique winner",
    "negative": "valid and neither supported nor mixed",
    "invalid": "identity/capacity/16-7-9/addressing/arm-set/heldout/provenance/determinism/persistence/resource-accounting failure"
  },
  "manifest_sha256": "a9d3cb36d94aa38188a18c96ff16d03116b8db99abceb2c48fe060e5ee90c2be",
  "governance": {
    "no_post_result_tuning": true,
    "no_hidden_memory_or_capacity_growth": true,
    "deterministic_replay": true,
    "no_oracle_or_label_leakage": true,
    "no_accepted_ref_mutation": true,
    "no_live_or_production_authority": true,
    "broad_continual_training": false,
    "positive_attribution_requires_fresh_replication_before_promotion": true
  },
  "successor_policy": {
    "supported": "fresh disjoint discrete-consumer replication required",
    "mixed": "bounded discrete-component interaction attribution required",
    "negative": "return to consolidation/consumer coupling diagnosis without changing 16/7/9"
  }
}
