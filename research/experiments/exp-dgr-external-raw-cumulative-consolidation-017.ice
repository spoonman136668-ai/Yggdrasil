{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-RAW-CUMULATIVE-CONSOLIDATION-017",
  "program": "Yggdrasil external fixed-capacity cumulative consolidation",
  "question": "Does Yggdrasil's supported fixed-capacity minimax-matched consolidation preserve useful predictive capability across genuinely independent external code, structured JSON, and technical prose without increasing the sixteen-cell substrate?",
  "hypothesis": "Using the exact three-source external manifest, fixed 60% first-half adaptation and 40% heldout evaluation splits, and the unchanged 016 sixteen-cell/radius-two/minimax-matched mechanism, every seen domain will retain positive heldout incremental correct predictions over the frozen baseline, minimum cumulative benefit will retain at least 0.50 of independently adapted benefit, prior-domain benefit will retain at least 0.50 of its first-encounter value, and the seven-active/nine-retained partition will preserve at least 0.50 of full cumulative benefit with zero capacity growth.",
  "exact_parent_sha": "650cafdfae07dfc5ce3f3d23c59810b80b6eb8aa",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-REAL-UTF8-MINIMAX-MATCHED-CONSOLIDATION-016",
    "qualification_run_id": "37075511579",
    "classification": "supported",
    "observation": "The fixed sixteen-cell minimax-matched mechanism preserved positive seen-domain benefit, matched independent adaptation at 1.0 minimum, never underperformed pooled, rescued two pooled failures, and retained 0.8421 of full benefit under exactly seven active and nine retained structures."
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "plan_receipt_run_id": "37079956943",
    "plan_receipt_sha256": "e1585e948b8640d50a3acd8bcea416dff764d32f7994d20aa6867e9e9e1b82aa",
    "fetch_receipt_run_id": "37080155190",
    "fetch_authority_receipt_sha256": "f9b763527699f042322b6aeece814c0fe9d67a3f2e8db02e20dad1b796f54dc6",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host must be distinct from LINKDEADKB",
    "persistent_corpus": false,
    "external_model_calls": false,
    "production_authority": false
  },
  "sources": [
    {
      "name": "A",
      "domain": "code",
      "uri": "https://raw.githubusercontent.com/python/cpython/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Lib/fractions.py",
      "sha256": "7a95f1c506c9ac4b2277df5f2bdd9d61cc67b520c45021a5a961939770221ef6",
      "bytes": 41453
    },
    {
      "name": "B",
      "domain": "structured",
      "uri": "https://raw.githubusercontent.com/json-schema-org/JSON-Schema-Test-Suite/5b0ee1613e45fcc2bddac00e07c19cd49b00d8a8/tests/draft2020-12/type.json",
      "sha256": "4c5cbe6cbcd28af73761091367b20e07d0403847e236c06c31fc27061bd81192",
      "bytes": 14365
    },
    {
      "name": "C",
      "domain": "technical-prose",
      "uri": "https://raw.githubusercontent.com/golang/go/6f5c275ebdc454197fff5f1496521c8f81e20eef/README.md",
      "sha256": "8247b7c5de1e74854aac1a08aa5894444d1d33b4045c70d5cc3367ad0e25c3f3",
      "bytes": 1454
    }
  ],
  "external_split": {
    "rule": "for each exact source bytes, adaptation cue is bytes [0:floor(0.60*N)] and heldout evaluation is bytes [floor(0.60*N):N]",
    "orders": [
      [
        "A",
        "B",
        "C"
      ],
      [
        "C",
        "B",
        "A"
      ]
    ],
    "contamination": "future-domain cue bytes and all heldout bytes are unavailable to candidate generation, contribution scoring, consolidation, activation, or threshold selection"
  },
  "frozen_reuse": {
    "base_training": "byte-identical repo-owned base training blobs from experiment 016; these initialize the generic previous-byte baseline only",
    "baseline": "byte-identical previous-byte baseline from 016",
    "candidate_statistics": "byte-identical four-byte candidate statistics, occurrence>=12, consistency>=0.60",
    "independent_adaptation": "same per-domain base-plus-own-cue development as 016",
    "pooled_control": "same cumulative pooled phenotype construction as 016",
    "minimax_ranking": "descending minimum cue-side incremental-correct contribution across seen domains, then descending summed contribution, then raw-key order",
    "local_assignment": "016 deterministic feasibility-preserving radius-two matching",
    "active_selector": "same per-domain cue-side contribution selector",
    "record_format": "same six-byte retained record"
  },
  "capacity": {
    "total_structures": 16,
    "active_structures": 7,
    "retained_structures": 9,
    "capacity_growth": false,
    "radius": 2
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
      "valid_stage_count",
      "==",
      6
    ],
    [
      "valid_seen_domain_evaluation_count",
      "==",
      12
    ],
    [
      "matched_assignment_failure_count",
      "==",
      0
    ],
    [
      "minimum_selected_motif_count",
      "==",
      16
    ],
    [
      "maximum_selected_motif_count",
      "==",
      16
    ],
    [
      "minimum_cumulative_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_cumulative_to_independent_incremental_correct_fraction",
      ">=",
      0.5
    ],
    [
      "minimum_prior_domain_incremental_correct_count",
      ">",
      0
    ],
    [
      "minimum_prior_domain_to_first_encounter_fraction",
      ">=",
      0.5
    ],
    [
      "minimum_active_retained_incremental_correct_fraction",
      ">=",
      0.5
    ],
    [
      "minimum_primary_active_structure_count",
      "==",
      7
    ],
    [
      "maximum_primary_active_structure_count",
      "==",
      7
    ],
    [
      "minimum_primary_retained_structure_count",
      "==",
      9
    ],
    [
      "maximum_primary_retained_structure_count",
      "==",
      9
    ],
    [
      "retained_record_integrity_mismatch_count",
      "==",
      0
    ],
    [
      "state_partition_mismatch_count",
      "==",
      0
    ],
    [
      "capacity_growth_event_count",
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
  "validity_criteria": [
    "Exact parent, North Star, ckb-plane authority lineage, manifest identity, source SHA-256 values, and source byte counts match.",
    "Execution occurs only on GitHub-hosted compute after ckb-plane READY_RESEARCH for this exact preregistration SHA.",
    "The three external sources are fetched from the frozen manifest URIs and verified before use, then discarded with the hosted runner.",
    "All heldout evaluation bytes are isolated from adaptation/consolidation/activation decisions.",
    "The repo-owned base blobs are unchanged and serve only the frozen generic baseline initialization.",
    "Experiment 016 candidate, minimax ranking, radius-two matching, sixteen-cell capacity, seven-active/nine-retained partition, and record semantics are reused without tuning.",
    "No tokenizer, external model, persistent corpus, capacity growth, production authority, or LINKDEADKB execution occurs.",
    "Both encounter orders complete and all metrics are finite."
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass.",
    "mixed": "Validity passes and all domains remain positive, but at least one 0.50 retention or partition-performance threshold fails.",
    "negative": "Validity passes but any seen external domain becomes nonpositive or fixed-capacity consolidation loses the majority of independent or prior-domain benefit.",
    "incomplete": "Authority, network, source retrieval, or compute interruption prevents the frozen matrix.",
    "invalid": "Any authority, identity, contamination, mechanism drift, capacity, partition, host-isolation, or determinism criterion fails."
  },
  "no_post_result_tuning_rule": "Do not alter sources, split, orders, base corpus, candidate rules, minimax scoring, matching, cell capacity, active/retained ceiling, metrics, thresholds, authority requirements, or classification after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-raw-cumulative-consolidation-017.ice",
    "research/applications/plane/exp-dgr-external-raw-cumulative-consolidation-017.py",
    ".github/workflows/external-raw-cumulative-consolidation-017.yml"
  ]
}