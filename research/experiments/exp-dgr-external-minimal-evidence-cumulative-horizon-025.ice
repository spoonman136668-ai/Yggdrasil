{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-HORIZON-025",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "Does the order-robust minimal-evidence memory remain stable over a substantially longer cumulative event horizon without increasing the 16/7/9 substrate?",
  "hypothesis": "Reuse the exact 024 external sources, admission rule, consolidation, active selector, retained encoding, predictive authority, and all six domain permutations. Increase only temporal resolution from six to twelve cumulative prefix packets per domain. Across 216 packet events, all eighteen schedule-domain admissions will complete, no admitted domain will undergo a positive-to-nonpositive transition, every final domain will remain positive, and the minimum active-to-independent benefit when independent is positive will remain at least 0.50.",
  "exact_parent_sha": "6f418ef6a9df8817693dde5322a55d1940fd1f85",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-cumulative-horizon-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-ORDER-STRESS-024",
    "github_run_id": "37107002153",
    "classification": "supported",
    "observation": {
      "packet_event_count": 72,
      "admitted_domain_count": 12,
      "postadmission_evaluation_count": 108,
      "positive_then_nonpositive_transition_count": 0,
      "final_nonpositive_domain_count": 0,
      "minimum_active_to_independent_fraction_when_independent_positive": 0.9650711513583441
    },
    "diagnosis": "Six-packet minimal-evidence consolidation is robust across all six domain orderings; the next bounded risk is longer cumulative consolidation horizon rather than ordering."
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
    "sources": "byte-identical external manifest from 024",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six permutations A-B-C, A-C-B, B-A-C, B-C-A, C-A-B, C-B-A",
    "maturity_rule": "permanent admission on first packet with at least one strictly positive cue-side contribution row over frozen baseline",
    "base_training": "byte-identical baseline initialization",
    "candidate_statistics": "byte-identical construction and eligibility",
    "independent_adaptation": "byte-identical mechanics",
    "cumulative_consolidation": "byte-identical minimax ranking and radius-two matching",
    "active_selector": "byte-identical seven-active cue-side contribution selector",
    "retained_encoding": "byte-identical nine-retained six-byte records",
    "predictive_authority": "seven active structures only; retained structures remain dormant storage"
  },
  "horizon_stress": {
    "packet_count_per_domain": 12,
    "prefix_length_rule": "for packet p in 1..11 use floor(N*p/12) bytes, minimum one byte and strictly less than N; packet 12 uses all N cue bytes",
    "schedule_count": 6,
    "packet_event_count": 216,
    "schedule_domain_admission_count": 18,
    "purpose": "double consolidation/event horizon while holding total evidence, domain order set, capacity, and memory mechanics fixed"
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
    ["packet_event_count","==",216],
    ["admitted_domain_count","==",18],
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
    "supported": "All validity criteria and frozen thresholds pass across all six schedules and twelve packets.",
    "mixed": "Validity passes and all schedule-domains mature and finish positive, but at least one post-admission retention threshold fails.",
    "negative": "Validity passes but at least one schedule-domain never matures or finishes nonpositive.",
    "invalid": "Any authority, source identity, heldout contamination, schedule, packetization, maturity, consolidation, fixed-capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "validity_criteria": [
    "Exact sealed 024 parent and North Star identities match.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration and external manifest.",
    "The only scientific delta from 024 is twelve cumulative prefix packets and inclusion of all six already-tested schedule permutations in one horizon matrix.",
    "All source bytes, split, admission logic, memory mechanics, capacity, and evaluation rules remain unchanged.",
    "Heldout bytes never influence admission, consolidation, active selection, thresholds, or stopping.",
    "Every admitted evaluation partitions exactly sixteen structures into seven active and nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter source bytes, split, twelve-packet boundaries, six frozen schedules, one-row maturity rule, consolidation, active selector, retained encoding, capacity, metrics, thresholds, classification, or authority requirements after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-CUMULATIVE-REACTIVATION",
    "intent": "introduce explicit dormant/reawaken cycles after the supported long horizon while preserving 16/7/9"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-HORIZON-ATTRIBUTION",
    "intent": "attribute any long-horizon failure to admission timing, consolidation pressure, or domain-specific interference before changing substrate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-minimal-evidence-cumulative-horizon-025.ice",
    "research/applications/plane/exp-dgr-external-minimal-evidence-cumulative-horizon-025.py",
    ".github/workflows/external-minimal-evidence-cumulative-horizon-025.yml"
  ]
}
