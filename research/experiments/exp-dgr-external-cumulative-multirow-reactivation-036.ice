{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-REACTIVATION-036",
  "program": "Yggdrasil fixed-capacity simultaneous dormant-capability preservation followed by explicit reactivation",
  "question": "After preserving two dormant capabilities across the full twelve-packet non-target horizon, can each preserved target be explicitly reactivated into the seven-active set without losing the other preserved target or damaging the non-target capability?",
  "hypothesis": "Reuse the exact supported 035 mechanism for all six schedules and all three target pairs through packet 12. Then apply each target's frozen maturity cue as an explicit reactivation cue, one target at a time in both target orders. Every reactivated target will remain positively above baseline, the still-dormant protected target will remain positively recoverable after the first reactivation, the second reactivation will also remain positive, and non-target heldout benefit will remain safe under the unchanged 16 total / 7 active / 9 retained capacity.",
  "exact_parent_sha": "a557aecdcdda62622a3c44b41353dabeee6d00a7",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-multirow-reactivation-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-HORIZON-035",
    "github_run_id": "37122307659",
    "classification": "supported",
    "observation": {
      "competition_epoch_case_count": 216,
      "target_reactivation_evaluation_count": 432,
      "positive_target_reactivation_evaluation_count": 432,
      "final_epoch_positive_target_evaluation_count": 36,
      "minimum_target_preserved_incremental_correct_count": 1,
      "zero_baseline_non_target_case_count": 60,
      "ratio_applicable_non_target_case_count": 156,
      "zero_baseline_preserved_negative_count": 0,
      "minimum_applicable_non_target_preserved_to_unprotected_fraction": 1
    },
    "diagnosis": "Two-target dormant preservation remains stable across every cumulative packet through the full horizon; the next bounded developmental question is whether preserved targets can move back into active use without erasing the other dormant target or the active non-target capability."
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "persistent_corpus": false,
    "external_model_calls": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "sources": "byte-identical 035 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [
      [
        "A",
        "B"
      ],
      [
        "A",
        "C"
      ],
      [
        "B",
        "C"
      ]
    ],
    "cumulative_horizon": "packet 12 state from the byte-identical 035 mechanism",
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "protected_row_rule": "byte-identical 035 per-target rule",
    "protected_key_deduplication": "byte-identical 035",
    "eviction_ranking": "byte-identical 035 non-target cue contribution, lower utility, lexicographically larger key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "zero_baseline_contract": "byte-identical 035 ratio-domain and safety semantics",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "reactivation_protocol": {
    "base_state": "preserved packet-12 state for each schedule-target-pair case",
    "target_orders": "both permutations of each two-target pair",
    "reactivation_steps": 2,
    "reactivation_cue": "frozen target maturity cue",
    "active_selection": "recompute the same seven-active selector from the current preserved state under the current target cue",
    "dormant_recovery_check": "after first target activation, score the other target with its frozen maturity cue without mutating rows",
    "non_target_safety_check": "score the non-target heldout evaluation after each target reactivation",
    "row_learning_during_reactivation": false,
    "heldout_updates": false
  },
  "metrics_and_thresholds": [
    [
      "source_identity_mismatch_count",
      "==",
      0
    ],
    [
      "source_count",
      "==",
      3
    ],
    [
      "total_source_bytes",
      "==",
      57272
    ],
    [
      "base_training_identity_mismatch_count",
      "==",
      0
    ],
    [
      "schedule_count",
      "==",
      6
    ],
    [
      "target_pair_count",
      "==",
      3
    ],
    [
      "reactivation_order_count_per_pair",
      "==",
      2
    ],
    [
      "reactivation_case_count",
      "==",
      36
    ],
    [
      "first_target_positive_reactivation_count",
      "==",
      36
    ],
    [
      "dormant_partner_positive_recovery_count",
      "==",
      36
    ],
    [
      "second_target_positive_reactivation_count",
      "==",
      36
    ],
    [
      "minimum_first_target_incremental_correct_count",
      ">=",
      1
    ],
    [
      "minimum_dormant_partner_incremental_correct_count",
      ">=",
      1
    ],
    [
      "minimum_second_target_incremental_correct_count",
      ">=",
      1
    ],
    [
      "zero_baseline_non_target_case_count_plus_ratio_applicable",
      "==",
      72
    ],
    [
      "zero_baseline_preserved_negative_count",
      "==",
      0
    ],
    [
      "minimum_applicable_non_target_preserved_to_unprotected_fraction",
      ">=",
      0.95
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
      "target_interference_leakage_count",
      "==",
      0
    ],
    [
      "heldout_selection_use_count",
      "==",
      0
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
    "supported": "Validity passes, all 36 first-target activations, all 36 dormant-partner recovery checks, and all 36 second-target activations remain positive; zero-baseline safety remains nonnegative and all ratio-applicable non-target retention ratios are at least 0.95.",
    "mixed": "Validity passes and every second target can ultimately reactivate, but a first-target, dormant-partner, or non-target safety threshold fails.",
    "negative": "Validity passes but at least one second-target reactivation is nonpositive.",
    "invalid": "Any sealed-parent, authority, source, reactivation-order accounting, row-preservation, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed 035 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The packet-12 preserved state is produced by the byte-identical supported 035 mechanism before any reactivation scoring.",
    "Reactivation changes active selection only; no rows, utilities, protected keys, thresholds, or learned structures are updated.",
    "Both target orders are evaluated independently from the same frozen packet-12 preserved state.",
    "Heldout evaluations affect scoring/classification only and never row selection, target order, active selection, thresholds, or stopping.",
    "Every state remains exactly sixteen structures / seven active / nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, packet-12 state construction, maturity cues, protected-row rule, eviction ranking, target orders, active selector, zero-baseline semantics, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-REACTIVATION-REUSE-037",
    "intent": "test repeated dormant-active-dormant reuse cycles under the same fixed-capacity preservation mechanism"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-REACTIVATION-ATTRIBUTION-037",
    "intent": "attribute the first target order/state transition that breaks partner persistence or non-target safety before changing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-multirow-reactivation-036.ice",
    "research/applications/plane/exp-dgr-external-cumulative-multirow-reactivation-036.py",
    ".github/workflows/external-cumulative-multirow-reactivation-036.yml"
  ]
}
