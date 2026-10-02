{
  "experiment_id": "EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-002",
  "program": "Wingless-Yggdrasil integration",
  "question": "Can Yggdrasil selectively maintain and regenerate the exact 16-structure Wingless WBG-5 raw-byte hierarchy while preserving Wingless local and long-range predictive behavior, without replacing the Wingless substrate or using an external model?",
  "hypothesis": "Across six new disjoint seeds, selectively lesioning two of four Wingless level-2 compound structures and their two corresponding reference-profile structures will collapse affected long-range prediction while preserving all level-1 local prediction and unaffected long-range prediction. Yggdrasil regeneration from bounded retained developmental records will restore exact pre-lesion structure identity and >=0.95 affected long-range accuracy in exactly four repair operations, with zero mutation of the twelve unlesioned Wingless structures. Erased and payload-shuffled repair controls will remain <=0.25 affected long-range accuracy.",
  "exact_parent_sha": "b9d8460204f784cfd4f628443ae52b9d4f2f3a68",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "wingless_source": {
    "repo": "spoonman136668-ai/Wingless",
    "classification_commit_sha": "fa272d061773003720afc3cd74e3a954246b062a",
    "experiment": "WLM-LM-MULTISCALE-NATIVE-LANGUAGE-PRECURSOR-R2",
    "qualified_head_sha": "14c6b2eb50463fb574c8d47ceda4eac94974583d",
    "qualification_run_id": "36999394724",
    "classification": "supported",
    "metrics_identity": {
      "minimum_level1_motif_recall": 1,
      "minimum_level2_compound_recall": 1,
      "minimum_local_successor_accuracy": 1,
      "minimum_long_range_reference_accuracy": 1,
      "minimum_reference_profile_coverage": 4,
      "maximum_total_learned_structure_count": 16
    }
  },
  "yggdrasil_source": {
    "classification_commit_sha": "5f916d7cde73625af42c477f2a3c71858fc2ffd0",
    "experiment": "EXP-DGR5-CROSS-DOMAIN-GRANULARITY-REORGANIZATION-002",
    "qualified_head_sha": "db8fece2e2754c9212529104199daad961da69f1",
    "classification": "supported"
  },
  "authority": "synthetic computational research only; no external-model inference, production, deployment, broker, accepted-ref, scheduler, queue, runtime, or cross-project execution authority changes",
  "changed_paths": [
    "research/experiments/exp-bridge-wingless-yggdrasil-hierarchy-maintenance-002.ice",
    "research/applications/plane/exp-bridge-wingless-yggdrasil-hierarchy-maintenance-002.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "canonical_wingless_state": {
    "structure_count": 16,
    "level1": {
      "count": 8,
      "cell_indices": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "motif_rule": "motif i=[128+i,64+((7*i) mod 32),170,85], i=0..7",
      "successor_rule": "16+13*i",
      "role": "raw-byte four-byte motif -> local successor"
    },
    "level2": {
      "count": 4,
      "cell_indices": [
        8,
        9,
        10,
        11
      ],
      "compound_rule": "compound c = motif c concatenated with motif c+4, c=0..3",
      "role": "eight-byte learned compound identity"
    },
    "reference_profiles": {
      "count": 4,
      "cell_indices": [
        12,
        13,
        14,
        15
      ],
      "profile_rule": "profile c stores high-role bit c mod 2 and low-role bit c mod 2",
      "prediction_rule": "reference byte=224+(profile[A].high<<1)+profile[B].low",
      "role": "factorized first/second compound reference contribution"
    },
    "state_identity_rule": "The above structure definitions are the canonical learned structures whose full recall/profile coverage were established by the sealed WBG-5 classification; evaluator definitions are frozen before this bridge experiment and may not be altered after output."
  },
  "yggdrasil_mapping": {
    "physical_cell_count": 16,
    "mapping": "Wingless structure index equals Yggdrasil physical cell index for this bridge assay",
    "permitted_operations": [
      "LESION",
      "RETAIN",
      "REGENERATE"
    ],
    "forbidden_operations": [
      "REPLICATE",
      "MERGE",
      "capacity growth",
      "structure substitution",
      "external inference"
    ],
    "unlesioned_mutation_forbidden": true
  },
  "lesion": {
    "selection": "For each seed let p=(seed//2) mod 4. Lesion level-2 compound structures p and (p+2) mod 4 plus reference-profile structures for the same two compound IDs; exactly four structures are removed.",
    "retained_records": {
      "level2": "10 bytes = receiver index, type byte 2, then eight-byte compound key",
      "reference_profile": "4 bytes = receiver index, type byte 3, high-role bit, low-role bit"
    },
    "retained_read_budget_bytes": 28,
    "repair_operation_budget": 4
  },
  "evaluation_grammar": {
    "seeds": [
      150001,
      151007,
      152017,
      153019,
      154021,
      155027
    ],
    "seed_policy": "All six seeds were checked against both Wingless and Yggdrasil repositories before preregistration and had no matches. No replacement, exclusion, or extension is permitted.",
    "records_per_seed": 2048,
    "exact_pairs": "all sixteen ordered compound-A/compound-B pairs, balanced exactly 128 times each",
    "record_shape": "compound A (8 raw bytes) + twelve filler bytes + compound B (8 raw bytes) + reference byte + three filler bytes = 32 raw bytes",
    "filler": "deterministic seed/record LCG mapped into 192..255",
    "affected_record_definition": "a record is affected iff compound A or compound B is one of the two lesioned compound IDs",
    "unaffected_record_definition": "neither compound belongs to the lesioned set",
    "local_level1_assay": "independent balanced raw motif stream over all eight level-1 motifs; local successor accuracy is scored before lesion, after lesion, and after regeneration"
  },
  "prediction_semantics": {
    "level1": "exact active level-1 motif key predicts stored successor; level-1 cells are never lesioned",
    "level2_recognition": "exact active eight-byte compound key identifies compound ID; missing compound structure means the compound is unrecognized",
    "reference": "only recognized A/B compounds with active corresponding reference profiles may emit factorized reference prediction; otherwise default byte 224",
    "no_hidden_shortcut": "Prediction may not use evaluator compound IDs, lesion IDs, or frozen formula except through active structure records.",
    "missing_higher_level_output": "If either compound or either reference profile needed for a long-range prediction is absent, emit abstention byte 255. Valid reference targets are only 224..227, so abstention is always scored incorrect."
  },
  "controls": {
    "erased": "after lesion attempt repair with no retained records",
    "shuffled": "Construct a type-preserving wrong-payload repair: cyclically swap the two retained level-2 compound payloads between their receiver records, and independently swap the two retained reference-profile payloads between their receiver records. Receiver index and type byte remain fixed. No cross-type or cross-length rotation is permitted.",
    "cold_redevelopment_reference": "32768 raw-byte update operations is the frozen comparison cost inherited from qualified Yggdrasil developmental-granularity assays; it is comparison-only and grants no extra training"
  },
  "metrics_and_thresholds": [
    [
      "valid_seed_count",
      "==",
      6
    ],
    [
      "minimum_pre_lesion_local_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_pre_lesion_long_range_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_lesion_local_accuracy",
      ">=",
      0.95
    ],
    [
      "maximum_post_lesion_affected_long_range_accuracy",
      "<=",
      0.25
    ],
    [
      "minimum_post_lesion_unaffected_long_range_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_regeneration_local_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_regeneration_affected_long_range_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_post_regeneration_unaffected_long_range_accuracy",
      ">=",
      0.95
    ],
    [
      "minimum_structure_jaccard_pre_vs_regenerated",
      "==",
      1
    ],
    [
      "maximum_unlesioned_structure_mutation_count",
      "==",
      0
    ],
    [
      "maximum_repair_read_bytes",
      "<=",
      28
    ],
    [
      "minimum_repair_read_bytes",
      "==",
      28
    ],
    [
      "maximum_repair_operations",
      "==",
      4
    ],
    [
      "maximum_repair_to_cold_operation_ratio",
      "<=",
      0.001
    ],
    [
      "maximum_erased_control_affected_long_range_accuracy",
      "<=",
      0.25
    ],
    [
      "maximum_shuffled_control_affected_long_range_accuracy",
      "<=",
      0.25
    ],
    [
      "maximum_final_structure_count",
      "==",
      16
    ],
    [
      "minimum_final_structure_count",
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
  "validity_criteria": [
    "Exact Yggdrasil parent SHA, both North-Star/source identities, sealed Wingless/Yggdrasil evidence identities, and invalid-R1 supersession match this preregistration.",
    "The canonical 16-structure state matches the frozen WBG-5 structure definitions and contains exactly 8 level-1, 4 level-2, and 4 reference-profile structures.",
    "Exactly four structures are lesioned per seed: two level-2 compounds plus their two corresponding profiles; no level-1 structure is lesioned.",
    "All sixteen compound pairs are balanced in evaluation and affected/unaffected strata are computed only by evaluator after prediction.",
    "Prediction uses only active structure records and raw bytes; evaluator compound IDs/lesion IDs are not exposed to prediction.",
    "Missing higher-level structure emits abstention byte 255 and cannot accidentally match a valid reference target.",
    "Repair reads exactly the four retained records for lesioned structures, never any unlesioned structure payload.",
    "Unlesioned structure records are byte-identical before and after repair.",
    "Erased control has no retained records. Shuffled control swaps payloads only within the two same-type retained record pairs, preserving receiver/type/record length.",
    "Physical/learned structure count remains sixteen after valid regeneration and no capacity growth occurs.",
    "Two duplicate executions from identical inputs must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty-one frozen thresholds pass.",
    "mixed": "Validity/completeness pass and regeneration causally restores affected capability, but at least one fidelity, collateral, cost, or control threshold fails.",
    "negative": "Validity passes but repair fails to restore affected Wingless prediction or materially damages unlesioned capability.",
    "incomplete": "Environmental or compute stop prevents the frozen matrix.",
    "invalid": "Source identity, structure identity, lesion construction, control isolation, fixed capacity, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "After any output is observed, do not alter source identities, structure definitions, mapping, seeds, lesion selection, retained encoding, repair rule, evaluation grammar, controls, metrics, thresholds, aggregation, or classification.",
  "supersedes_invalid_attempt": {
    "experiment": "EXP-BRIDGE-WINGLESS-YGGDRASIL-HIERARCHY-MAINTENANCE-001",
    "disposition": "invalid-preregistration-before-execution",
    "scientific_claim": false
  }
}
