{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-COALITION-064",
  "program": "Yggdrasil training-only context gate for cumulative collateral memory",
  "question": "Can a deterministic training-only context gate use the single retained row causally identified by 063 to preserve prose collateral across all four transfer schedules without harming already-successful contexts or increasing capacity?",
  "hypothesis": "Replay the exact 062 four schedules, transfer manifest, 60/40 split, rebalanced history, carry6 baseline, twelve-packet future stream, dependent cue, success rule and 16 total / 7 active / 9 retained capacity. Freeze the retained memory key R=[10,32,32,32], identified in 063 because every rescuing variant contained R and every tested variant lacking R failed. For each schedule derive the current historical prose_guard7 using training bytes only. If R is already in prose_guard7, the context gate is a no-op and uses the original guard. If R is absent, require the frozen shared5 from 063, retain the highest-ranked current context-specific guard row by the existing training-only prose contribution ordering, replace the lower-ranked context-specific row with R sourced from the training-only B+C donor state, and inject carry6 ∪ gated_guard into the fixed 16-row transfer state with the byte-identical 062 deterministic eviction rule. No evaluation labels or packet outcomes affect gating. Supported requires exact gate use in the two R-absent schedules and no-op in the two R-present schedules, full success/prose/partner collateral in all four schedules, no schedule slower than baseline, mean packet reduction >=1.0, exact 16/7/9 capacity, and zero invalid rows.",
  "exact_parent_sha": "899d7309453163ef034e914c5121db4531a5ed17",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-indexed-collateral-coalition-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-STATE-COMPATIBILITY-ATTRIBUTION-063",
    "github_run_id": 37162779172,
    "classification": "supported",
    "observation": {
      "original_ac_failure_schedule_count": 2,
      "bc_containing_variant_rescue_both_count": 3,
      "rescuing_variants": [
        0,
        1,
        2
      ],
      "common_rescue_key": [
        10,
        32,
        32,
        32
      ],
      "variants_without_common_rescue_key": [
        3,
        4,
        5
      ],
      "variants_without_common_rescue_key_rescue_count": 0
    },
    "interpretation": "The single retained newline-plus-indentation row R is the common causal discriminator across all rescuing guards; general BC-context membership is insufficient because variants 4 and 5 contain the other BC-specific row but still fail."
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
  "frozen_gate": {
    "retained_memory_key": [
      10,
      32,
      32,
      32
    ],
    "shared5": [
      [
        118,
        101,
        108,
        111
      ],
      [
        101,
        118,
        101,
        108
      ],
      [
        100,
        101,
        118,
        101
      ],
      [
        111,
        112,
        109,
        101
      ],
      [
        32,
        32,
        32,
        32
      ]
    ],
    "absent_rule": "if R absent from training-only prose_guard7: keep shared5 + highest-ranked existing non-shared guard row + R",
    "present_rule": "if R present: use original prose_guard7 unchanged",
    "retained_row_source": "training-only B+C historical donor state",
    "context_specific_rank": "existing historical technical-prose contribution order; no heldout labels",
    "expected_gate_use_schedule_count": 2,
    "expected_gate_noop_schedule_count": 2
  },
  "frozen_reuse": {
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "sources": "byte-identical 062/063 transfer manifest",
    "history_rebalancing": "byte-identical 062",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 062",
    "required_union_injection": "byte-identical 062",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "metrics_and_thresholds": [
    [
      "gate_use_schedule_count",
      "==",
      2
    ],
    [
      "gate_noop_schedule_count",
      "==",
      2
    ],
    [
      "retained_memory_donor_missing_count",
      "==",
      0
    ],
    [
      "candidate_reserved_key_missing_count",
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
      "candidate_schedule_slower_than_baseline_count",
      "==",
      0
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
      "active_structure_count_min",
      "==",
      7
    ],
    [
      "retained_structure_count_min",
      "==",
      9
    ],
    [
      "capacity_growth_event_count",
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
    "supported": "valid and all frozen gate/collateral/no-regression/mean-improvement thresholds pass",
    "mixed": "valid and gate identity/capacity pass with full prose/partner collateral, but packet-efficiency/no-regression thresholds are not all met",
    "negative": "valid but the gated guard fails collateral or exact context behavior",
    "invalid": "any parent, authority, source, retained-row donor identity, gate rule, heldout-selection boundary, deterministic replay, fixed capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter retained key R, shared5, present/absent gate rules, donor source, current-row ranking rule, schedules, sources, packets, baseline, state injection, success rule, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-RETAIN-REVERT-065",
    "intent": "verify deterministic bounded research-state retain/revert and rollback for the context-indexed retained row before any persistence/generalization claim; a later new-manifest test remains required"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-GATE-ATTRIBUTION-065",
    "intent": "attribute the gate failure before changing retained memory or capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-coalition-064.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-coalition-064.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-indexed-collateral-coalition-064.yml"
  ]
}
