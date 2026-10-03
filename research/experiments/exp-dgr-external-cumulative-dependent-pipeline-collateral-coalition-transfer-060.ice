{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-TRANSFER-060",
  "program": "Yggdrasil disjoint-dataset transfer replication of fixed-k7 collateral coalition",
  "question": "Does the frozen k=7 coalition mechanism from 059 improve future-data learning efficiency on a wholly new code/structured/prose dataset under the same effective data, compute, capacity, and authority budgets?",
  "hypothesis": "Use the new immutable transfer manifest below, truncate each fresh source to the exact effective byte count of the 059 source it replaces, then replay the 059 four affected schedules, 60/40 cue/evaluation split, rebalanced technical-prose history, twelve-packet future stream, carry6 injection, dependent cue, baseline selector, fixed k=7 candidate, success rule, and 16 total / 7 active / 9 retained capacity. The candidate is frozen before any 060 result. Supported requires the k=7 candidate to restore technical-prose collateral in all four schedules, preserve partner collateral, improve packets-to-success in at least three schedules, and reduce mean packets-to-success by at least 1.0 versus no-change on this disjoint dataset. This experiment is the required transfer replication; success makes the mechanism retention-eligible for a later explicit retain/revert experiment, but 060 itself does not promote or persist it.",
  "exact_parent_sha": "7dc1bd70d83157260a10378bcf0902312f99a21c",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-collateral-coalition-transfer-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "portfolio_context": {
    "branch": "research/portfolio-rsi-v1",
    "commit": "0643cb23ac8830c8f130c14cc8385b390d877cdc",
    "role": "advisory-only; transfer advantage required before retention"
  },
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-059",
    "github_run_id": "37149672339",
    "classification": "supported",
    "observation": {
      "candidate_k": 7,
      "baseline_mean_first_success_packet": 13,
      "candidate_mean_first_success_packet": 1,
      "candidate_mean_packet_reduction": 12,
      "candidate_positive_reduction_schedule_count": 4,
      "candidate_positive_prose_collateral_schedule_count": 4,
      "candidate_partner_collateral_failure_count": 0
    },
    "limitation": "059 used the originating external dataset and cannot by itself justify retention."
  },
  "external_transfer_manifest": {
    "schema": "yggdrasil.external-transfer-manifest.v1",
    "sources": [
      {
        "domain": "code",
        "repository": "python/cpython",
        "commit": "ebf955df7a89ed0c7968f79faec1de49f61ed7cb",
        "path": "Lib/statistics.py",
        "full_bytes": 61896,
        "full_sha256": "3023ec949802c2e880a000775bfd1a6b70c21b5423881118141e3ec69d8e3336",
        "effective_prefix_bytes": 41453,
        "effective_prefix_sha256": "66bb25b24a0316b4965c64798494de93a1d7332672b15b5f430ab6a2fb4b9d45"
      },
      {
        "domain": "structured",
        "repository": "json-schema-org/JSON-Schema-Test-Suite",
        "commit": "5b0ee1613e45fcc2bddac00e07c19cd49b00d8a8",
        "path": "tests/draft2020-12/uniqueItems.json",
        "full_bytes": 14490,
        "full_sha256": "ed84ef6ddc827659e257ba64cbe9679f06932b6320bea5c07622bf3d2cc4daa5",
        "effective_prefix_bytes": 14365,
        "effective_prefix_sha256": "95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932"
      },
      {
        "domain": "technical_prose",
        "repository": "golang/go",
        "commit": "6f5c275ebdc454197fff5f1496521c8f81e20eef",
        "path": "doc/README.md",
        "full_bytes": 3124,
        "full_sha256": "c1bf000e7a873b3afed329c5b9f9c07f7692b1d7fb2bfca2d7600cec8b1d1407",
        "effective_prefix_bytes": 1454,
        "effective_prefix_sha256": "48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b"
      }
    ],
    "effective_total_bytes": 57272
  },
  "external_transfer_manifest_sha256": "c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250",
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "effective_domain_bytes": {
      "code": 41453,
      "structured": 14365,
      "technical_prose": 1454
    },
    "source_split": "60% cue / 40% evaluation exactly as 059 loader semantics",
    "affected_schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "history_rebalancing": "byte-identical 059 rule",
    "future_packets": 12,
    "carry6_injection": "byte-identical 059",
    "dependent_cue": "byte-identical 059",
    "baseline": "byte-identical 059 no-change carry6 active selection",
    "candidate_k": 7,
    "candidate_order": "top seven rows by historical technical-prose contribution; tie higher utility then key",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained",
    "retention": false
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
      "transfer_manifest_identity_mismatch_count",
      "==",
      0
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
    "supported": "Validity passes and the frozen k=7 candidate transfers its packet-efficiency/collateral advantage to the wholly new manifest under the fixed 059 budgets.",
    "mixed": "Validity passes and the candidate preserves collateral on the new data but does not meet both preregistered packet-efficiency transfer thresholds.",
    "negative": "Validity passes but the originating-dataset advantage does not transfer or harms collateral.",
    "invalid": "Any parent, authority, transfer-manifest, prefix identity, effective-byte budget, split, mechanism identity, heldout-selection boundary, capacity, determinism, provenance, or accounting criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter source files/commits/hashes/prefix lengths, effective byte budgets, split, schedules, history rule, future packets, carry6 injection, dependent cue, k=7, active ordering, baseline, success rule, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-RETAIN-REVERT-061",
    "intent": "mark k=7 as transfer-supported inside a bounded research candidate state, verify exact retain/revert and rollback semantics, and expose another unseen future dataset before calling the change retained"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-ATTRIBUTION-061",
    "intent": "attribute why the 059 advantage failed to transfer before modifying the mechanism"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-transfer-060.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-collateral-coalition-transfer-060.py",
    ".github/workflows/external-cumulative-dependent-pipeline-collateral-coalition-transfer-060.yml"
  ]
}
