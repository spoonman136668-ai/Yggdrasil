{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-TRANSFER-FACTORIAL-069",
  "program": "Yggdrasil factorial attribution of transported retained-state failure",
  "question": "Why did exact retained row R improve dependent/partner counts but fail to restore prose collateral on the third manifest: activation position, retained payload mismatch, or target-context mismatch?",
  "hypothesis": "Use only the immutable third manifest e46907... and exact retained state R from 067. Preserve 068 construction, schedules, 60/40 split, 12 packets, scoring and 16/7/9 capacity. Factor A (activation position): for each schedule, transport R into the 16-row state and evaluate seven preregistered guards formed by replacing exactly guard rank positions 1..7 with R (or unchanged if R already occupies that position); no result chooses a position. Factor B (context identity): count exact 4-byte R-key occurrences and observed successor bytes in the training-only technical-prose cue; separately count R-key occurrences in evaluation for evaluator-only attribution. If training occurrences exist, report training-only argmax successor and whether it equals retained best=32. Do not synthesize/rebind a row. Attribution labels are frozen: ACTIVATION_POSITION if at least one position yields more positive-prose schedules than rank7; PAYLOAD_MISMATCH if no position rescues, training R occurs, and training argmax successor differs from 32; TARGET_CONTEXT_MISMATCH if no position rescues and R has zero training occurrences; otherwise UNRESOLVED.",
  "exact_parent_sha": "36f38df165cb35cda6def1cc3ce8078b5f720a62",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-retained-state-transfer-factorial-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-STATE-TRANSPORT-ATTRIBUTION-068",
    "github_run_id": 37164857152,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "transported_state_identity_mismatch_count": 0,
      "active_transport_use_schedule_count": 4,
      "passive_transport_state_schedule_count": 4,
      "original_positive_prose_collateral_schedule_count": 0,
      "passive_positive_prose_collateral_schedule_count": 0,
      "active_positive_prose_collateral_schedule_count": 0,
      "original_mean_first_success_packet": 13,
      "passive_mean_first_success_packet": 13,
      "active_mean_first_success_packet": 13,
      "capacity_growth_event_count": 0,
      "invalid_evaluation_rows": 0
    },
    "retained_state": {
      "key": [
        10,
        32,
        32,
        32
      ],
      "best": 32,
      "best_count": 112,
      "total": 112,
      "consistency": 1,
      "utility": 112,
      "cell_index": 12,
      "map_best": 32
    }
  },
  "external_manifest": {
    "path": "research/experiments/external-future-data-third-manifest-066.json",
    "sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "source_count": 3,
    "effective_total_bytes": 57272
  },
  "external_authority": {
    "ckb_plane_main_sha": "2518306c74ff426278f31b1199f8ad9891299d14",
    "manifest_sha256": "e46907e74ce92564bab657afc8d28b1a39b269bac88fb9b21092716c7ff53cb7",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_factors": {
    "retained_state": {
      "key": [
        10,
        32,
        32,
        32
      ],
      "best": 32,
      "best_count": 112,
      "total": 112,
      "consistency": 1,
      "utility": 112,
      "cell_index": 12,
      "map_best": 32
    },
    "activation_positions": [
      1,
      2,
      3,
      4,
      5,
      6,
      7
    ],
    "position_variant": "replace exactly the indicated training-ranked prose_guard7 row with R; preserve the other six rows and all row payloads",
    "training_context_measure": "sliding exact 4-byte R-key matches within the technical-prose training cue; successor is immediately following byte",
    "evaluator_context_measure": "same exact-key occurrence count in technical-prose evaluation; unavailable to position construction or any decision",
    "variant_selection_from_results": false
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
    "required_union_injection": "byte-identical 068 with immutable transported R",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "classification_rules": {
    "supported": "valid and attribution is one of ACTIVATION_POSITION, PAYLOAD_MISMATCH, TARGET_CONTEXT_MISMATCH with all frozen accounting/isolation criteria passing",
    "mixed": "valid but evidence matches more than one attribution or only partially separates hypotheses",
    "negative": "valid and attribution remains UNRESOLVED",
    "invalid": "any parent, authority, manifest identity, retained-state identity, position sweep completeness, heldout-selection boundary, deterministic replay, capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter R, retained payload, activation positions, position replacement rule, key-occurrence measurement, schedules, split, packets, scoring, 16/7/9 capacity, attribution rules, classification, or authority after primary output.",
  "successor_by_attribution": {
    "ACTIVATION_POSITION": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-NEUTRAL-POSITION-GATE-070",
    "PAYLOAD_MISMATCH": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-PAYLOAD-REBINDING-070",
    "TARGET_CONTEXT_MISMATCH": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-070",
    "UNRESOLVED": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-TRANSFER-FACTORIAL-070"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-retained-state-transfer-factorial-069.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-state-transfer-factorial-069.py",
    ".github/workflows/external-cumulative-dependent-pipeline-retained-state-transfer-factorial-069.yml"
  ]
}
