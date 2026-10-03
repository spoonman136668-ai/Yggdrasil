{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-059",
  "program": "Yggdrasil fixed-k active-collateral coalition candidate under fixed future-data budget",
  "question": "Does the smallest single fixed historical technical-prose coalition that covered every 058 schedule (k=7) restore full dependent-task success versus the unchanged carry6 baseline without increasing data, compute, capacity, or authority?",
  "hypothesis": "Replay the exact four affected 058 schedules, rebalanced historical state, future-C split, twelve-packet budget, carry6 injection, dependent cue, 16/7/9 capacity, and no-change baseline. Freeze one bounded candidate before execution: after carry6 injection, reserve the top seven rows from the historical technical-prose active ordering identified by the training-only contribution ranking; because k=7 equals active capacity, the candidate active partition is exactly that frozen seven-row coalition. k=7 is selected solely from the completed 058 attribution as the smallest single fixed k that was positive across all four schedules; there is no per-run or heldout-driven k selection. Compare candidate versus byte-identical no-change carry6 baseline at all twelve packets using the unchanged full success rule: dependent score >0, technical-prose collateral >0, partner collateral >0. This experiment does not retain the candidate. Even if supported, a preregistered disjoint future split/task replication is mandatory before retention.",
  "exact_parent_sha": "1ba9f44a7508e9d6e4a36f5f8456148be7911205",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-collateral-coalition-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; bounded candidate test, no retention without disjoint transfer"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-ATTRIBUTION-058",
    "github_run_id": "37149126747",
    "classification": "supported",
    "observation": {
      "affected_schedule_count": 4,
      "minimum_positive_k_by_schedule": {
        "A-C-B": 5,
        "B-C-A": 7,
        "C-A-B": 5,
        "C-B-A": 7
      },
      "post_injection_state_incompatibility_count": 0,
      "selected_global_fixed_k": 7
    },
    "interpretation": "The failure is coalition-size dependent, not state incompatibility. Seven historical prose-active rows are the smallest single fixed coalition covering all four observed schedules."
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
    "history": "byte-identical rebalanced 058",
    "future_split": "byte-identical 058",
    "packet_budget": 12,
    "carry6_injection": "byte-identical 058",
    "dependent_cue": "byte-identical 058",
    "baseline": "byte-identical 057/058 carry6 dependent-cue active selection",
    "candidate_k": 7,
    "candidate_order": "top seven rows by historical technical-prose cue contribution; tie higher utility then key",
    "capacity": "16 total / 7 active / 9 retained",
    "retention": false
  },
  "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
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
      "candidate_k",
      "==",
      7
    ],
    [
      "packet_budget_per_schedule",
      "==",
      12
    ],
    [
      "candidate_selection_heldout_use_count",
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
    "supported": "Validity passes; fixed k=7 candidate has positive prose collateral in all four schedules, no partner collateral failure, reduces packets-to-success in at least three of four schedules, and mean packet reduction is at least 1.0 versus no-change.",
    "mixed": "Validity passes and k=7 restores positive prose collateral broadly but does not meet both transfer-efficiency thresholds.",
    "negative": "Validity passes but k=7 does not restore full task success or produces no positive packet-efficiency gain.",
    "invalid": "Any parent, authority, source, split, carry identity, fixed-k identity, heldout-selection boundary, capacity, determinism, provenance, or accounting criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter sources, schedules, rebalanced history, future split, packet count, carry6 injection, dependent cue, k=7, coalition ordering, baseline, success rule, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-TRANSFER-060",
    "intent": "replicate the frozen k=7 mechanism on a preregistered disjoint future split/task under identical budgets before any retention"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRADEOFF-060",
    "intent": "attribute whether the fixed seven-row prose coalition sacrifices dependent or partner utility before changing the mechanism"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-059.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-059.py",
    ".github/workflows/external-cumulative-dependent-pipeline-collateral-coalition-059.yml"
  ]
}
