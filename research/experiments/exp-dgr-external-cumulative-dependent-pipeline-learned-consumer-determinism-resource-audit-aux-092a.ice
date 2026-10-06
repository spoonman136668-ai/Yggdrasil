{
  "schema": "yggdrasil.auxiliary-evidence-only.v1",
  "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-DETERMINISM-RESOURCE-AUDIT-AUX-092A",
  "parent_experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-ARCHITECTURE-092",
  "parent_sha": "d2da0d5b871cbe910e0e20cbf1b8a487ac821e22",
  "hypothesis": "An independent evidence-only replay of the exact frozen Y092 learned-consumer package on the dedicated auxiliary runner will reproduce the deterministic scientific result bit-for-bit while preserving the declared 16 total / 7 active / 9 retained algorithmic resource envelope.",
  "role": "auxiliary evidence only; no primary successor authority; no primary state mutation; no shared scientific state",
  "runner_label": "research-only",
  "data": {
    "mode": "reuse exact authorized Y092 manifest; no new data",
    "manifest_sha256": "ea4dfd21ac7d2b6bc98e8e26c45bfef768a0bf9ea6d2a3502ab67469df346cf3",
    "unseen_contexts": [
      "fifteenth",
      "sixteenth"
    ],
    "no_additional_fetch_scope": true
  },
  "frozen_mechanism": {
    "interface": "cognition_consumer(retained_state, local_state) -> decision_state",
    "candidate_count": 4,
    "alpha_grid": [
      0,
      0.25,
      0.5,
      0.75,
      1
    ],
    "historical_selection_data": "exact Y091 historical transfer/third/fourth contexts",
    "candidate_frozen_before_unseen_outcomes": true,
    "primary_result_use_forbidden": true
  },
  "resource_envelope": {
    "capacity": "16 total / 7 active / 9 retained",
    "baseline_effective_consumer_scalars": 1,
    "max_candidate_learned_scalars": 4,
    "external_model_calls": 0,
    "hidden_memory_growth": false,
    "persistent_state_growth": false,
    "gpu_required": false,
    "broad_continual_training": false,
    "no_capacity_or_compute_class_growth": true
  },
  "evaluation": {
    "executions": 2,
    "result_json_must_be_bit_identical": true,
    "algorithmic_resource_envelope_must_match": true,
    "process_resource_telemetry": "record only; no post-result threshold tuning",
    "supported": "valid; both independent executions are bit-identical and all frozen algorithmic resource/capacity/data/provenance checks pass",
    "mixed": "not used",
    "negative": "not used",
    "invalid": "any identity, authority, data, capacity, deterministic-result, provenance, hidden-state, persistent-state, external-model-call, or resource-accounting invariant fails"
  },
  "governance": {
    "preregistered_before_execution": true,
    "primary_successor_authority": false,
    "primary_state_mutation": false,
    "shares_scientific_state": false,
    "no_post_result_tuning": true,
    "no_oracle_or_label_leakage": true,
    "no_accepted_ref_mutation": true,
    "no_live_or_production_authority": true
  }
}
