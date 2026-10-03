{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-TRANSFER-VALIDITY-ATTRIBUTION-061",
  "program": "Yggdrasil transfer-validity attribution for frozen k=7 collateral coalition",
  "question": "Which exact invariant produced the 26 invalid_evaluation_rows in transfer experiment 060, without changing any 060 state construction, selection, scoring, threshold, capacity, or scientific behavior?",
  "hypothesis": "Replay 060 byte-identically and add accounting-only counters at every existing invalid_evaluation_rows increment site. The preregistered primary attribution is that all 26 invalid counts arise because one or more frozen historical technical-prose coalition keys are absent from the reconstructed 16-row transfer state when candidate select(..., reserved=prose_guard) executes; the selector then fills the missing reservation slots from the current ranking, preserving active_count=7 but violating exact frozen-coalition identity. Supported requires candidate_reserved_key_missing_count=26, original_invalid_evaluation_rows=26, and every other diagnostic invalid-source counter=0. No result from 061 may retroactively change 060's invalid classification.",
  "exact_parent_sha": "bf45fc1475b998555a20501199cd4e2426afe211",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-collateral-coalition-transfer-validity-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-TRANSFER-060",
    "github_run_id": 37161706893,
    "classification": "invalid",
    "validity_pass": false,
    "sealed_observation": {
      "invalid_evaluation_rows": 26,
      "source_identity_mismatch_count": 0,
      "transfer_manifest_identity_mismatch_count": 0,
      "base_training_identity_mismatch_count": 0,
      "matched_assignment_failure_count": 0,
      "candidate_positive_prose_collateral_schedule_count": 4,
      "candidate_partner_collateral_failure_count": 0,
      "preserved_state_structure_count_min": 16,
      "active_structure_count_min": 7,
      "retained_structure_count_min": 9
    }
  },
  "external_transfer_manifest_sha256": "c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250",
  "external_authority": {
    "ckb_plane_main_sha": "06c3cb723820407bc2db1bd3ec9e46f462059e41",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "implementation_behavior": "byte-identical 060 except additive diagnostic counters",
    "sources": "byte-identical 060 transfer manifest and effective prefixes",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "packet_budget": 12,
    "candidate_k": 7,
    "capacity": "16 total / 7 active / 9 retained",
    "selection_and_scoring": "byte-identical 060",
    "original_invalid_metric": "retained unchanged"
  },
  "diagnostic_counters": [
    "candidate_reserved_key_missing_count",
    "candidate_reserved_key_missing_select_count",
    "inject_missing_carry_key_count",
    "inject_capacity_failure_count",
    "build_structure_failure_count",
    "partition_failure_count",
    "oversized_reserved_set_count",
    "active_selection_failure_count",
    "history_budget_failure_count",
    "empty_derived_count",
    "short_history_rank_count",
    "short_prose_rank_count",
    "empty_future_count",
    "empty_packet_count",
    "schedule_count_failure_count",
    "other_low_level_invalid_count"
  ],
  "classification_rules": {
    "supported": "replay is deterministic; original_invalid_evaluation_rows==26; candidate_reserved_key_missing_count==26; candidate_reserved_key_missing_select_count>0; every other diagnostic invalid-source counter==0",
    "mixed": "replay is deterministic; candidate_reserved_key_missing_count>0 but at least one other diagnostic source also contributes",
    "negative": "replay is deterministic; candidate_reserved_key_missing_count==0 and the 26 invalid rows are fully attributed to another diagnostic source",
    "invalid": "replay differs from 060 behavior/output identities, source/authority identities fail, diagnostic accounting does not sum to original invalid count, or any behavior-changing delta is detected"
  },
  "no_post_result_tuning_rule": "Do not change 060 data, state construction, schedules, packet count, carry injection, k=7 coalition, selection, scoring, capacity, original invalid metric, thresholds, authority, or classification. Only additive diagnostics are permitted.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-STATE-COMPATIBILITY-062",
    "intent": "test a preregistered bounded mechanism that preserves exact coalition identity across transfer-state reconstruction without capacity growth or heldout-driven selection"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-VALIDITY-ATTRIBUTION-062",
    "intent": "isolate the remaining validity source before modifying the coalition mechanism"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-transfer-validity-attribution-061.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-transfer-validity-attribution-061.py",
    ".github/workflows/external-cumulative-dependent-pipeline-collateral-coalition-transfer-validity-attribution-061.yml"
  ]
}
