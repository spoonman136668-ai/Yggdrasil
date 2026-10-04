{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071",
  "program": "Yggdrasil factorial attribution of context-local candidate rank versus activation position",
  "question": "Did Y70 fail because its deterministic rank-1 local donor row was the wrong candidate, because rank-7 activation was wrong for that row, or because a single local row is insufficient?",
  "hypothesis": "Replay the exact Y70 third-manifest induction and require the same ordered eligible donor pool. Y70 sealed local_candidate_count=2; therefore 071 freezes candidate ranks {1,2} from the unchanged training-only eligibility/ranking rule and active positions {1..7}. Evaluate all 14 candidate-rank × position cells; no result chooses a candidate or position. For each cell, use the exact donor row payload for that candidate. Construct each active guard from the original seven prose-guard rows by removing the candidate if already present, otherwise dropping only the original row at the target position, then inserting the candidate at that target position; preserve six original rows and exactly seven unique active rows. All schedules, 12 packets, scoring, split and 16/7/9 capacity remain byte-identical to 068/Y70. Attribution is CANDIDATE_RANK if rank-2 rescues at any position while rank-1 rescues nowhere; ACTIVATION_POSITION if rank-1 rescues outside rank 7; CANDIDATE_POSITION_INTERACTION if rescue exists only for rank-2 outside rank 7; MULTIPLE if more than one attribution pattern is simultaneously true; NO_RESCUE if no cell restores positive prose collateral without partner failure.",
  "exact_parent_sha": "6cca52d3c69f2884ef92f5407ebd31819fa467ff",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-local-key-induction-factorial-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-070",
    "github_run_id": 37166281621,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "local_candidate_count": 2,
      "selected_rank": 1,
      "selected_local_key": [
        32,
        116,
        104,
        101
      ],
      "selected_local_key_train_occurrence_count": 8,
      "selected_local_key_train_argmax_count": 7,
      "active_local_use_schedule_count": 2,
      "original_positive_prose_collateral_schedule_count": 0,
      "active_positive_prose_collateral_schedule_count": 0,
      "original_mean_first_success_packet": 13,
      "active_mean_first_success_packet": 13,
      "active_partner_collateral_failure_count": 0
    }
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
  "frozen_factors": {
    "candidate_ranks": [
      1,
      2
    ],
    "candidate_source": "ordered eligible canonical B+C donor rows from byte-identical Y70 induction rule",
    "expected_candidate_count": 2,
    "activation_positions": [
      1,
      2,
      3,
      4,
      5,
      6,
      7
    ],
    "variant_count": 14,
    "active_guard_rule": "remove candidate if already present; if absent remove original row at target rank; insert candidate at target rank; preserve six original rows and exactly seven unique rows",
    "heldout_candidate_selection_count": 0,
    "heldout_position_selection_count": 0,
    "row_synthesis_count": 0
  },
  "frozen_reuse": {
    "induction": "byte-identical Y70 canonical B+C donor, eligibility and ranking",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 068/Y70",
    "required_union_injection": "byte-identical 068 using exact donor candidate row",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "classification_rules": {
    "supported": "valid and at least one of 14 cells has positive-prose collateral on more schedules than ORIGINAL with zero partner collateral failures; attribution is frozen from the candidate-rank/position pattern",
    "mixed": "valid and cells alter dependent/partner behavior or first-success timing but no cell improves positive-prose collateral",
    "negative": "valid and all 14 cells are behaviorally equivalent to or worse than ORIGINAL with no prose-collateral rescue",
    "invalid": "any parent, authority, manifest identity, candidate-pool identity/count, induction rule, factorial completeness, active-guard rule, heldout-selection boundary, donor-row identity, deterministic replay, capacity, provenance, or accounting requirement fails"
  },
  "attribution_rules": {
    "CANDIDATE_RANK": "rank-2 has at least one rescue and rank-1 has none",
    "ACTIVATION_POSITION": "rank-1 has at least one rescue at positions 1..6",
    "CANDIDATE_POSITION_INTERACTION": "rank-2 has rescue outside rank 7, rank-2 rank7 does not rescue, and rank-1 has none",
    "MULTIPLE": "more than one of the above patterns is true",
    "NO_RESCUE": "no cell rescues"
  },
  "no_post_result_tuning_rule": "Do not alter candidate ranks, eligibility/ranking, activation positions, active-guard construction, schedules, split, packet count, scoring, 16/7/9 capacity, attribution rules, classification, or authority after primary output.",
  "successor_by_attribution": {
    "CANDIDATE_RANK": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-RANK-GATE-072",
    "ACTIVATION_POSITION": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-POSITION-GATE-072",
    "CANDIDATE_POSITION_INTERACTION": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-CANDIDATE-POSITION-GATE-072",
    "MULTIPLE": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-FACTORIAL-ATTRIBUTION-072",
    "NO_RESCUE": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-MULTIROW-COALITION-072"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.yml"
  ]
}
