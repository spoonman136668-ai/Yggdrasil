{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-ATTRIBUTION-058",
  "program": "Yggdrasil active-collateral selector failure attribution",
  "question": "Why did the 057 two-row prose guard leave technical-prose collateral at zero: are the two guarded rows intrinsically insufficient, or do the five dependent-ranked fill rows erase otherwise recoverable prose support?",
  "hypothesis": "Replay the exact four affected 057 schedules at frozen future packet 12 with byte-identical rebalanced history, carry6 injection, 16/7/9 capacity, dependent task, and heldout isolation. Construct diagnostic active partitions only; do not alter the accepted mechanism. B=unchanged 055 reserved carry6 partition. G2D5=exact 057 candidate (two top historical prose-contribution guard rows plus five dependent-ranked rows). G2P5=the same two guard rows plus five remaining rows ranked by technical-prose cue contribution. P7=top seven post-injection rows ranked by technical-prose cue contribution. Score prose collateral, partner collateral, and dependent task for all four partitions. Assign exactly one category per schedule: guard_pair_insufficient if P7 prose>0 but G2P5 prose<=0; dependent_fill_conflict if G2P5 prose>0 but G2D5 prose<=0; partner_tradeoff if G2D5 prose>0 and partner<=0; dependent_tradeoff if G2D5 prose>0 and partner>0 but dependent<=0; selector_no_effect if G2D5 active keys equal B and prose remains<=0; preserved_without_success if G2D5 prose>0 and partner/dependent>0 but frozen success still fails; unresolved otherwise. No data, carry, injection, capacity, success rule, or retained mechanism changes.",
  "exact_parent_sha": "ce928b3d2b4af0622c790be3d98ba28afff1cb8d",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-active-collateral-attribution-r2",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; attribution before any new candidate mechanism"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-057",
    "github_run_id": "37144120318",
    "classification": "negative",
    "observation": {
      "baseline_mean_first_success_packet": 13,
      "candidate_mean_first_success_packet": 13,
      "candidate_mean_packet_reduction": 0,
      "candidate_positive_reduction_schedule_count": 0,
      "candidate_positive_prose_collateral_schedule_count": 0,
      "candidate_partner_collateral_failure_count": 0
    },
    "diagnosis": "Two-row collateral reservation did not improve technical-prose collateral or future-data learning efficiency."
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
    "future_packet": 12,
    "historical_bytes": "byte-identical 057/055 rebalanced history",
    "carry_injection": "byte-identical 057 carry6",
    "baseline_partition": "byte-identical 055",
    "candidate_partition": "byte-identical 057 G2D5",
    "capacity": "16 total / 7 active / 9 retained",
    "evaluations": "byte-identical technical-prose collateral, partner collateral, dependent task"
  },
  "diagnostic_partitions": {
    "B": "unchanged 055 reserved carry6 active set",
    "G2D5": "exact 057 selector",
    "G2P5": "same frozen two guard rows as 057; fill remaining five by descending technical-prose cue contribution, tie utility then key",
    "P7": "top seven post-injection rows by descending technical-prose cue contribution, tie utility then key"
  },
  "categories": [
    "guard_pair_insufficient",
    "dependent_fill_conflict",
    "partner_tradeoff",
    "dependent_tradeoff",
    "selector_no_effect",
    "preserved_without_success",
    "unresolved"
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
      "attribution_accounting_error_count",
      "==",
      0
    ],
    [
      "candidate_identity_mismatch_count",
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
    "supported": "Validity passes; all four schedules receive exactly one frozen attribution category with zero candidate-identity mismatch, and at least one non-unresolved category explains the 057 failure.",
    "negative": "Validity passes but all four schedules remain unresolved.",
    "invalid": "Any parent, authority, source, packet identity, history/carry/injection identity, candidate identity, heldout isolation, capacity, accounting, determinism, or provenance criterion fails."
  },
  "successor_if_dependent_fill_conflict_dominates": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-FILL-059",
    "intent": "test one frozen mixed collateral/dependent fill rule against unchanged 057 under equal budgets; require later disjoint transfer before retention"
  },
  "successor_if_guard_pair_insufficient_dominates": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-WIDTH-059",
    "intent": "factor guard width under fixed active capacity before proposing a retained selector"
  },
  "successor_otherwise": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-FACTORIAL-059",
    "intent": "factor the dominant tradeoff indicated by 058 without changing data/compute/capacity budgets"
  },
  "no_post_result_tuning_rule": "Do not alter source identities, affected schedules, packet 12, rebalanced history, carry6/injection, B/G2D5/G2P5/P7 definitions, scoring, categories, metrics, classification, capacity, or authority after primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-active-collateral-attribution-058.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-active-collateral-attribution-058.py",
    ".github/workflows/external-cumulative-dependent-pipeline-active-collateral-attribution-058.yml"
  ]
}
