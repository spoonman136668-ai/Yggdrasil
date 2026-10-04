{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-070",
  "program": "Yggdrasil training-only induction of a context-local retained row on the third manifest",
  "question": "Can a row induced from the third-manifest B+C training-only donor, whose key actually occurs in third-manifest prose context, restore prose collateral where the transported old retained row failed because of target-context mismatch?",
  "hypothesis": "Use only the immutable third manifest e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7 and the exact 068/069 construction. Build one canonical B+C donor state using third-manifest structured+technical-prose training cues with the byte-identical rebalancing, matched-minimax 16-row builder and specialized map. For each donor row, count exact 4-byte key occurrences in the technical-prose training cue and successor bytes. Eligible rows must: (1) occur at least once in prose training, (2) have at least one observed successor, (3) have training-only successor argmax equal to the donor row best, and (4) be present in the donor specialized map with map_best equal to donor best. Rank eligible rows by prose training key occurrence count descending, then argmax successor count descending, then row utility descending, then lexicographic key ascending; freeze the top row as LOCAL_R before any evaluation. No evaluation bytes, labels, schedule outcomes, or packet outcomes may influence selection. In each of the four frozen schedules, inject LOCAL_R exactly as a donor row while preserving 16 total structures. PASSIVE carries the row in state but uses the original prose guard. ACTIVE uses the original prose guard unchanged if LOCAL_R is already present; otherwise it replaces only guard rank 7 with LOCAL_R. Compare original/passive/active under the byte-identical 068 scoring and 12-packet budget.",
  "exact_parent_sha": "65675f40549edc4983d576845c12ca5fafd807b1",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-context-local-key-induction-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-TRANSFER-FACTORIAL-069",
    "github_run_id": 37165379273,
    "classification": "supported",
    "attribution": "TARGET_CONTEXT_MISMATCH",
    "observation": {
      "position_variant_count": 7,
      "position_max_positive_prose_collateral_schedule_count": 0,
      "prose_train_retained_key_occurrence_count": 0,
      "prose_eval_retained_key_occurrence_count": 0,
      "activation_position_attribution_flag": 0,
      "payload_mismatch_attribution_flag": 0,
      "target_context_mismatch_attribution_flag": 1
    },
    "interpretation": "The old retained row is well-formed and position-independent but its key is absent from the new prose context; the next test must induce a context-local row using training-only state rather than transport the old key."
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
  "frozen_induction": {
    "canonical_donor_domains": [
      "B",
      "C"
    ],
    "canonical_donor_split": "60% training cue / 40% evaluation per source; only training cues may participate in induction",
    "canonical_donor_rebalancing": "byte-identical 068 rebalanced(B,C)",
    "canonical_donor_builder": "byte-identical 068 matched-minimax 16-row build + specialized_map",
    "candidate_pool": "exact canonical donor rows only; no row synthesis or rebinding",
    "eligibility": [
      "exact 4-byte row key occurs >=1 in technical-prose training cue",
      "at least one training successor byte observed after the key",
      "training successor argmax equals donor row best",
      "donor map contains key and map_best equals donor row best"
    ],
    "ranking": [
      "prose training key occurrence count descending",
      "training argmax successor count descending",
      "donor row utility descending",
      "lexicographic key ascending"
    ],
    "selected_row_count": 1,
    "heldout_selection_count": 0,
    "row_synthesis_count": 0
  },
  "frozen_reuse": {
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 068",
    "required_union_injection": "byte-identical 068 with LOCAL_R as exact donor row",
    "active_position": "rank 7 only when LOCAL_R is absent from original prose guard",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "metrics_and_thresholds": [
    [
      "local_candidate_count",
      ">=",
      1
    ],
    [
      "selected_local_key_train_occurrence_count",
      ">=",
      1
    ],
    [
      "selected_local_key_train_argmax_count",
      ">=",
      1
    ],
    [
      "selected_local_row_map_best_mismatch_count",
      "==",
      0
    ],
    [
      "local_row_synthesis_count",
      "==",
      0
    ],
    [
      "heldout_local_row_selection_count",
      "==",
      0
    ],
    [
      "active_local_use_schedule_count",
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
    "supported": "valid, a context-local donor row is selected from training only, ACTIVE improves positive-prose collateral over ORIGINAL on at least one schedule, partner collateral failures remain zero, and all frozen thresholds pass",
    "mixed": "valid and LOCAL_R changes dependent/partner behavior or first-success timing but does not improve positive-prose collateral over ORIGINAL",
    "negative": "valid but no eligible LOCAL_R exists or ACTIVE is behaviorally equivalent/worse without prose-collateral improvement",
    "invalid": "any parent, authority, manifest identity, donor construction, induction eligibility/ranking, evaluation-isolation, donor-row identity, active-position rule, deterministic replay, capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter source identities, canonical B+C donor construction, induction eligibility/ranking, row payload, rank-7 activation rule, schedules, split, packet count, success rule, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-ROW-RETAIN-REVERT-071",
    "intent": "verify bounded retain/revert for the induced context-local row before broader cumulative integration or cross-manifest retention"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071",
    "intent": "factor candidate eligibility/ranking versus row activation without using heldout results to select a row"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-070.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-070.py",
    ".github/workflows/external-cumulative-dependent-pipeline-context-local-key-induction-070.yml"
  ]
}
