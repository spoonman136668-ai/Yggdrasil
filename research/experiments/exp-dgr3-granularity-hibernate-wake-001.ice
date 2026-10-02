{
  "experiment_id": "EXP-DGR3-GRANULARITY-HIBERNATE-WAKE-001",
  "proposal_parent": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "proposal_stage": "DGR-3",
  "question": "Can the qualified four-structure DGR-2 granularity phenotype fully hibernate and later reactivate from bounded retained wake information materially faster than cold redevelopment while preserving predictive function across repeated cycles?",
  "hypothesis": "Across the six paired DGR-1/DGR-2 seeds, hibernation will reduce active motif structures from four to zero while retaining exactly 36 logical wake bytes; wake will restore all four merged structures in exactly four wake operations, recover at least 0.95 held-out accuracy across three repeated hibernate/wake cycles, cost at most 1% of cold redevelopment operations, and erased or successor-shuffled wake controls will remain at or below 0.25 accuracy.",
  "exact_parent_sha": "2b38a19cca9fa528857cc40111e7f8ac402f225a",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DGR2-RESOURCE-PRESSURE-GRANULARITY-CONSOLIDATION-001",
    "classification": "supported",
    "result_sha256": "bdc8879ab58ea31c2cdca76bbcc751e06429e1ae85c4d55e47b0f9e6995d8cb7",
    "scientific_claim": "Eight specialized raw-byte motifs locally merged into four compact structures with perfect capability, 50% active-structure reduction, and 20% logical motif-state reduction."
  },
  "authority": "synthetic computational research only; no wetware, production, live, accepted-ref, scheduler, queue-consumer, deployment, or external-model inference authority",
  "changed_paths": [
    "research/experiments/exp-dgr3-granularity-hibernate-wake-001.ice",
    "research/applications/plane/exp-dgr3-granularity-hibernate-wake-001.py",
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
    "paired_reuse_reason": "Exact DGR-1 development plus DGR-2 merge replay; this experiment isolates hibernate/wake rather than fresh learning.",
    "frozen_reuse": [
      "DGR-1 corpus and differentiation",
      "DGR-2 local merge rule",
      "DGR-2 compact merged representation",
      "held-out evaluation corpus"
    ]
  },
  "hibernation": {
    "active_structures_before": 4,
    "active_structures_during": 0,
    "retained_record_per_merged_structure": "one receiver cell index byte + two shared-suffix bytes + two (two-byte prefix + one successor byte) variants = 9 logical bytes",
    "retained_structure_count": 4,
    "retained_logical_bytes": 36,
    "operation": "HIBERNATE",
    "forbidden_during_hibernation": [
      "retraining",
      "candidate scanning",
      "re-differentiation",
      "MERGE",
      "REPLICATE",
      "external retrieval"
    ]
  },
  "wake": {
    "operation": "WAKE",
    "wake_operations": "one reconstruction operation per retained merged structure",
    "expected_wake_operations": 4,
    "repeated_cycles": 3,
    "cold_redevelopment_operations": "number of four-byte training windows processed by DGR-1 development plus DGR-2 merge operations",
    "control_erased": "replace all retained wake bytes with zero before wake",
    "control_successor_shuffled": "preserve receiver positions, keys, suffixes, and record sizes but cyclically rotate the eight stored successor bytes by one position before wake"
  },
  "metrics_and_thresholds": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 6
    },
    {
      "name": "minimum_post_wake_accuracy_across_cycles",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "minimum_cold_redevelopment_accuracy",
      "comparator": ">=",
      "threshold": 0.95
    },
    {
      "name": "maximum_wake_accuracy_gap_vs_cold",
      "comparator": "<=",
      "threshold": 0.02
    },
    {
      "name": "maximum_hibernated_active_structure_count",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "maximum_retained_wake_bytes",
      "comparator": "==",
      "threshold": 36
    },
    {
      "name": "minimum_retained_wake_bytes",
      "comparator": "==",
      "threshold": 36
    },
    {
      "name": "maximum_wake_operations",
      "comparator": "==",
      "threshold": 4
    },
    {
      "name": "minimum_cold_redevelopment_operations",
      "comparator": ">=",
      "threshold": 32768
    },
    {
      "name": "maximum_wake_to_cold_operation_ratio",
      "comparator": "<=",
      "threshold": 0.01
    },
    {
      "name": "maximum_erased_wake_control_accuracy",
      "comparator": "<=",
      "threshold": 0.25
    },
    {
      "name": "maximum_successor_shuffled_wake_control_accuracy",
      "comparator": "<=",
      "threshold": 0.25
    },
    {
      "name": "minimum_wake_structure_jaccard_vs_prehibernate",
      "comparator": ">=",
      "threshold": 1
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
      "name": "invalid_wake_rows",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "validity_criteria": [
    "Exact parent SHA, North Star identity, and sealed DGR-2 evidence identity match.",
    "Each seed reproduces the exact DGR-2 four-structure phenotype before hibernation.",
    "HIBERNATE leaves zero active motif structures and retains exactly four fixed 9-byte records.",
    "WAKE uses only retained records and fixed topology; no training bytes, candidate tables, hidden motif IDs, or canonical successor table are available.",
    "Repeated wake cycles use the phenotype produced by the prior wake cycle, not a fresh DGR-2 reconstruction.",
    "Cold redevelopment replays the full frozen DGR-1 train stream and DGR-2 merge rule.",
    "Erased and successor-shuffled controls receive no corrective oracle or retraining.",
    "Total physical cell count remains exactly sixteen and no capacity growth occurs.",
    "The source emits yggdrasil.research-scientific-result.v1 with exact experiment identifier and finite metrics.",
    "Two duplicate executions from identical inputs must be byte-identical."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all seventeen frozen thresholds pass.",
    "mixed": "Wake is materially cheaper than cold redevelopment and preserves most capability, but at least one exact-state, repeated-cycle, or control threshold fails.",
    "null": "Validity passes but post-wake accuracy remains below 0.25 and wake controls are indistinguishable.",
    "negative": "Validity passes but wake is not materially cheaper than cold redevelopment or loses substantial capability.",
    "incomplete": "Environmental or compute stop prevents complete deterministic evaluation.",
    "invalid": "Provenance, DGR-2 replay, retained-state identity, no-retraining isolation, fixed-capacity, deterministic execution, or qualification criteria fail."
  },
  "no_post_result_tuning_rule": "After any output is observed, do not alter seeds, DGR-1/DGR-2 replay, retention encoding, retained bytes, cycle count, wake operation definition, cold-cost accounting, controls, metrics, thresholds, aggregation, or classification."
}
