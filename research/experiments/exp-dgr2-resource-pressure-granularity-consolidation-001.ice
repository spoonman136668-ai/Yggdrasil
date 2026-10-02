{
  "experiment_id": "EXP-DGR2-RESOURCE-PRESSURE-GRANULARITY-CONSOLIDATION-001",
  "proposal_parent": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "proposal_stage": "DGR-2",
  "question": "Under a fixed four-active-structure resource ceiling, can the qualified Yggdrasil DGR-1 phenotype locally merge eight specialized raw-byte motif cells into four compact higher-span structures while preserving held-out capability and approaching a hand-specified static-chunk resource footprint?",
  "hypothesis": "Replaying the exact qualified DGR-1 developmental process on the same paired seeds, a bounded radius-two MERGE rule will form exactly four two-motif structures by discovering their common two-byte suffix, preserve at least 0.95 held-out successor accuracy, reduce active specialized structures by at least 50%, reduce logical motif-state bytes by at least 15%, remain within 2 percentage points of both no-merge and static-chunk accuracy, and use no more logical motif-state bytes than the static-chunk baseline.",
  "exact_parent_sha": "802225b2be118395752ca63f85239aee813dd73e",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR1-DEVELOPMENTAL-BYTE-MOTIF-SPECIALIZATION-001",
    "classification": "supported",
    "result_sha256": "61b32638eb4dea49baaf0a9459e884abf4aae3f328947cf099e8057d93ffae7b",
    "scientific_claim": "The fixed 16-cell ring differentiated all eight predictive raw-byte motifs with causal, reproducible held-out function."
  },
  "authority": "synthetic computational research only; no wetware, production, live, accepted-ref, scheduler, queue-consumer, deployment, or external-model inference authority",
  "changed_paths": [
    "research/experiments/exp-dgr2-resource-pressure-granularity-consolidation-001.ice",
    "research/applications/plane/exp-dgr2-resource-pressure-granularity-consolidation-001.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "compositional_reuse": {
    "seeds": [
      130003,
      131009,
      132017,
      133027,
      134033,
      135043
    ],
    "seed_reuse_reason": "Paired compositional qualification from the exact DGR-1 phenotype; no fresh learning claim is made.",
    "frozen_dgr1_reuse": [
      "16-cell fixed ring",
      "raw byte corpus",
      "motif schedule",
      "filler generator",
      "candidate ownership hash",
      "DIFFERENTIATE threshold and consistency rule",
      "radius-two differentiation",
      "held-out evaluation corpus"
    ]
  },
  "pressure_and_merge": {
    "active_specialized_structure_ceiling": 4,
    "permitted_new_operation": "MERGE",
    "merge_radius": 2,
    "merge_candidate_rule": "Two still-active specialized cells may merge only if ring distance <=2 and their learned four-byte motif keys have an identical final two-byte suffix.",
    "merge_order": "ascending receiver cell index; for each unmerged receiver choose nearest compatible unmerged neighbor, ties by lower cell index",
    "compact_representation": "one shared two-byte suffix plus, for each of two motifs, a two-byte prefix and one learned successor byte",
    "logical_bytes_per_unmerged_motif": 5,
    "logical_bytes_per_two_motif_merge": 8,
    "donor_after_merge": "generic/inactive motif role; total physical cell count remains 16",
    "capacity_growth": false
  },
  "comparison_arms": {
    "no_merge": "qualified DGR-1 phenotype remains at eight specialized cells; each motif stores four key bytes plus one successor byte",
    "developmental_merge": "apply only the frozen local MERGE rule until no additional merge is possible or four active motif structures remain",
    "static_chunk": "hand-specified evaluator baseline pairs the same eight true motifs into four two-motif structures using the same compact encoding; it is a comparator, not deployed substrate capability"
  },
  "resource_accounting": {
    "no_merge_expected_active_structures": 8,
    "no_merge_expected_logical_motif_bytes": 40,
    "developmental_expected_active_structures": 4,
    "developmental_expected_logical_motif_bytes": 32,
    "static_expected_active_structures": 4,
    "static_expected_logical_motif_bytes": 32,
    "physical_cell_count": 16,
    "topology": "unchanged fixed ring"
  },
  "metrics_and_thresholds": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 6
    },
    {
      "name": "minimum_developmental_merge_heldout_accuracy",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "minimum_no_merge_heldout_accuracy",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "minimum_static_chunk_heldout_accuracy",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "maximum_developmental_accuracy_loss_vs_no_merge",
      "comparator": "<=",
      "threshold": 0.02
    },
    {
      "name": "maximum_developmental_accuracy_gap_vs_static",
      "comparator": "<=",
      "threshold": 0.02
    },
    {
      "name": "maximum_developmental_active_structure_count",
      "comparator": "<=",
      "threshold": 4
    },
    {
      "name": "minimum_developmental_merge_count",
      "comparator": ">=",
      "threshold": 4
    },
    {
      "name": "maximum_developmental_active_structure_ratio_vs_no_merge",
      "comparator": "<=",
      "threshold": 0.5
    },
    {
      "name": "maximum_developmental_logical_motif_bytes",
      "comparator": "<=",
      "threshold": 34
    },
    {
      "name": "maximum_developmental_resident_bytes_ratio_vs_no_merge",
      "comparator": "<=",
      "threshold": 0.85
    },
    {
      "name": "maximum_developmental_over_static_resident_bytes_ratio",
      "comparator": "<=",
      "threshold": 1
    },
    {
      "name": "minimum_pairwise_merge_structure_jaccard",
      "comparator": ">=",
      "threshold": 0.75
    },
    {
      "name": "maximum_final_physical_cell_count",
      "comparator": "==",
      "threshold": 16
    },
    {
      "name": "minimum_final_physical_cell_count",
      "comparator": "==",
      "threshold": 16
    },
    {
      "name": "merge_radius_violation_count",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "capacity_growth_event_count",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "invalid_merge_rows",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "validity_criteria": [
    "Exact parent SHA, North Star identity, DGR-1 sealed evidence identity, and proposal-stage identity match.",
    "The DGR-1 phenotype is reproduced from the exact frozen developmental/corpus rules before pressure is applied; all eight true motifs must be specialized before an arm is evaluated.",
    "No-merge, developmental-merge, and static-chunk arms begin from equivalent eight-motif capability.",
    "Developmental MERGE may inspect only the two candidate cells' learned motif keys, learned successors, ring positions, and common-suffix relation; hidden motif IDs are unavailable.",
    "No developmental merge spans ring distance greater than two.",
    "Total physical cell count remains exactly sixteen and no replication/capacity growth occurs.",
    "Static-chunk baseline is evaluator-specified and cannot influence developmental merge choices.",
    "Logical motif-state bytes are computed from frozen representation formulas, not Python object size.",
    "The source emits yggdrasil.research-scientific-result.v1 with the exact experiment identifier and finite metrics.",
    "Two duplicate executions from identical inputs must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all eighteen frozen thresholds pass.",
    "mixed": "Capability is preserved and developmental consolidation reduces active structures, but at least one resident-byte, reproducibility, or static-baseline parity threshold fails.",
    "null": "Validity passes but developmental active-structure ratio remains above 0.75 with no material resident-byte reduction.",
    "negative": "Validity passes but consolidation materially harms capability or cannot meet the four-structure ceiling.",
    "incomplete": "Environmental or compute stop prevents complete deterministic evaluation.",
    "invalid": "Provenance, DGR-1 reproduction, local-merge isolation, fixed-capacity, resource-accounting, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "After any output is observed, do not alter seeds, DGR-1 replay, pressure ceiling, merge radius, compatibility rule, compact encoding, arm definitions, resource formulas, metrics, thresholds, aggregation, or classification."
}
