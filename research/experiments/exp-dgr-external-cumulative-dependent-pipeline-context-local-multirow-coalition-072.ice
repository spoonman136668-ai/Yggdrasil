{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-MULTIROW-COALITION-072",
  "program": "Yggdrasil two-row context-local coalition after single-row NO_RESCUE",
  "question": "Can the two training-only context-local donor rows identified in Y71 restore prose collateral when activated together at fixed capacity, even though neither row rescues alone at any activation position?",
  "hypothesis": "Replay the exact third-manifest Y70/Y71 induction and require the same ordered two-row eligible donor pool: rank1 key [32,116,104,101] and rank2 key [32,97,110,100], each with its exact donor payload. No candidate search remains. For each frozen schedule, build the original seven-row prose guard. PASSIVE injects/carries both local donor rows in the 16-row state but activates the original prose guard unchanged. ACTIVE removes any coalition keys from the original guard, preserves the first five remaining original guard rows in original rank order, and appends rank1 then rank2 coalition rows, yielding exactly seven unique active rows. All source identities, 60/40 splits, four schedules, 12 packets, carry6 logic, scoring and 16 total / 7 active / 9 retained capacity are byte-identical to 068/Y70/Y71. Supported requires ACTIVE to increase positive-prose collateral schedule count over ORIGINAL with zero active partner collateral failures and no capacity growth.",
  "exact_parent_sha": "2b1ed36c4858d837b395bb97bd2d0b770eaabb31",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-local-multirow-coalition-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071",
    "github_run_id": 37166648538,
    "classification": "negative",
    "attribution": "NO_RESCUE",
    "observation": {
      "candidate_count": 2,
      "variant_count": 14,
      "any_rescue_count": 0,
      "behavior_change_cell_count": 0,
      "candidate_1": {
        "key": [
          32,
          116,
          104,
          101
        ],
        "train_occurrence_count": 8,
        "train_argmax_count": 7
      },
      "candidate_2": {
        "key": [
          32,
          97,
          110,
          100
        ],
        "train_occurrence_count": 3,
        "train_argmax_count": 2
      }
    },
    "interpretation": "Candidate identity and activation position are individually insufficient; the next bounded question is whether the two context-local rows are jointly necessary."
  },
  "external_manifest": {
    "path": "research/experiments/external-future-data-third-manifest-066.json",
    "sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "source_count": 3,
    "effective_total_bytes": 57272
  },
  "external_authority": {
    "ckb_plane_main_sha": "c591f97184e22565e8ccfc230a70a58f62b26d5c",
    "manifest_sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_coalition": {
    "expected_candidate_count": 2,
    "candidate_rank_order": [
      1,
      2
    ],
    "candidate_keys": [
      [
        32,
        116,
        104,
        101
      ],
      [
        32,
        97,
        110,
        100
      ]
    ],
    "candidate_payloads": "exact canonical B+C donor rows from unchanged Y70/Y71 induction",
    "passive_rule": "both donor rows carried in state; original prose guard unchanged",
    "active_rule": "remove coalition keys from original guard; preserve first five remaining original rows; append rank1 then rank2 local rows",
    "original_rows_preserved_in_active": 5,
    "local_rows_active": 2,
    "active_row_count": 7,
    "row_synthesis_count": 0,
    "heldout_candidate_selection_count": 0,
    "heldout_position_selection_count": 0
  },
  "frozen_reuse": {
    "induction": "byte-identical Y70/Y71 canonical B+C donor eligibility/ranking",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 068/Y70/Y71",
    "required_union_injection": "byte-identical 068 extended only to require both exact donor coalition rows",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "metrics_and_thresholds": [
    [
      "coalition_candidate_count",
      "==",
      2
    ],
    [
      "passive_coalition_state_schedule_count",
      "==",
      4
    ],
    [
      "active_coalition_use_schedule_count",
      ">=",
      1
    ],
    [
      "active_positive_prose_collateral_schedule_count",
      ">",
      "original_positive_prose_collateral_schedule_count"
    ],
    [
      "active_partner_collateral_failure_count",
      "==",
      0
    ],
    [
      "row_synthesis_count",
      "==",
      0
    ],
    [
      "heldout_candidate_selection_count",
      "==",
      0
    ],
    [
      "heldout_position_selection_count",
      "==",
      0
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
    "supported": "valid and jointly activating the two frozen local donor rows increases positive-prose collateral over ORIGINAL on at least one schedule with zero active partner collateral failures and all frozen thresholds passing",
    "mixed": "valid and the coalition changes dependent/partner behavior or first-success timing but does not increase positive-prose collateral",
    "negative": "valid and ACTIVE is behaviorally equivalent to or worse than ORIGINAL with no prose-collateral rescue",
    "invalid": "any parent, authority, manifest identity, candidate-pool identity/count, donor-row payload, coalition construction, deterministic replay, heldout boundary, capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter candidate pool/order/payloads, five-original-plus-two-local active rule, schedules, split, packet count, scoring, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-COALITION-RETAIN-REVERT-073",
    "intent": "verify bounded retain/revert of the supported two-row coalition before any broader cumulative integration"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-MULTIROW-CAPACITY-ATTRIBUTION-073",
    "intent": "test whether the missing mechanism is broader local-state coverage rather than two-row coalition identity, without silently increasing capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-local-multirow-coalition-072.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-multirow-coalition-072.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-local-multirow-coalition-072.yml"
  ]
}
