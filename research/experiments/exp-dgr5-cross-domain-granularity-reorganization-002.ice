{
  "experiment_id": "EXP-DGR5-CROSS-DOMAIN-GRANULARITY-REORGANIZATION-002",
  "proposal_parent": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "proposal_stage": "DGR-5",
  "question": "Can one fixed 16-cell Yggdrasil substrate preserve four shared low-level raw-byte structures while sequentially differentiating, hibernating, and cue-reactivating domain-specific structures across four disjoint domains under a six-active-structure ceiling?",
  "hypothesis": "Across six disjoint seeds, four shared motif cells remain byte-identical through all domains, exactly two domain-specific cells differentiate on each first exposure, outgoing domain-specific cells hibernate so active specialized structure count never exceeds six, and raw-byte cue streams later reactivate exactly the correct two structures in two wake operations with >=0.95 revisited-domain accuracy, >=0.95 prior-domain retained capability, zero shared-cell mutation, and wake cost <=1% of first-exposure development cost.",
  "exact_parent_sha": "6e34cfc23dc3f56502155165041bca9ba06a63dd",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR4-GRANULARITY-LESION-REGENERATION-001",
    "classification": "supported",
    "result_sha256": "d7ca3556436e78466037de6078f11d4ca06fb7d53c0463b6e36ed25ca2e84ee8"
  },
  "supersedes_invalid_attempt": {
    "experiment": "EXP-DGR5-CROSS-DOMAIN-GRANULARITY-REORGANIZATION-001",
    "disposition": "invalid-provenance-before-execution",
    "scientific_claim": false
  },
  "authority": "synthetic computational research only",
  "changed_paths": [
    "research/experiments/exp-dgr5-cross-domain-granularity-reorganization-002.ice",
    "research/applications/plane/exp-dgr5-cross-domain-granularity-reorganization-002.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "domains": {
    "names": [
      "prose-like",
      "code-like",
      "structured-data-like",
      "binary-like"
    ],
    "shared_motifs": [
      [
        128,
        64,
        170,
        85
      ],
      [
        129,
        71,
        170,
        85
      ],
      [
        130,
        78,
        170,
        85
      ],
      [
        131,
        85,
        170,
        85
      ]
    ],
    "shared_successors": [
      16,
      29,
      42,
      55
    ],
    "domain_unique_motifs": {
      "0": [
        [
          41,
          96,
          204,
          51
        ],
        [
          42,
          99,
          204,
          51
        ]
      ],
      "1": [
        [
          34,
          101,
          204,
          51
        ],
        [
          35,
          104,
          204,
          51
        ]
      ],
      "2": [
        [
          43,
          106,
          204,
          51
        ],
        [
          44,
          109,
          204,
          51
        ]
      ],
      "3": [
        [
          36,
          111,
          204,
          51
        ],
        [
          37,
          114,
          204,
          51
        ]
      ]
    },
    "unique_successors": {
      "0": [
        128,
        131
      ],
      "1": [
        136,
        139
      ],
      "2": [
        144,
        147
      ],
      "3": [
        152,
        155
      ]
    },
    "frozen_home_cells": {
      "shared": [
        13,
        3,
        9,
        15
      ],
      "domain0": [
        0,
        2
      ],
      "domain1": [
        4,
        6
      ],
      "domain2": [
        8,
        10
      ],
      "domain3": [
        12,
        14
      ]
    },
    "collision_control": "All twelve motif home cells are distinct under the frozen DGR-1 home hash."
  },
  "substrate": {
    "physical_cell_count": 16,
    "topology": "fixed ring",
    "local_radius": 2,
    "active_specialized_structure_ceiling": 6,
    "persistent_shared_structure_count": 4,
    "current_domain_unique_active_count": 2,
    "operations": [
      "DIFFERENTIATE",
      "HIBERNATE",
      "WAKE"
    ],
    "forbidden": [
      "REPLICATE",
      "MERGE",
      "PRUNE",
      "REPAIR",
      "capacity growth"
    ],
    "raw_input": "identity uint8 stream; no tokenizer, domain marker, segmentation label, motif ID, or external embedding"
  },
  "sequence": {
    "first_pass": [
      0,
      1,
      2,
      3
    ],
    "revisit_pass": [
      0,
      1,
      2,
      3
    ],
    "first_exposure_training_records_per_domain": 2048,
    "heldout_evaluation_records_per_domain": 1024,
    "revisit_cue_records_per_domain": 16,
    "schedule": "Every six-record block contains all four shared plus both current-domain unique motifs exactly once.",
    "transition": "Before a new domain, hibernate the outgoing two unique structures to fixed 6-byte records; four shared structures remain active.",
    "first_exposure": "Develop only motifs not already active or retained.",
    "revisit": "Use only raw-byte cue keys; a retained structure wakes iff its exact four-byte key appears in the 16-record cue stream."
  },
  "retention": {
    "per_unique_record": "1 receiver-index byte + 4 motif-key bytes + 1 successor byte = 6 logical bytes",
    "per_domain_unique_retained_bytes": 12,
    "maximum_total_hibernated_unique_bytes": 48,
    "domain_identity_storage": "none"
  },
  "seeds": [
    140009,
    141011,
    142019,
    143021,
    144037,
    145043
  ],
  "seed_policy": "All six seeds were checked against the Yggdrasil repository before preregistration and had no matches.",
  "metrics_and_thresholds": [
    [
      "valid_seed_count",
      "==",
      6
    ],
    [
      "minimum_shared_motif_reuse_count",
      "==",
      4
    ],
    [
      "maximum_shared_structure_mutation_count",
      "==",
      0
    ],
    [
      "minimum_first_exposure_unique_specialization_count_per_domain",
      "==",
      2
    ],
    [
      "maximum_first_exposure_unique_specialization_count_per_domain",
      "==",
      2
    ],
    [
      "minimum_first_exposure_domain_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_revisit_domain_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_prior_domain_retained_accuracy",
      ">=",
      0.95
    ],
    [
      "maximum_active_specialized_structure_count",
      "<=",
      6
    ],
    [
      "maximum_total_hibernated_unique_bytes",
      "<=",
      48
    ],
    [
      "minimum_revisit_wake_count",
      "==",
      2
    ],
    [
      "maximum_revisit_wake_count",
      "==",
      2
    ],
    [
      "minimum_revisit_cue_precision",
      ">=",
      1
    ],
    [
      "minimum_revisit_cue_recall",
      ">=",
      1
    ],
    [
      "maximum_wake_to_first_exposure_operation_ratio",
      "<=",
      0.01
    ],
    [
      "minimum_final_known_motif_count",
      "==",
      12
    ],
    [
      "maximum_final_known_motif_count",
      "==",
      12
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
      "local_radius_violation_count",
      "==",
      0
    ],
    [
      "invalid_transition_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent SHA, North Star identity, and sealed DGR-4 evidence identity match.",
    "All twelve frozen motif keys map to the preregistered distinct home cells before execution.",
    "No domain ID, motif ID, record boundary, or evaluator target label is visible to development, hibernation, cue matching, or wake.",
    "Shared motif structures learned on domain 0 remain active and byte-identical through every transition.",
    "At most two current-domain unique structures may be active in addition to the four shared structures.",
    "Outgoing unique structures hibernate to exactly two fixed 6-byte records; no hidden domain tag is stored.",
    "Revisit wake decisions use only exact raw-byte motif keys observed in the cue stream.",
    "No source-domain rehearsal occurs during another domain's first exposure or revisit.",
    "Physical cell count remains sixteen with no replication/capacity growth.",
    "Two duplicate executions from identical inputs must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all frozen thresholds pass.",
    "mixed": "Shared structures remain stable and cue-based reactivation works, but at least one retention, cost, or domain-accuracy threshold fails.",
    "negative": "Validity passes but sequential domains overwrite shared capability, require capacity growth, or cannot reactivate prior domain-specific structures.",
    "incomplete": "Environmental or compute stop prevents complete deterministic sequence.",
    "invalid": "Provenance, home-cell identity, domain-label isolation, active-ceiling, retention-boundary, fixed-capacity, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "Do not alter seeds, motif keys, home cells, domain order, corpus sizes, active ceiling, retention encoding, cue length, wake rule, controls, metrics, thresholds, aggregation, or classification after output is observed."
}
