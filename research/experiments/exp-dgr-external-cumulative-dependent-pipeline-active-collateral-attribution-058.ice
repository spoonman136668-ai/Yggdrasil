{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-ATTRIBUTION-058",
  "program": "Yggdrasil active-collateral coalition attribution",
  "question": "Why did the two-row collateral guard in 057 fail: does technical-prose recovery require a larger historical active-row coalition, or does post-injection state destroy recoverability even when the full historical coalition is restored?",
  "hypothesis": "Replay the exact four affected 057 schedules through the exact rebalanced historical state and final future-C packet 12. This is attribution only. For each schedule, freeze the historical technical-prose active partition (the seven rows selected by technical-prose contribution before future C). After byte-identical carry6 injection into the final C state, evaluate diagnostic counterfactual active partitions k=1..7: reserve the top-k rows from that frozen historical prose-active ordering, then fill remaining slots by the unchanged dependent-cue ranking. Record prose collateral score for each k. The minimum k yielding positive prose collateral is an attribution statistic, not a retained policy. If no k<=7 restores positivity, classify post-injection state incompatibility. Heldout scores may classify the already-frozen counterfactuals but may not alter the grid, ordering, bytes, carry, capacity, or any future mechanism.",
  "exact_parent_sha": "ce928b3d2b4af0622c790be3d98ba28afff1cb8d",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-active-collateral-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; attribution does not retain a mechanism"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-057",
    "github_run_id": "37144120318",
    "classification": "negative",
    "observation": {
      "candidate_positive_prose_collateral_schedule_count": 0,
      "candidate_mean_packet_reduction": 0,
      "candidate_positive_reduction_schedule_count": 0,
      "candidate_partner_collateral_failure_count": 0
    },
    "diagnosis": "Two-row prose reservation is insufficient in all four affected schedules under the exact 055/057 state."
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
  "frozen_reuse": {
    "affected_schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "history": "byte-identical rebalanced 057",
    "future_packet": 12,
    "carry6_injection": "byte-identical 057",
    "dependent_cue": "byte-identical 057",
    "historical_prose_active_order": "top seven rows by technical-prose historical cue contribution, tie higher utility then key",
    "diagnostic_k_grid": [
      1,
      2,
      3,
      4,
      5,
      6,
      7
    ],
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
      "diagnostic_k_count",
      "==",
      7
    ],
    [
      "diagnostic_record_count",
      "==",
      28
    ],
    [
      "historical_positive_count",
      "==",
      4
    ],
    [
      "attribution_accounting_error_count",
      "==",
      0
    ],
    [
      "heldout_selection_use_count",
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
    "supported": "Validity passes and all four schedules receive a deterministic attribution: minimum positive coalition k in 1..7 or post_injection_state_incompatibility if none restores positive prose collateral.",
    "negative": "Validity passes but one or more schedules cannot be attributed by the frozen k-grid.",
    "invalid": "Any parent, authority, source, history/carry identity, k-grid, heldout-use boundary, capacity, determinism, provenance, or accounting criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter sources, rebalanced history, final packet, carry6 injection, historical prose ordering, k-grid 1..7, dependent fill ranking, capacity, metrics, attribution rules, classification, or authority after primary output.",
  "successor_if_minimum_k_identified": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-059",
    "intent": "preregister one bounded training-only coalition selector at the attributed fixed k, compare against no-change under equal budgets, then require disjoint transfer before retention"
  },
  "successor_if_state_incompatibility": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-STATE-COMPATIBILITY-059",
    "intent": "attribute which injected-map interaction destroys technical-prose recoverability before proposing a mechanism"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-active-collateral-attribution-058.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-active-collateral-attribution-058.py",
    ".github/workflows/external-cumulative-dependent-pipeline-active-collateral-attribution-058.yml"
  ]
}
