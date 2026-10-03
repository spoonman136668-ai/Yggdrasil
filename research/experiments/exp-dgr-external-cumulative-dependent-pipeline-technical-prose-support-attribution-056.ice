{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-ATTRIBUTION-056",
  "program": "Yggdrasil downstream loss attribution after fixed-budget technical-prose support repair",
  "question": "After 055 restored positive historical technical-prose support under the fixed byte budget, why did all four affected schedules still fail the dependent task?",
  "hypothesis": "Replay only the four affected 055 schedules with the exact rebalanced historical byte allocation, carry6 construction, future-C packets, dependent task, and 16/7/9 capacity. At the final packet (12), trace the technical-prose capability through frozen checkpoints: H historical rebalanced support; K protected-key membership in carry6; I protected-key survival after injection plus technical-prose score under its own contribution-ranked active partition; R protected-key membership in the actual reserved dependent active set plus reserved technical-prose collateral score; D final dependent score and partner collateral score. Assign exactly one frozen attribution per schedule in order: historical_not_positive if H<=0; row_not_carried if H>0 and K=false; injection_loss if K=true and protected key absent after injection; reservation_selection_loss if present after injection but not active at R; active_score_loss if active at R but technical-prose collateral<=0; preserved_but_dependent_failure if technical-prose collateral>0 and the schedule still fails because dependent or partner collateral is nonpositive. No byte allocation, carry ranking, injection/eviction, active selection, capacity, packet schedule, heldout task, or success criterion changes.",
  "exact_parent_sha": "4edd6b72a6fd86231ca82816027ae0dcae27e3cd",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-technical-prose-support-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; no mechanism retention without disjoint transfer"
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
    "diagnosis": "Equal-byte reallocation restored technical-prose historical support from 0 to +1 in all four affected schedules without harming controls, but did not produce a successful dependent pipeline at any packet."
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
    "rebalanced_history_rule": "byte-identical 055",
    "future_packet": 12,
    "carry_mechanism": "carry6 byte-identical 055",
    "injection_eviction": "byte-identical 055",
    "dependent_active_selector": "byte-identical 055",
    "dependent_eval": "byte-identical 055",
    "success_rule": "byte-identical 055",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "attribution_categories": [
    "historical_not_positive",
    "row_not_carried",
    "injection_loss",
    "reservation_selection_loss",
    "active_score_loss",
    "preserved_but_dependent_failure"
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
      "affected_schedule_count",
      "==",
      4
    ],
    [
      "attribution_record_count",
      "==",
      4
    ],
    [
      "historical_positive_count",
      "==",
      4
    ],
    [
      "failed_final_packet_count",
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
    "supported": "Validity passes and all four persistent 055 failures receive exactly one frozen downstream attribution with complete accounting.",
    "negative": "Validity passes but one or more failed schedules cannot be attributed by the frozen checkpoints.",
    "invalid": "Any parent, authority, source, byte-allocation identity, carry/injection/selection identity, final-packet identity, heldout isolation, capacity, determinism, provenance, or accounting criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter 055 source identities, rebalanced history, carry6, packet 12, injection/eviction, active selector, dependent task, success rule, capacity, attribution categories, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_active_score_loss_dominates": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-057",
    "intent": "test one frozen collateral-aware active selection rule against unchanged 055 under equal budgets; require later disjoint transfer before retention"
  },
  "successor_if_preserved_but_dependent_failure_dominates": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-DERIVED-STATE-057",
    "intent": "test whether an explicit retained A+B derived-state row, rather than source support, improves the dependent A+B+C task under fixed capacity and equal budgets"
  },
  "successor_otherwise": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-FACTORIAL-057",
    "intent": "factor carry identity, injection, reservation and collateral scoring without changing data/compute/capacity budgets"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-technical-prose-support-attribution-056.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-technical-prose-support-attribution-056.py",
    ".github/workflows/external-cumulative-dependent-pipeline-technical-prose-support-attribution-056.yml"
  ]
}
