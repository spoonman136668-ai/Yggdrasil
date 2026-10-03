{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-STATE-COMPATIBILITY-ATTRIBUTION-063",
  "program": "Yggdrasil causal attribution of context-specific frozen coalition rows",
  "question": "Is the valid 062 transfer failure caused specifically by the two context-specific rows completing the shared five-row prose coalition, rather than by exact-state preservation itself?",
  "hypothesis": "062 exposed two deterministic guard families. The failing A+C-history schedules use shared5 plus AC-specific rows [32,110,111,116] and [61,61,61,61]; the successful B+C-history schedules use the same shared5 plus BC-specific rows [97,116,105,111] and [10,32,32,32]. Freeze all six 7-row guards formed by shared5 plus every 2-of-4 pair from these four context-specific keys. On only the two preregistered failing schedules A-C-B and C-A-B, replay the exact 062 data, state construction, required-union injection, packet budget, scoring and 16/7/9 capacity. Rows/maps for a key are taken only from the corresponding training-only historical A+C or B+C donor state; no evaluation labels select donors or variants. Supported requires the original AC pair to reproduce failure in both schedules and at least one variant containing a BC-specific row to restore full success in both schedules with positive prose and partner collateral, zero capacity growth, and zero invalid rows. This is attribution only; no variant is retained.",
  "exact_parent_sha": "f612fba96a5234360b54fc4ffc21eaf0efef3c1c",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-collateral-state-compatibility-attribution-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-COALITION-STATE-COMPATIBILITY-062",
    "github_run_id": 37162357061,
    "classification": "negative",
    "validity_pass": true,
    "observation": {
      "baseline_mean_first_success_packet": 3,
      "candidate_mean_first_success_packet": 7,
      "candidate_mean_packet_reduction": -4,
      "candidate_positive_prose_collateral_schedule_count": 2,
      "candidate_reserved_key_missing_count": 0,
      "candidate_required_union_over_capacity_count": 0,
      "failing_schedules": [
        "A-C-B",
        "C-A-B"
      ],
      "successful_schedules": [
        "B-C-A",
        "C-B-A"
      ]
    },
    "guard_difference": {
      "shared5": [
        [
          118,
          101,
          108,
          111
        ],
        [
          101,
          118,
          101,
          108
        ],
        [
          100,
          101,
          118,
          101
        ],
        [
          111,
          112,
          109,
          101
        ],
        [
          32,
          32,
          32,
          32
        ]
      ],
      "ac_specific": [
        [
          32,
          110,
          111,
          116
        ],
        [
          61,
          61,
          61,
          61
        ]
      ],
      "bc_specific": [
        [
          97,
          116,
          105,
          111
        ],
        [
          10,
          32,
          32,
          32
        ]
      ]
    }
  },
  "external_transfer_manifest_sha256": "c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250",
  "external_authority": {
    "ckb_plane_main_sha": "06c3cb723820407bc2db1bd3ec9e46f462059e41",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "frozen_variants": {
    "shared5": [
      [
        118,
        101,
        108,
        111
      ],
      [
        101,
        118,
        101,
        108
      ],
      [
        100,
        101,
        118,
        101
      ],
      [
        111,
        112,
        109,
        101
      ],
      [
        32,
        32,
        32,
        32
      ]
    ],
    "context_specific_pool": [
      [
        32,
        110,
        111,
        116
      ],
      [
        61,
        61,
        61,
        61
      ],
      [
        97,
        116,
        105,
        111
      ],
      [
        10,
        32,
        32,
        32
      ]
    ],
    "variants": "all lexicographically ordered 2-of-4 combinations; exactly 6",
    "original_ac_pair": [
      [
        32,
        110,
        111,
        116
      ],
      [
        61,
        61,
        61,
        61
      ]
    ],
    "donor_rule": "each key uses its training-only row/map from the historical A+C donor if present there, otherwise from historical B+C donor; if present in both, A+C donor precedes B+C donor",
    "variant_selection_from_results": false
  },
  "frozen_reuse": {
    "schedules": [
      "A-C-B",
      "C-A-B"
    ],
    "source_manifest": "byte-identical 062",
    "split": "byte-identical 062",
    "history_rebalancing": "byte-identical 062",
    "future_packets": 12,
    "carry6_baseline": "byte-identical 062",
    "required_union_injection": "byte-identical 062",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "classification_rules": {
    "supported": "valid; original AC pair fails both target schedules; at least one frozen variant containing >=1 BC-specific row achieves full success in both target schedules with positive prose and partner collateral",
    "mixed": "valid; a BC-containing variant rescues exactly one target schedule or restores prose collateral without full success in both",
    "negative": "valid; no BC-containing variant improves the preregistered failing schedules materially",
    "invalid": "any parent, authority, source, donor identity, six-variant enumeration, heldout-selection boundary, deterministic replay, fixed capacity, provenance, or accounting requirement fails"
  },
  "no_post_result_tuning_rule": "Do not alter shared5, the four context-specific keys, six variants, donor precedence, target schedules, sources, packets, state injection, success rule, 16/7/9 capacity, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-COALITION-064",
    "intent": "preregister a training-only context gate for choosing among the causally supported coalition completions, then test it prospectively without heldout selection"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-ROW-INTERACTION-064",
    "intent": "attribute higher-order row interactions before introducing any context gate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-collateral-state-compatibility-attribution-063.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-collateral-state-compatibility-attribution-063.py",
    ".github/workflows/external-cumulative-dependent-pipeline-collateral-state-compatibility-attribution-063.yml"
  ]
}
