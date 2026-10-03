{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ATTRIBUTION-054",
  "program": "Yggdrasil dependent-pipeline transfer failure attribution",
  "question": "Why did the retained-state mechanisms in 053 improve future-data learning in only two of six schedules: is failure localized to historical technical-prose support, carried-row identity, injection/eviction, or seven-active-slot selection?",
  "hypothesis": "Replay the exact six schedules, history/future split, twelve-packet budget, carry6/carry7 candidate construction, and heldout-isolation contract from 053. Add only frozen diagnostic checkpoints. For each historical domain in each schedule, measure collateral recoverability at four stages: (H) historical A+B state before future C; (C) C-only future state; (I) post-injection 16-row state scored with the domain's own contribution-ranked seven-active partition without carry reservation; and (R) the actual reserved carry6/carry7 dependent-cue partition used by 053. Also record whether the highest-contribution historical row for each domain is present in the carry set, survives injection, and is active at R. Attribution categories are frozen: historical_support_failure if H<=0; row_not_carried if H>0 and protected historical key is absent from carry; injection_loss if key is carried but absent after injection; reservation_selection_loss if present after injection but inactive at R; cross_domain_active_interference if active at R but collateral<=0; preserved if collateral>0. No mechanism, row ranking, capacity, data split, packet schedule, or success criterion changes.",
  "exact_parent_sha": "3bb0a60b818ad9901252688f99f6de90112a5f83",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; no mechanism may be retained without later disjoint transfer"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSFER-053",
    "github_run_id": "37142374613",
    "classification": "negative",
    "observation": {
      "cold_mean_first_success_packet": 13,
      "carry6_mean_first_success_packet": 9,
      "carry7_mean_first_success_packet": 9,
      "selected_candidate_mean_packet_reduction": 4,
      "selected_candidate_positive_reduction_schedule_count": 2,
      "selected_candidate_collateral_failure_count": 4,
      "successful_schedules": [
        "A-B-C",
        "B-A-C"
      ],
      "failed_schedules": [
        "A-C-B",
        "B-C-A",
        "C-A-B",
        "C-B-A"
      ]
    },
    "frozen_pattern": "Both successful schedules exclude technical-prose from the historical pair; all four failed schedules include technical-prose in the historical pair."
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
    "sources": "byte-identical 053",
    "schedules": "byte-identical six 053 permutations",
    "split": "byte-identical first-half historical A/B and second-half future C",
    "future_packets": 12,
    "mechanisms": [
      "carry6",
      "carry7"
    ],
    "carry_ranking": "byte-identical 053",
    "injection_eviction": "byte-identical 053",
    "dependent_cue": "byte-identical 053",
    "success_rule": "byte-identical 053",
    "capacity": "16 total / 7 active / 9 retained",
    "heldout_selection_use": false
  },
  "attribution_categories": [
    "historical_support_failure",
    "row_not_carried",
    "injection_loss",
    "reservation_selection_loss",
    "cross_domain_active_interference",
    "preserved"
  ],
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
      "schedule_count",
      "==",
      6
    ],
    [
      "mechanism_count",
      "==",
      2
    ],
    [
      "attribution_record_count",
      "==",
      24
    ],
    [
      "failed_053_schedule_count",
      "==",
      4
    ],
    [
      "successful_053_schedule_count",
      "==",
      2
    ],
    [
      "technical_prose_historical_failure_schedule_count",
      ">=",
      3
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
    "supported": "Validity passes and at least three of the four failed 053 schedules attribute the failing collateral path to the historical technical-prose capability through one frozen category, with complete accounting.",
    "mixed": "Validity passes and failures are attributable, but no single technical-prose-linked category explains at least three of four failed schedules.",
    "negative": "Validity passes but the diagnostic checkpoints do not explain the 053 collateral failures under the frozen attribution categories.",
    "invalid": "Any parent, authority, source, split, mechanism identity, attribution accounting, heldout isolation, capacity, determinism, or provenance criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter 053 sources, schedules, splits, packets, carry sets, injection/eviction, active selector, capacity, checkpoints, attribution categories, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-055",
    "intent": "test one preregistered bounded support mechanism targeted to the attributed technical-prose failure, still against no-change and requiring later disjoint transfer before retention"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-FACTORIAL-055",
    "intent": "factor carried-row identity, injection, and active reservation separately under the same fixed budgets before proposing any mechanism change"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-attribution-054.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-attribution-054.py",
    ".github/workflows/external-cumulative-dependent-pipeline-attribution-054.yml"
  ]
}
