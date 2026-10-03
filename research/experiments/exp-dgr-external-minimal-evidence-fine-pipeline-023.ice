{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-FINE-PIPELINE-023",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "Does the supported minimal-evidence admission rule remain stable when the same external cue streams arrive in six finer packets instead of three?",
  "hypothesis": "Reuse the exact 022 external sources, 16 total / 7 active / 9 retained architecture, minimal positive-evidence admission rule, minimax consolidation, active selector, retained encoding, and dormant-retained predictive authority. Split each domain's same 60% adaptation cue into six contiguous cumulative prefix packets and interleave the same A-B-C and C-B-A schedules. Supported requires all six schedule-domain admissions, no pre-admission evaluation, zero positive-to-nonpositive collapse after admission, every final domain positive, and at least 0.50 active-to-independent benefit whenever the independent arm is positive.",
  "exact_parent_sha": "9bdc26c52fe7a82d1dc816d261bcfb20ae103c60",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-fine-pipeline-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-PIPELINE-022",
    "github_run_id": "37088263406",
    "classification": "supported",
    "observation": {
      "admitted_domain_count": 6,
      "positive_then_nonpositive_transition_count": 0,
      "final_nonpositive_domain_count": 0,
      "minimum_active_to_independent_fraction_when_independent_positive": 0.9650711513583441
    },
    "diagnosis": "Minimal nonzero cue-side evidence solved feed admission without weakening fixed-capacity cumulative retention."
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
    "sources": "byte-identical external source manifest from 017-022",
    "external_split": "byte-identical first 60% cue / final 40% heldout split",
    "base_training": "byte-identical baseline initialization",
    "candidate_statistics": "byte-identical candidate construction and eligibility",
    "independent_adaptation": "byte-identical independent adaptation mechanics",
    "cumulative_consolidation": "byte-identical minimax ranking and radius-two matching",
    "active_selector": "byte-identical cue-side seven-active contribution selector",
    "retained_encoding": "byte-identical six-byte retained records",
    "predictive_authority": "only seven cue-selected active structures predict; nine retained structures remain dormant storage",
    "maturity_rule": "admit permanently on first packet whose current independent cue has at least one strictly positive contribution row over frozen baseline"
  },
  "fine_packetization": {
    "packet_count_per_domain": 6,
    "prefix_length_rule": "for packet p in 1..5 use floor(N*p/6) bytes, with a minimum of one byte and strictly less than N; packet 6 uses all N cue bytes",
    "schedules": [["A","B","C"],["C","B","A"]],
    "total_packet_event_count": 36,
    "heldout_bytes_in_admission": false
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
    ["packet_event_count","==",36],
    ["admitted_domain_count","==",6],
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
  "diagnostic_metrics": [
    "maturity packet index by schedule/domain",
    "positive contribution row count at every one of six packets",
    "buffered packet count before admission",
    "post-admission evaluation count",
    "minimum active incremental correct count after admission",
    "per-stage baseline, independent, active increments for admitted domains only"
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass.",
    "mixed": "Validity passes and every domain matures and finishes positive, but a post-admission retention threshold fails.",
    "negative": "Validity passes but a domain never reaches minimal positive evidence, or a final admitted domain is nonpositive.",
    "invalid": "Any authority, source identity, heldout contamination, packetization drift, maturity-gate drift, consolidation drift, fixed-capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "validity_criteria": [
    "Exact sealed 022 parent and North Star identities match.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration commit and external manifest.",
    "Execution occurs only on GitHub-hosted compute; verified external bytes are deleted before completion.",
    "Only packet granularity changes from 022: six cumulative prefix packets replace three; all scientific memory/admission mechanisms remain identical.",
    "Maturity uses only delivered cue bytes, frozen baseline, independent state, and unchanged contribution function; heldout bytes never influence admission.",
    "A zero-positive-row domain remains buffered and unevaluated; admission is permanent on the first positive-evidence packet.",
    "Every admitted evaluation partitions exactly sixteen structures into seven active and nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter source bytes, split, six-packet boundaries, schedules, one-row maturity threshold, admission monotonicity, consolidation, active selector, retained encoding, capacity, metrics, thresholds, classification, or authority requirements after any primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-ORDER-STRESS",
    "intent": "stress the supported fine-grained feed under additional preregistered domain orderings without changing capacity"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-FINE-PIPELINE-ATTRIBUTION",
    "intent": "attribute failure to packet granularity, admission timing, or consolidation interaction before changing the memory substrate"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-minimal-evidence-fine-pipeline-023.ice",
    "research/applications/plane/exp-dgr-external-minimal-evidence-fine-pipeline-023.py",
    ".github/workflows/external-minimal-evidence-fine-pipeline-023.yml"
  ]
}
