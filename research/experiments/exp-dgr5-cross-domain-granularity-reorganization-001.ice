{
  "experiment_id": "EXP-DGR5-CROSS-DOMAIN-GRANULARITY-REORGANIZATION-001",
  "proposal_parent": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "proposal_stage": "DGR-5",
  "question": "Can the qualified developmental granularity substrate preserve and reuse shared low-level raw-byte specializations while reorganizing bounded higher-span structures for a sealed fourth synthetic domain under one fixed 16-cell resource ceiling?",
  "hypothesis": "Across six disjoint seeds, sequential exposure to three source domains followed by a sealed fourth domain will reuse all four shared motif specializations, require at most two target-specific new motif specializations and at most one higher-span structural reorganization, reach at least 0.95 target accuracy, preserve at least 0.95 source accuracy, keep resident logical state growth at or below 20%, and recover target capability after hibernation/reactivation at no more than 1% of cold redevelopment cost.",
  "exact_parent_sha": "3d31cdd10fc2edf9f24b7e89edec90fbfc041217",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR4-GRANULARITY-LESION-REGENERATION-001",
    "classification": "supported",
    "qualification_run_id": "36998343570",
    "result_sha256": "d7ca3556436e78466037de6078f11d4ca06fb7d53c0463b6e36ed25ca2e84ee8"
  },
  "authority": "synthetic computational research only",
  "substrate": {
    "physical_cell_count": 16,
    "shared_low_level_motif_count": 4,
    "domain_specific_motif_count": 2,
    "merged_higher_span_capacity": 4,
    "capacity_growth": false,
    "allowed_operations": [
      "DIFFERENTIATE",
      "MERGE",
      "HIBERNATE",
      "WAKE"
    ],
    "forbidden_operations": [
      "REPLICATE",
      "external model inference"
    ],
    "reuse": "DGR-1 local differentiation, DGR-2 merge, DGR-3 retained wake records, DGR-4 selective preservation rules"
  },
  "domains": {
    "names": [
      "prose-like",
      "code-like",
      "structured-data-like",
      "binary-like"
    ],
    "source_ids": [
      0,
      1,
      2
    ],
    "heldout_id": 3,
    "shared_motifs": "four byte-identical motifs and successors across domains",
    "domain_specific": "two unique motifs per domain",
    "learner_visibility": "concatenated raw bytes only; domain labels and boundaries evaluator-only"
  },
  "corpora": {
    "seeds": [
      136001,
      136013,
      136027,
      136033,
      136043,
      136057
    ],
    "source_training_records_per_domain": 3072,
    "target_adaptation_records": 768,
    "evaluation_records_per_domain": 768
  },
  "metrics_and_thresholds": [
    [
      "valid_seed_count",
      "==",
      6
    ],
    [
      "minimum_shared_motif_reuse_count",
      ">=",
      4
    ],
    [
      "maximum_target_new_motif_specialization_count",
      "<=",
      2
    ],
    [
      "maximum_target_higher_span_reorganization_count",
      "<=",
      1
    ],
    [
      "minimum_target_heldout_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_adaptation_source_accuracy",
      ">=",
      0.95
    ],
    [
      "maximum_source_accuracy_loss",
      "<=",
      0.05
    ],
    [
      "maximum_resident_logical_state_growth_ratio",
      "<=",
      0.2
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
      "maximum_reactivation_to_cold_operation_ratio",
      "<=",
      0.01
    ],
    [
      "minimum_post_reactivation_target_accuracy",
      ">=",
      0.95
    ],
    [
      "capacity_growth_event_count",
      "==",
      0
    ],
    [
      "invalid_reorganization_rows",
      "==",
      0
    ]
  ],
  "validity_criteria": [
    "Exact parent, North Star, and DGR-4 evidence identities match.",
    "All six seeds and four domains complete frozen cardinalities.",
    "Domain labels and boundaries are not visible to developmental updates.",
    "Shared motifs are byte/successor identical; each domain has exactly two unique motifs.",
    "No physical cell growth occurs.",
    "Target adaptation may reorganize only within the preallocated developmental substrate.",
    "Source retention is evaluated without source rehearsal after target adaptation.",
    "Hibernation/reactivation uses the existing bounded retained-record mechanism.",
    "Two duplicate executions must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All frozen thresholds and validity criteria pass.",
    "mixed": "Cross-domain reuse and target adaptation are demonstrated but at least one retention, state-growth, reorganization, or wake threshold fails.",
    "null": "Validity passes but target accuracy remains below 0.25 and shared reuse is below two motifs.",
    "negative": "Validity passes but adaptation materially overwrites source capability or approaches fresh redevelopment/state growth.",
    "incomplete": "Environmental or compute interruption prevents frozen cardinality.",
    "invalid": "Provenance, domain isolation, fixed-capacity, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "Do not alter seeds, domains, motif definitions, resource ceiling, developmental operations, controls, metrics, thresholds, aggregation, or classification after output is observed."
}
