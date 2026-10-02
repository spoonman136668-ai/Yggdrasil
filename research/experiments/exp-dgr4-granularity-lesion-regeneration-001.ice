{
  "experiment_id": "EXP-DGR4-GRANULARITY-LESION-REGENERATION-001",
  "proposal_parent": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "proposal_stage": "DGR-4",
  "question": "Can Yggdrasil selectively regenerate only lesioned higher-span granularity structures from bounded retained developmental information while preserving intact specialized structures and capability?",
  "hypothesis": "Across the six paired DGR seeds, removing exactly two of four qualified merged structures will selectively destroy their motif capability while preserving unlesioned capability; regeneration using only the two corresponding 9-byte retained records (18 bytes total) will restore at least 0.95 lesioned-target accuracy in exactly two repair operations, preserve at least 0.99 intact-target accuracy, match the pre-lesion structure set exactly, cost at most 0.5% of cold redevelopment, and fail under erased or successor-shuffled repair records.",
  "exact_parent_sha": "ef64dde77db5a7691e54ec768fedd6e23578398b",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR3-GRANULARITY-HIBERNATE-WAKE-001",
    "classification": "supported",
    "result_sha256": "bc5a5a48292001f2b19ff1dad4894d02d06b7f885998e69504dc21ee907e1271",
    "scientific_claim": "Four merged granularity structures hibernated to zero active structures and woke from exactly 36 retained bytes in four operations with perfect repeated-cycle function."
  },
  "authority": "synthetic computational research only; no wetware, production, live, accepted-ref, scheduler, queue-consumer, deployment, or external-model inference authority",
  "changed_paths": [
    "research/experiments/exp-dgr4-granularity-lesion-regeneration-001.ice",
    "research/applications/plane/exp-dgr4-granularity-lesion-regeneration-001.py",
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
    "paired_reuse_reason": "Exact DGR-1 development, DGR-2 merge, and DGR-3 retained-record encoding are replayed; the only new manipulation is selective lesion plus selective regeneration.",
    "frozen_reuse": [
      "DGR-1 developmental phenotype",
      "DGR-2 four merged structures",
      "DGR-3 9-byte retained record per merged structure",
      "held-out evaluation corpus"
    ]
  },
  "lesion": {
    "target_structure_count": 2,
    "selection_rule": "Sort the four active merged receiver-cell indices ascending; lesion positions seed mod 2 and seed mod 2 + 2 in that sorted list.",
    "operation": "LESION sets selected merged receiver cells to generic and removes active motif data from those cells only.",
    "intact_structures": "The other two merged structures remain byte-identical and active.",
    "oracle_restriction": "Lesion selection may use receiver indices only; motif identities and held-out performance are unavailable."
  },
  "regeneration": {
    "operation": "REGENERATE",
    "readable_state": "Only the two 9-byte DGR-3 retained records corresponding to the lesioned receiver indices.",
    "readable_bytes": 18,
    "repair_operations": "exactly one reconstruction per lesioned structure",
    "expected_repair_operations": 2,
    "forbidden": [
      "training corpus access",
      "candidate tables",
      "hidden motif IDs",
      "canonical successor map",
      "rewriting intact structures",
      "replication",
      "capacity growth"
    ],
    "erased_control": "replace the two selected 9-byte repair records with zeros",
    "shuffled_control": "preserve receiver index, suffix, and prefixes in the two repair records but cyclically swap/rotate their four stored successor bytes"
  },
  "evaluation": {
    "pre_lesion": "Score all eight motifs.",
    "post_lesion": "Separately score targets mapped to lesioned structures and targets mapped to intact structures.",
    "post_regeneration": "Repeat lesion/intact-stratified scoring.",
    "structure_recovery": "Compare the set of merged motif-pair signatures before lesion and after regeneration.",
    "cold_reference": "Full DGR-1 redevelopment plus DGR-2 merge from the frozen training stream."
  },
  "metrics_and_thresholds": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 6
    },
    {
      "name": "minimum_pre_lesion_accuracy",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "maximum_post_lesion_lesioned_target_accuracy",
      "comparator": "<=",
      "threshold": 0.1
    },
    {
      "name": "minimum_post_lesion_intact_target_accuracy",
      "comparator": ">=",
      "threshold": 0.99
    },
    {
      "name": "minimum_post_regeneration_lesioned_target_accuracy",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "minimum_post_regeneration_intact_target_accuracy",
      "comparator": ">=",
      "threshold": 0.99
    },
    {
      "name": "maximum_intact_accuracy_loss_due_to_regeneration",
      "comparator": "<=",
      "threshold": 0.01
    },
    {
      "name": "minimum_structure_jaccard_pre_vs_regenerated",
      "comparator": ">=",
      "threshold": 1
    },
    {
      "name": "maximum_repair_read_bytes",
      "comparator": "==",
      "threshold": 18
    },
    {
      "name": "minimum_repair_read_bytes",
      "comparator": "==",
      "threshold": 18
    },
    {
      "name": "maximum_repair_operations",
      "comparator": "==",
      "threshold": 2
    },
    {
      "name": "minimum_cold_redevelopment_operations",
      "comparator": ">=",
      "threshold": 32768
    },
    {
      "name": "maximum_repair_to_cold_operation_ratio",
      "comparator": "<=",
      "threshold": 0.005
    },
    {
      "name": "maximum_erased_repair_lesioned_target_accuracy",
      "comparator": "<=",
      "threshold": 0.25
    },
    {
      "name": "maximum_shuffled_repair_lesioned_target_accuracy",
      "comparator": "<=",
      "threshold": 0.25
    },
    {
      "name": "maximum_intact_structure_mutation_count",
      "comparator": "==",
      "threshold": 0
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
      "name": "capacity_growth_event_count",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "invalid_repair_rows",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "validity_criteria": [
    "Exact parent SHA, North Star identity, and sealed DGR-3 evidence identity match.",
    "Each seed reproduces the exact DGR-2 four-structure phenotype and DGR-3 36-byte retained representation before lesion.",
    "Exactly two merged structures are lesioned by the frozen receiver-index selection rule.",
    "The two unlesioned structures remain byte-identical through lesion and regeneration.",
    "Regeneration reads exactly two matching 9-byte retained records and no other retained/training information.",
    "Regeneration performs exactly one reconstruction per lesioned receiver and may not rewrite intact cells.",
    "Erased and successor-shuffled controls receive no retraining or corrective oracle.",
    "Total physical cell count remains sixteen with no capacity growth.",
    "Lesioned/intact target strata are evaluator-only and unavailable to repair.",
    "The source emits yggdrasil.research-scientific-result.v1 with exact experiment identifier and finite metrics.",
    "Two duplicate executions from identical inputs must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all twenty frozen thresholds pass.",
    "mixed": "Selective regeneration restores substantial lesioned capability and preserves intact capability, but at least one exact structure, cost, or control threshold fails.",
    "null": "Validity passes but lesioned-target post-regeneration accuracy remains below 0.25 and controls are indistinguishable.",
    "negative": "Validity passes but repair damages intact capability or is not materially cheaper/effective than cold redevelopment.",
    "incomplete": "Environmental or compute stop prevents complete deterministic evaluation.",
    "invalid": "Provenance, DGR-3 replay, selective-lesion isolation, repair-state boundary, intact-state preservation, fixed-capacity, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "After any output is observed, do not alter seeds, lesion selection, lesion count, retained-record encoding, readable bytes, repair operation definition, controls, cold-cost accounting, metrics, thresholds, aggregation, or classification."
}
