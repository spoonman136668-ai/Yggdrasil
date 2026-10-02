{
  "experiment_id": "EXP-DGR6-LANGUAGE-HIERARCHY-MAINTENANCE-001",
  "question": "Can the qualified Yggdrasil maintenance substrate preserve and repeatedly regenerate the exact functional 16-structure Wingless WBG-5 language-like hierarchy after selective multi-level lesions using only bounded retained developmental records, while preserving untouched language structures?",
  "hypothesis": "Across six disjoint seeds and three frozen lesion/regeneration cycles, deleting two level-1 motifs, one level-2 compound, and one reference profile per cycle will reduce only the corresponding target assays, while regeneration from bounded retained records restores exact structure identity and >=0.99 affected-function accuracy in four repair operations per cycle with zero untouched-structure mutation, erased/shuffled controls <=0.25, and repair-to-cold operation ratio <=0.01.",
  "exact_parent_sha": "5f916d7cde73625af42c477f2a3c71858fc2ffd0",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "cross_project_evidence": {
    "repo": "spoonman136668-ai/Wingless",
    "experiment": "WLM-LM-MULTISCALE-NATIVE-LANGUAGE-PRECURSOR-R2",
    "qualified_head_sha": "14c6b2eb50463fb574c8d47ceda4eac94974583d",
    "qualification_run_id": "36999394724",
    "evidence_commit": "ed15e0df2e1f70f3c3e690bd8567a982dfb9a2b3",
    "classification_commit": "fa272d061773003720afc3cd74e3a954246b062a"
  },
  "authority": "synthetic computational cross-project bridge only; no production/deployment/external-model authority",
  "hierarchy": {
    "physical_cell_count": 16,
    "structures": [
      "8 level-1 motif structures: 4-byte key + 1-byte successor",
      "4 level-2 compound structures: two 1-byte level-1 structure references",
      "4 reference profile structures: frozen first-role and second-role binary contribution state"
    ],
    "structure_cell_mapping": "level1 cells 0..7, level2 cells 8..11, reference-profile cells 12..15",
    "capacity_growth": false
  },
  "retained_records": {
    "level1": "cell index + 4 key bytes + successor = 6 bytes",
    "level2": "cell index + two level1 references = 3 bytes",
    "reference_profile": "cell index + first-role bit + second-role bit = 3 bytes",
    "lesion_record_bytes_per_cycle": "2*6 + 3 + 3 = 18 bytes",
    "hidden_extra_state_forbidden": true
  },
  "lesion_schedule": {
    "cycles": 3,
    "cycle0": {
      "level1": [
        0,
        4
      ],
      "level2": [
        0
      ],
      "reference": [
        0
      ]
    },
    "cycle1": {
      "level1": [
        1,
        5
      ],
      "level2": [
        1
      ],
      "reference": [
        1
      ]
    },
    "cycle2": {
      "level1": [
        2,
        6
      ],
      "level2": [
        2
      ],
      "reference": [
        2
      ]
    },
    "rule": "retained records are captured before lesion; affected cells are then zeroed; untouched cells remain byte-identical"
  },
  "assays": {
    "pre_lesion": "all eight local motif successors + all four compound identities + all four long-range reference role profiles",
    "post_lesion": "affected local/compound/reference assays plus untouched assays separately",
    "post_regeneration": "same full assay after exactly four retained-record repair operations",
    "erased_control": "same four cell lesions with all retained record bytes zeroed",
    "shuffled_control": "same retained record bytes deterministically permuted among the four lesioned receiver cells"
  },
  "cost_accounting": {
    "repair_operations_per_cycle": 4,
    "repair_read_bytes_per_cycle": 18,
    "cold_redevelopment_operations": "reuse WBG-5 frozen 4096 lexicon training records + 3072 grammar records as 7168 development operations",
    "target_ratio": "4/7168"
  },
  "seeds": [
    150001,
    150011,
    150019,
    150029,
    150041,
    150053
  ],
  "metrics_and_thresholds": [
    [
      "valid_seed_count",
      "==",
      6
    ],
    [
      "completed_cycle_count",
      "==",
      18
    ],
    [
      "minimum_pre_lesion_full_accuracy",
      ">=",
      0.99
    ],
    [
      "maximum_post_lesion_affected_accuracy",
      "<=",
      0.25
    ],
    [
      "minimum_post_lesion_untouched_accuracy",
      ">=",
      0.99
    ],
    [
      "minimum_post_regeneration_affected_accuracy",
      ">=",
      0.99
    ],
    [
      "minimum_post_regeneration_untouched_accuracy",
      ">=",
      0.99
    ],
    [
      "maximum_untouched_structure_mutation_count",
      "==",
      0
    ],
    [
      "minimum_structure_identity_jaccard_pre_vs_regenerated",
      "==",
      1
    ],
    [
      "maximum_repair_read_bytes_per_cycle",
      "==",
      18
    ],
    [
      "maximum_repair_operations_per_cycle",
      "==",
      4
    ],
    [
      "maximum_repair_to_cold_operation_ratio",
      "<=",
      0.01
    ],
    [
      "maximum_erased_control_affected_accuracy",
      "<=",
      0.25
    ],
    [
      "maximum_shuffled_control_affected_accuracy",
      "<=",
      0.25
    ],
    [
      "maximum_final_physical_cell_count",
      "==",
      16
    ],
    [
      "minimum_final_physical_cell_count",
      "==",
      16
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "invalid_repair_rows",
      "==",
      0
    ]
  ],
  "classification_rules": {
    "supported": "All frozen thresholds and validity criteria pass across all three cycles and six seeds.",
    "mixed": "Regeneration restores target function but at least one collateral, exact-identity, cost, or control threshold fails.",
    "negative": "Validity passes but bounded retained records do not restore language-hierarchy function materially better than erased/shuffled controls.",
    "incomplete": "Environmental or compute interruption prevents full frozen matrix.",
    "invalid": "Cross-project evidence identity, retained-state boundary, lesion isolation, deterministic construction, capacity, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "Do not alter hierarchy mapping, lesion schedule, retained-record encoding, seeds, controls, cost definitions, metrics, thresholds, or classification after output is observed."
}
