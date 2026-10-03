{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-055",
  "program": "Yggdrasil fixed-budget historical data reallocation for technical-prose support",
  "question": "Can fixed-budget historical data reallocation restore technical-prose collateral support and improve later dependent-pipeline learning without increasing total data, compute, capacity, or authority?",
  "hypothesis": "Replay all six 053 schedules and the same future-C twelve-packet stream using carry6 only. Compare two frozen historical-data mechanisms under identical total historical byte budgets per schedule: baseline uses the first half of each historical source exactly as 053; rebalanced uses the full technical-prose cue whenever technical prose is in the historical pair and removes exactly the added technical-prose bytes from the end of the other historical source prefix, preserving total historical bytes. Schedules without technical prose in history are byte-identical controls. All state construction, carry ranking/injection, future-C packets, heldout dependent task, success rule, 16/7/9 capacity, compute, and authority remain unchanged. Supported requires the rebalanced mechanism to make technical-prose historical collateral positive in at least three of four affected schedules, reduce mean packets-to-success versus baseline by at least 1.0 across the four affected schedules, improve at least three of four affected schedules, and not worsen either no-prose control. This experiment does not retain the mechanism; a disjoint replication is mandatory before retention.",
  "exact_parent_sha": "8fa499a2ef067071ad4f80b51fdbd9adc7383279",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-technical-prose-support-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; optimize future-data learning efficiency under fixed budgets"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ATTRIBUTION-054",
    "github_run_id": "37142876124",
    "classification": "supported",
    "observation": {
      "technical_prose_historical_failure_schedule_count": 4,
      "historical_support_failure_count": 8,
      "row_not_carried_count": 0,
      "injection_loss_count": 0,
      "reservation_selection_loss_count": 0,
      "cross_domain_active_interference_count": 0,
      "preserved_count": 16
    },
    "diagnosis": "All four failed 053 schedules fail before carry because the historical technical-prose capability has zero collateral score; carry identity, injection, reservation, and active interference were exonerated."
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
    "schedules": [
      "A-B-C",
      "A-C-B",
      "B-A-C",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "affected_schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "no_prose_controls": [
      "A-B-C",
      "B-A-C"
    ],
    "baseline_history_rule": "first half of each historical cue exactly as 053",
    "rebalanced_history_rule": "if technical prose is historical, use its full cue and shorten the partner historical prefix by exactly the added technical-prose bytes; total historical bytes remain equal to baseline schedule budget",
    "future_c_rule": "byte-identical 053 second-half future C in twelve cumulative packets",
    "mechanism": "carry6 only, byte-identical 053 carry construction/injection/active reservation",
    "dependent_eval": "byte-identical 053 nested heldout A+B+C interleave",
    "success_rule": "dependent heldout incremental correct >0 and both historical collateral increments >0",
    "capacity": "16 total / 7 active / 9 retained",
    "modification_retention": false
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
      "schedule_count",
      "==",
      6
    ],
    [
      "affected_schedule_count",
      "==",
      4
    ],
    [
      "control_schedule_count",
      "==",
      2
    ],
    [
      "history_byte_budget_mismatch_count",
      "==",
      0
    ],
    [
      "rebalanced_technical_prose_positive_historical_support_count",
      ">=",
      3
    ],
    [
      "affected_mean_packet_reduction",
      ">=",
      1
    ],
    [
      "affected_positive_reduction_schedule_count",
      ">=",
      3
    ],
    [
      "control_worsening_schedule_count",
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
    "supported": "Validity passes; rebalancing makes technical-prose historical support positive in at least three of four affected schedules, reduces mean future packets-to-success by at least 1.0, improves at least three affected schedules, and worsens neither control.",
    "mixed": "Validity passes and technical-prose support improves, but the future-data packet or breadth thresholds are not all met.",
    "negative": "Validity passes but fixed-budget reallocation does not materially improve technical-prose support or later learning efficiency.",
    "invalid": "Any parent, authority, source, byte-budget conservation, schedule/split identity, carry identity, heldout isolation, capacity, determinism, or provenance criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter source identities, affected/control schedules, baseline/rebalanced byte-allocation rule, total historical byte budgets, future-C packets, carry6 mechanics, dependent evaluation, success rule, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-TRANSFER-REPLICATION-056",
    "intent": "replicate the fixed-budget reallocation advantage on a second disjoint future split/task before retaining the mechanism"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-ATTRIBUTION-056",
    "intent": "attribute whether insufficient technical-prose bytes, representation overlap, or shared-state competition prevents support before changing budgets or capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-technical-prose-support-055.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-technical-prose-support-055.py",
    ".github/workflows/external-cumulative-dependent-pipeline-technical-prose-support-055.yml"
  ]
}
