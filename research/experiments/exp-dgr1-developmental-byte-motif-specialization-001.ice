{
  "experiment_id": "EXP-DGR1-DEVELOPMENTAL-BYTE-MOTIF-SPECIALIZATION-001",
  "proposal_parent": "DG1-ADAPTIVE-GRANULARITY-DEVELOPMENT-PROPOSAL-R1",
  "proposal_stage": "DGR-1",
  "question": "Can the existing bounded Yggdrasil developmental/cellular substrate differentiate reproducible motif-specialized cells directly from unsegmented raw-byte streams when motif recurrence is predictive, while resisting equally frequent but successor-shuffled controls?",
  "hypothesis": "Across six new disjoint seeds, a fixed 16-cell ring using only bounded local home-plus/minus-two differentiation will specialize to at least six of eight predictive four-byte motifs, achieve at least 0.90 held-out successor accuracy, lose at least 0.65 accuracy when specialized cells are ablated, and show at most two specialized true-motif cells plus at most 0.25 held-out accuracy under the frequency-matched successor-shuffled control. Pairwise specialized-motif reproducibility across seeds will be at least 0.75 Jaccard.",
  "exact_parent_sha": "2eb8d20f5f9e4c95bff9e852f362146808141c7e",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "prior_evidence": {
    "experiment": "EXP-DG1B-MOTIF-COMPRESSION-DURABILITY-034",
    "classification": "supported",
    "result_sha256": "e3d6d9ff47d1f6a24c04bc84bb20ebac491314757be34696e047f83b3ae5f9d9",
    "scientific_claim": "One informative float64 value (8 bytes) remained sufficient for the frozen regeneration phenotype while zero-information erased/cold controls did not."
  },
  "authority": "synthetic computational research only; no wetware, production, broker, live, accepted-ref, credential, runner-configuration, scheduler, queue-consumer, deployment, or external-model inference authority",
  "changed_paths": [
    "research/experiments/exp-dgr1-developmental-byte-motif-specialization-001.ice",
    "research/applications/plane/exp-dgr1-developmental-byte-motif-specialization-001.py",
    ".yggdrasil/qualification-request.json",
    ".yggdrasil/isolated-run.json"
  ],
  "substrate": {
    "cell_count": 16,
    "topology": "fixed ring",
    "local_assignment_radius": 2,
    "developmental_operations": [
      "DIFFERENTIATE"
    ],
    "forbidden_operations": [
      "REPLICATE",
      "MERGE",
      "HIBERNATE",
      "WAKE",
      "PRUNE",
      "REPAIR",
      "REGENERATE"
    ],
    "capacity_growth": false,
    "raw_input": "identity uint8 bytes with no tokenizer, segmentation marker, motif label, vocabulary remapping, or external embedding",
    "local_candidate_ownership": "each four-byte window is assigned to a home cell h=(3*b0+5*b1+7*b2+11*b3) mod 16; only that cell stores recurrence/successor statistics for the candidate",
    "differentiation_rule": "when a home-local candidate reaches occurrence >=64 with best-successor fraction >=0.90, assign the candidate to the nearest still-generic cell within ring distance <=2 from its home; ties choose lower ring distance then lower cell index. A specialized cell stores exactly one four-byte motif key and one learned successor.",
    "role_persistence": "once differentiated, a cell keeps its role for the remainder of the arm; no reassignment"
  },
  "raw_stream": {
    "hidden_motif_count": 8,
    "hidden_motif_rule": "motif i=[128+i,64+((7*i) mod 32),170,85], i=0..7",
    "successor_rule": "successor i=16+13*i",
    "record_shape": "four motif bytes + one successor byte + three filler bytes; records concatenated without boundary bytes",
    "motif_schedule": "id=(5*record+seed_offset) mod 8, where seed_offset=seed mod 8; every eight-record block contains each motif exactly once",
    "filler_rule": "three bytes per record from an independent SplitMix64-derived stream mapped into 192..255",
    "true_arm": "canonical motif-dependent successor",
    "shuffled_control_arm": "same motif schedule and filler bytes, but successor id=(motif_id+1+((record//8) mod 7)) mod 8; motif frequencies and successor alphabet are preserved while motif-successor consistency is broken",
    "learner_visibility": "record boundaries, motif IDs, canonical successor mapping, and control construction are evaluator-only"
  },
  "corpora": {
    "training_records_per_seed": 4096,
    "evaluation_records_per_seed": 2048,
    "training_bytes_per_seed": 32768,
    "evaluation_bytes_per_seed": 16384,
    "seeds": [
      130003,
      131009,
      132017,
      133027,
      134033,
      135043
    ],
    "seed_policy": "All six seeds were checked against the Yggdrasil repository before preregistration and had no matches. No replacement, exclusion, or extension is permitted.",
    "train_eval_separation": "training and evaluation fillers use disjoint SplitMix64 counter ranges; motif schedule remains balanced in both"
  },
  "evaluation": {
    "target_positions": "successor byte immediately following each hidden four-byte motif; evaluator-only",
    "normal_readout": "for the current four-byte window compute home cell and inspect only specialized cells within home plus/minus two; exact motif-key matches may predict their learned successor, tie by nearest distance then lower cell index; otherwise predict byte zero",
    "ablation_readout": "disable all specialized cells from the true-trained phenotype without retraining; otherwise identical readout",
    "control_readout": "evaluate the successor-shuffled-trained phenotype on the canonical held-out true stream without retraining",
    "specialization_identity": "a specialized cell is counted as true-motif-specialized only if its stored four-byte key equals one of the eight hidden motifs"
  },
  "budgets": {
    "seed_count": 6,
    "arm_count": 2,
    "cell_count": 16,
    "maximum_specialized_cells": 16,
    "local_assignment_radius": 2,
    "training_records_total": 49152,
    "evaluation_records_total": 12288,
    "resident_state_layout": "fixed 16 cell records plus bounded candidate dictionaries owned by fixed home cells; no cell-count growth",
    "timeout_seconds": 1800,
    "numeric_mode": "integer counters and deterministic Python scalar arithmetic; single process"
  },
  "metrics_and_thresholds": [
    {
      "name": "valid_seed_count",
      "comparator": "==",
      "threshold": 6
    },
    {
      "name": "minimum_true_arm_specialized_true_motif_count",
      "comparator": ">=",
      "threshold": 6
    },
    {
      "name": "minimum_true_arm_true_motif_recall",
      "comparator": ">=",
      "threshold": 0.75
    },
    {
      "name": "maximum_true_arm_false_specialization_count",
      "comparator": "<=",
      "threshold": 2
    },
    {
      "name": "minimum_true_arm_heldout_successor_accuracy",
      "comparator": ">=",
      "threshold": 0.9
    },
    {
      "name": "minimum_true_arm_ablation_accuracy_drop",
      "comparator": ">=",
      "threshold": 0.65
    },
    {
      "name": "maximum_control_specialized_true_motif_count",
      "comparator": "<=",
      "threshold": 2
    },
    {
      "name": "maximum_control_heldout_successor_accuracy",
      "comparator": "<=",
      "threshold": 0.25
    },
    {
      "name": "minimum_pairwise_true_arm_specialized_motif_jaccard",
      "comparator": ">=",
      "threshold": 0.75
    },
    {
      "name": "maximum_final_cell_count",
      "comparator": "==",
      "threshold": 16
    },
    {
      "name": "minimum_final_cell_count",
      "comparator": "==",
      "threshold": 16
    },
    {
      "name": "local_assignment_radius_violation_count",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "capacity_growth_event_count",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "invalid_candidate_rows",
      "comparator": "==",
      "threshold": 0
    },
    {
      "name": "counter_overflow_rows",
      "comparator": "==",
      "threshold": 0
    }
  ],
  "validity_criteria": [
    "Exact parent SHA, updated North Star SHA-256, prior sealed evidence identity, and proposal-stage identity match this preregistration.",
    "All six seeds, both arms, and frozen train/evaluation record counts complete deterministically.",
    "Both arms receive identical motif frequencies, motif byte identities, filler bytes, cell topology, cell count, local radius, candidate threshold, and update budget; only motif-successor consistency differs.",
    "No boundary byte, motif ID, canonical successor table, or arm label is visible to candidate ownership, differentiation, or prediction.",
    "Candidate statistics are stored only at their deterministic home cell and differentiation searches no farther than ring radius two.",
    "Cell count remains exactly sixteen and no replication/capacity growth occurs.",
    "Ablation disables specialized cells without retraining or replacement.",
    "The source emits yggdrasil.research-scientific-result.v1 with this exact experiment identifier and a finite metrics object.",
    "Two duplicate executions from identical inputs must be byte-identical before qualification."
  ],
  "classification_rules": {
    "supported": "All validity criteria and all fifteen frozen metric thresholds pass.",
    "mixed": "Validity/completeness pass and true-arm specialization is causal, but at least one recall, reproducibility, control, or accuracy threshold fails.",
    "null": "Validity passes but true-arm specialized-motif recall is below 0.25 and ablation accuracy drop is below 0.10.",
    "negative": "Validity passes but outcome is neither supported, mixed, nor null, including control specialization matching the true arm or noncausal specialization.",
    "incomplete": "Environmental or compute stop prevents full frozen cardinality; preserve diagnostics and make no scientific claim.",
    "invalid": "Any provenance, hidden-label isolation, deterministic construction, local-radius, fixed-capacity, cardinality, finiteness, or qualification criterion fails; invalid is not scientific evidence."
  },
  "stop_conditions": [
    "Stop before execution on provenance, authority, North Star, package-scope, proposal-stage, or hidden-label isolation drift.",
    "Stop as invalid on boundary leakage, motif-ID leakage, assignment beyond radius two, cell-count growth, non-determinism, or malformed resource accounting.",
    "Do not stop early for apparent support, mixed, null, or negative observations."
  ],
  "no_post_result_tuning_rule": "After any primary or diagnostic output is observed, do not alter seeds, motif definitions, schedule, successor/filler rules, control construction, home hash, candidate threshold, consistency threshold, assignment radius, cell count, readout, metrics, thresholds, aggregation, classification, or stop conditions under this experiment identifier."
}
