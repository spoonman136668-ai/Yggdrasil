{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-ORDER-STRESS-024",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "Does the supported six-packet minimal-evidence pipeline remain stable across the four domain orderings not exercised by the prior A-B-C / C-B-A pair?",
  "hypothesis": "Reuse the exact 023 sources, six-packet cumulative prefixes, minimal positive-evidence admission, 16 total / 7 active / 9 retained architecture, minimax consolidation, cue-side active selector, retained encoding, and dormant-retained predictive authority. Execute the four remaining permutations A-C-B, B-A-C, B-C-A, and C-A-B. Supported requires all twelve schedule-domain admissions, no pre-admission evaluation, zero positive-to-nonpositive collapse after admission, every final domain positive, and at least 0.50 active-to-independent benefit whenever the independent arm is positive.",
  "exact_parent_sha": "417270f32c515b6f3663d128c75129bdbee60f57",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-order-stress-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-FINE-PIPELINE-023",
    "github_run_id": "37089779627",
    "classification": "supported",
    "observation": {
      "packet_event_count": 36,
      "admitted_domain_count": 6,
      "postadmission_evaluation_count": 54,
      "positive_then_nonpositive_transition_count": 0,
      "final_nonpositive_domain_count": 0,
      "minimum_active_to_independent_fraction_when_independent_positive": 0.9650711513583441
    }
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host must be distinct from LINKDEADKB",
    "persistent_corpus": false,
    "external_model_calls": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "sources": "byte-identical 023 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "packetization": "byte-identical six cumulative prefix packets from 023",
    "maturity_rule": "byte-identical first strictly positive cue-side contribution admission",
    "base_training": "byte-identical baseline initialization",
    "candidate_statistics": "byte-identical construction and eligibility",
    "independent_adaptation": "byte-identical mechanics",
    "cumulative_consolidation": "byte-identical minimax ranking and radius-two matching",
    "active_selector": "byte-identical seven-active cue-side contribution selector",
    "retained_encoding": "byte-identical nine-retained six-byte records",
    "predictive_authority": "seven active structures only; retained structures are dormant storage"
  },
  "order_stress": {
    "schedules": [["A","C","B"],["B","A","C"],["B","C","A"],["C","A","B"]],
    "packet_count_per_domain": 6,
    "packet_event_count": 72,
    "schedule_domain_admission_count": 12,
    "purpose": "complete the six permutations without changing any memory or feed mechanism"
  },
  "capacity": {
    "total_structures": 16,
    "active_structures": 7,
    "retained_structures": 9,
    "capacity_growth": false,
    "radius": 2
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["packet_event_count","==",72],
    ["admitted_domain_count","==",12],
    ["preadmission_evaluation_count","==",0],
    ["maturity_criterion_violation_count","==",0],
    ["minimum_positive_contribution_rows_at_admission",">=",1],
    ["matched_assignment_failure_count","==",0],
    ["minimum_selected_motif_count","==",16],
    ["maximum_selected_motif_count","==",16],
    ["minimum_active_structure_count","==",7],
    ["maximum_active_structure_count","==",7],
    ["minimum_retained_structure_count","==",9],
    ["maximum_retained_structure_count","==",9],
    ["positive_then_nonpositive_transition_count","==",0],
    ["final_nonpositive_domain_count","==",0],
    ["minimum_active_to_independent_fraction_when_independent_positive",">=",0.5],
    ["retained_record_integrity_mismatch_count","==",0],
    ["state_partition_mismatch_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass across all four remaining schedules.",
    "mixed": "Validity passes and all domains mature/finalize positive, but at least one post-admission retention threshold fails.",
    "negative": "Validity passes but at least one schedule-domain never matures or finishes nonpositive.",
    "invalid": "Any authority, source identity, heldout contamination, schedule drift, packetization drift, maturity-rule drift, fixed-capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "validity_criteria": [
    "Exact sealed 023 parent and North Star identities match.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration and external manifest.",
    "The only experimental delta from 023 is replacing A-B-C/C-B-A with the four remaining frozen permutations.",
    "All source bytes, splits, six-packet boundaries, admission logic, memory mechanics, capacity, and evaluation rules remain unchanged.",
    "Heldout bytes never influence admission, consolidation, active selection, thresholds, or stopping.",
    "Every admitted evaluation partitions exactly sixteen structures into seven active and nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter source bytes, split, six-packet boundaries, the four frozen orderings, one-row maturity rule, consolidation, active selector, retained encoding, capacity, metrics, thresholds, classification, or authority requirements after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-HORIZON",
    "intent": "extend the supported pipeline over repeated domain epochs/reactivation cycles while keeping 16/7/9 fixed"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-ORDER-STRESS-ATTRIBUTION",
    "intent": "attribute any ordering-specific failure before changing the memory substrate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-minimal-evidence-order-stress-024.ice",
    "research/applications/plane/exp-dgr-external-minimal-evidence-order-stress-024.py",
    ".github/workflows/external-minimal-evidence-order-stress-024.yml"
  ]
}
