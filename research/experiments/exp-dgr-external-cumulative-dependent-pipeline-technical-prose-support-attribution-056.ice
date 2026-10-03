{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-ATTRIBUTION-056",
  "program": "Yggdrasil restored-support downstream attribution under fixed budgets",
  "question": "After 055 restored technical-prose historical support in all four affected schedules but produced zero future-data packet improvement, at what frozen downstream stage is that restored support lost?",
  "hypothesis": "Replay the exact 055 baseline and rebalanced histories, carry6 mechanics, future-C twelve-packet stream, dependent evaluation, and fixed 16/7/9 capacity. Restrict primary attribution to the rebalanced arm in the four technical-prose-affected schedules. For technical prose, trace the highest-contribution positive historical row through four frozen stages at packet 1 and packet 12: H=historical rebalanced state, K=selected carry6 key set, I=post-injection 16-row state, R=actual reserved active-7 dependent partition. Score technical-prose collateral at H, I using a prose-ranked active partition, and R. Assign exactly one category per schedule/packet checkpoint: historical_nonpositive if H<=0; row_not_carried if H>0 but the protected key is absent from carry6; injection_loss if carried but absent after injection; reservation_selection_loss if present after injection but inactive in R; active_partition_interference if active in R but technical-prose collateral<=0; preserved_positive if collateral>0 in R. No history allocation, carry rule, eviction, active selection, data, capacity, or success criterion changes.",
  "exact_parent_sha": "4edd6b72a6fd86231ca82816027ae0dcae27e3cd",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-technical-prose-support-attribution-r2",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; optimize future-data learning efficiency under fixed budgets"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-055",
    "github_run_id": "37143304678",
    "classification": "mixed",
    "observation": {
      "rebalanced_technical_prose_positive_historical_support_count": 4,
      "baseline_affected_mean_first_success_packet": 13,
      "rebalanced_affected_mean_first_success_packet": 13,
      "affected_mean_packet_reduction": 0,
      "affected_positive_reduction_schedule_count": 0,
      "control_worsening_schedule_count": 0
    },
    "diagnosis": "Fixed-budget data reallocation restores historical technical-prose support but does not improve the later dependent task, so the remaining bottleneck is downstream of historical support formation."
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
    "schedules": "byte-identical 055",
    "affected_schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "rebalanced_history_rule": "byte-identical 055 fixed-budget reallocation",
    "future_c_rule": "byte-identical 055",
    "carry6_rule": "byte-identical 055",
    "injection_eviction": "byte-identical 055",
    "dependent_eval": "byte-identical 055",
    "success_rule": "byte-identical 055",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "checkpoints": {
    "packets": [
      1,
      12
    ],
    "stages": [
      "H",
      "K",
      "I",
      "R"
    ],
    "protected_row_rule": "highest technical-prose cue contribution row in the rebalanced historical state, ties utility then key",
    "categories": [
      "historical_nonpositive",
      "row_not_carried",
      "injection_loss",
      "reservation_selection_loss",
      "active_partition_interference",
      "preserved_positive"
    ]
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
      "checkpoint_packet_count",
      "==",
      2
    ],
    [
      "attribution_record_count",
      "==",
      8
    ],
    [
      "rebalanced_technical_prose_positive_historical_support_count",
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
    "supported": "Validity passes; all eight affected schedule/checkpoint records receive exactly one frozen downstream attribution category with complete accounting, and at least one non-preserved downstream loss category occurs.",
    "negative": "Validity passes but all eight records are preserved_positive despite 055 showing no future-data packet improvement.",
    "invalid": "Any parent, authority, source, rebalanced-history identity, packet identity, carry/injection/active-selection identity, heldout isolation, capacity, accounting, determinism, or provenance criterion fails."
  },
  "successor_if_active_partition_interference_dominates": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-ACTIVE-GUARD-057",
    "intent": "test one frozen active-partition support guard against no-change under identical data/compute/capacity budgets; require later disjoint replication before retention"
  },
  "successor_otherwise": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-DOWNSTREAM-FACTORIAL-057",
    "intent": "factor carry identity, injection, and reservation effects indicated by 056 before any mechanism change"
  },
  "no_post_result_tuning_rule": "Do not alter 055 source identities, schedules, rebalanced byte allocation, future packets, carry6, injection/eviction, active selector, capacity, checkpoint packets/stages, categories, metrics, thresholds, classification, or authority after primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-technical-prose-support-attribution-056.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-technical-prose-support-attribution-056.py",
    ".github/workflows/external-cumulative-dependent-pipeline-technical-prose-support-attribution-056.yml"
  ]
}
