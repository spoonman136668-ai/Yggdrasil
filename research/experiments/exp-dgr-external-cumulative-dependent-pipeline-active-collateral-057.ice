{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-057",
  "program": "Yggdrasil fixed-budget collateral-aware active selection",
  "question": "Can a frozen training-only collateral-aware active selector preserve the repaired technical-prose capability and reduce future packets-to-success without changing historical bytes, carry width, total capacity, compute budget, or authority?",
  "hypothesis": "Replay the exact four affected 055 schedules, rebalanced historical bytes, carry6 construction/injection, twelve future-C packets, dependent task, and 16 total / 7 active / 9 retained capacity. Compare unchanged 055 reserved-carry6 active selection against one frozen collateral-aware selector. The candidate selector reserves the two highest technical-prose historical-contribution rows from the rebalanced A+B state, then fills the remaining five active slots by the unchanged current dependent-cue ranking without duplicates. It does not use heldout scores, future outcomes, or target labels for selection. Supported requires positive technical-prose collateral on at least three of four affected schedules at the first successful packet, at least 1.0 mean packet reduction versus unchanged 055, improvement on at least three of four schedules, and no partner-collateral failures. This is a candidate mechanism test only; no mechanism is retained without a later preregistered disjoint transfer replication.",
  "exact_parent_sha": "07a3c113f9737e4c8b5fac84e932e416124a469c",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-active-collateral-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; future-data learning efficiency is primary; candidate selector is not retained here"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-ATTRIBUTION-056",
    "github_run_id": "37143690458",
    "classification": "supported",
    "observation": {
      "historical_positive_count": 4,
      "row_not_carried_count": 0,
      "injection_loss_count": 0,
      "reservation_selection_loss_count": 0,
      "active_score_loss_count": 4,
      "preserved_but_dependent_failure_count": 0
    },
    "diagnosis": "Rebalanced technical-prose support is positive historically and survives carry/injection; all four failures arise only because the final seven-active dependent partition drives technical-prose collateral from +1 to 0."
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_design": {
    "affected_schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "historical_bytes": "byte-identical rebalanced 055",
    "future_c_packets": "byte-identical twelve-packet 055 stream",
    "baseline_selector": "byte-identical 055 carry6 reserved selection",
    "candidate_selector": "reserve top two rows by technical-prose historical cue contribution from rebalanced A+B state, tie higher utility then key; fill remaining five by current dependent-cue contribution, tie higher utility then key",
    "candidate_selection_inputs": "training/history cues and current future-C prefix only; no heldout labels/scores/outcomes",
    "carry_injection": "byte-identical 055 carry6 state injection before active selection",
    "dependent_eval": "byte-identical 055",
    "success_rule": "dependent score >0 and both historical collateral scores >0",
    "capacity": "16 total / 7 active / 9 retained",
    "retention": false
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
      "affected_schedule_count",
      "==",
      4
    ],
    [
      "packet_budget_per_schedule",
      "==",
      12
    ],
    [
      "history_byte_budget_mismatch_count",
      "==",
      0
    ],
    [
      "candidate_selection_heldout_use_count",
      "==",
      0
    ],
    [
      "candidate_positive_prose_collateral_schedule_count",
      ">=",
      3
    ],
    [
      "candidate_mean_packet_reduction",
      ">=",
      1
    ],
    [
      "candidate_positive_reduction_schedule_count",
      ">=",
      3
    ],
    [
      "candidate_partner_collateral_failure_count",
      "==",
      0
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
      "row_mutation_event_count",
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
    "supported": "Validity passes; candidate selector preserves positive technical-prose collateral in at least three affected schedules, reduces mean packets-to-success by at least 1.0 versus unchanged 055, improves at least three schedules, and causes zero partner-collateral failures.",
    "mixed": "Validity passes and candidate improves either collateral or packet efficiency but not all supported thresholds.",
    "negative": "Validity passes but candidate does not improve collateral or learning efficiency versus unchanged 055.",
    "invalid": "Any parent, authority, source, byte-budget identity, carry/injection identity, selector identity, heldout isolation, capacity, determinism, or provenance criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter sources, rebalanced historical bytes, future packets, carry6/injection, two-row collateral reservation rule, dependent ranking, success rule, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-TRANSFER-058",
    "intent": "replicate the candidate on a preregistered disjoint future split/task under the same budgets before any retention"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-ATTRIBUTION-058",
    "intent": "attribute whether two-row collateral reservation is insufficient or conflicts with dependent/partner support before changing the candidate set"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-active-collateral-057.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-active-collateral-057.py",
    ".github/workflows/external-cumulative-dependent-pipeline-active-collateral-057.yml"
  ]
}
