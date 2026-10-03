{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-STATE-COMPATIBILITY-062",
  "program": "Yggdrasil bounded transfer-state compatibility for frozen k=7 collateral coalition",
  "question": "If the transfer state is reconstructed so the frozen historical k=7 prose coalition actually exists before active selection, does the 059 mechanism become valid and recover its packet-efficiency/collateral advantage on the disjoint 060 dataset without increasing capacity or using heldout selection?",
  "hypothesis": "Replay the exact 060 transfer manifest, schedules, 60/40 split, rebalanced history, twelve-packet future stream, dependent cue, success rule, and 16 total / 7 active / 9 retained capacity. Keep the 060 carry6 baseline byte-identical. For the candidate only, before selecting the frozen prose_guard7 active set, inject the training-only required union carry6 ∪ prose_guard7 from the historical 16-row state into the current 16-row transfer state using the existing deterministic inject eviction rule, never exceeding 16 rows. Then select exactly prose_guard7 as the seven active rows. No heldout labels or results influence required keys or eviction ordering. Supported requires zero missing candidate reservation keys, exact 16/7/9 capacity, positive prose collateral in all four schedules, zero partner collateral failures, packet-to-success improvement in at least three schedules, and mean packet reduction >=1 versus the unchanged baseline.",
  "exact_parent_sha": "ded5b15706a42bbbe9153842f6f2f259c9d20f45",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-collateral-coalition-state-compatibility-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-TRANSFER-VALIDITY-ATTRIBUTION-061",
    "github_run_id": 37162044836,
    "classification": "supported",
    "observation": {
      "original_invalid_evaluation_rows": 26,
      "candidate_reserved_key_missing_count": 26,
      "candidate_reserved_key_missing_select_count": 26,
      "all_other_invalid_source_count": 0
    },
    "interpretation": "060 failed validity solely because frozen coalition keys were absent after transfer-state reconstruction; selection filled those holes, so the tested candidate was not exact k=7."
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
    "sources": "byte-identical 060/061 disjoint manifest",
    "affected_schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "history_rebalancing": "byte-identical 060",
    "future_packets": 12,
    "carry6_injection": "byte-identical baseline",
    "dependent_cue": "byte-identical 060",
    "baseline": "byte-identical 060 carry6 state + carry6 active selection",
    "candidate_k": 7,
    "candidate_required_state_keys": "deterministic union of frozen carry6 and prose_guard7; training-only",
    "candidate_active": "exact frozen prose_guard7",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "metrics_and_thresholds": [
    [
      "source_identity_mismatch_count",
      "==",
      0
    ],
    [
      "transfer_manifest_identity_mismatch_count",
      "==",
      0
    ],
    [
      "candidate_reserved_key_missing_count",
      "==",
      0
    ],
    [
      "candidate_required_union_over_capacity_count",
      "==",
      0
    ],
    [
      "candidate_state_capacity_failure_count",
      "==",
      0
    ],
    [
      "candidate_positive_prose_collateral_schedule_count",
      "==",
      4
    ],
    [
      "candidate_partner_collateral_failure_count",
      "==",
      0
    ],
    [
      "candidate_positive_reduction_schedule_count",
      ">=",
      3
    ],
    [
      "candidate_mean_packet_reduction",
      ">=",
      1
    ],
    [
      "preserved_state_structure_count_min",
      "==",
      16
    ],
    [
      "preserved_state_structure_count_max",
      "==",
      16
    ],
    [
      "active_structure_count_min",
      "==",
      7
    ],
    [
      "active_structure_count_max",
      "==",
      7
    ],
    [
      "retained_structure_count_min",
      "==",
      9
    ],
    [
      "retained_structure_count_max",
      "==",
      9
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "tokenizer_use_count",
      "==",
      0
    ],
    [
      "external_model_call_count",
      "==",
      0
    ],
    [
      "invalid_evaluation_rows",
      "==",
      0
    ]
  ],
  "classification_rules": {
    "supported": "valid; exact candidate coalition identity is preserved and all preregistered collateral plus packet-efficiency thresholds pass",
    "mixed": "valid; exact candidate coalition identity is preserved with full prose/partner collateral, but one or both packet-efficiency thresholds fail",
    "negative": "valid but exact coalition identity cannot be preserved within fixed state capacity or collateral fails",
    "invalid": "any parent, authority, transfer-source, deterministic state injection, heldout-selection boundary, capacity, provenance, or accounting criterion fails"
  },
  "no_post_result_tuning_rule": "Do not alter transfer data, schedules, split, history, packets, carry6 baseline, prose_guard7 identity, required-union construction, deterministic eviction rule, success rule, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-RETAIN-REVERT-063",
    "intent": "test bounded research-state retain/revert and rollback of the transfer-supported compatibility mechanism before any persistence claim"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-STATE-COMPATIBILITY-ATTRIBUTION-063",
    "intent": "attribute remaining performance or collateral loss before modifying the compatibility mechanism"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-state-compatibility-062.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-state-compatibility-062.py",
    ".github/workflows/external-cumulative-dependent-pipeline-collateral-coalition-state-compatibility-062.yml"
  ]
}
