{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MINIMAL-EVIDENCE-PIPELINE-022",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "Can Yggdrasil preserve cumulative external information when a domain is admitted as soon as its delivered cue contains any strictly positive training-side evidence, instead of requiring enough positive rows to fill all seven active slots?",
  "hypothesis": "Reuse the exact 021 external sources, packet schedules, fixed sixteen-structure consolidation, seven-active selector, nine-retained storage, and dormant-retained predictive authority. Admit a not-yet-admitted domain when its current independent cue has at least one row with strictly positive contribution over the frozen baseline. Supported requires all domains to mature in both schedules, no pre-admission evaluation, zero positive-to-nonpositive collapse after admission, every final domain positive, and at least 0.50 active-to-independent benefit whenever the independent arm is positive.",
  "exact_parent_sha": "8258919e63e5e0b70fe131b88d872ebafa01e36b",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-minimal-evidence-pipeline-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-EVIDENCE-GATED-PIPELINE-021",
    "github_run_id": "37087624365",
    "classification": "negative",
    "observation": {
      "admitted_domain_count": 4,
      "minimum_active_to_independent_fraction_when_independent_positive": 0.9650711513583441,
      "positive_then_nonpositive_transition_count": 0,
      "technical_prose_positive_rows_by_packet": [0,0,1],
      "code_positive_rows_by_packet": [4,7,10],
      "structured_positive_rows_by_packet": [4,4,7]
    },
    "diagnosis": "The seven-positive-row maturity rule excluded low-signal technical prose even when its final cue contained a real positive contribution. Post-admission retention for admitted domains remained strong."
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
    "sources": "byte-identical external source manifest from 017-021",
    "external_split": "byte-identical first 60% cue / final 40% heldout split",
    "packetization": "byte-identical three contiguous prefix increments from 020-021",
    "schedules": [["A","B","C"],["C","B","A"]],
    "base_training": "byte-identical baseline initialization",
    "candidate_statistics": "byte-identical candidate construction and eligibility",
    "independent_adaptation": "byte-identical independent adaptation mechanics",
    "cumulative_consolidation": "byte-identical minimax ranking and radius-two matching",
    "active_selector": "byte-identical cue-side seven-active contribution selector",
    "retained_encoding": "byte-identical six-byte retained records",
    "predictive_authority": "only seven cue-selected active structures predict; nine retained structures are dormant storage"
  },
  "maturity_gate": {
    "scope": "training-side cue only; heldout bytes and heldout accuracy are unavailable",
    "calculation": "unchanged 021 independent sixteen-structure cue contribution scoring relative to the frozen baseline",
    "criterion": "positive_contribution_row_count >= 1",
    "basis": "minimal evidence: require at least one learned row with strictly positive cue-side contribution before admitting the domain; zero-evidence packets remain buffered",
    "before_maturity": "the domain contributes no bytes to shared consolidation and receives no heldout evaluation",
    "after_maturity": "admission is permanent and later packets update normally",
    "threshold_tuning": false
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
    ["packet_event_count","==",18],
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
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass.",
    "mixed": "Validity passes and every domain matures and finishes positive, but a post-admission retention threshold fails.",
    "negative": "Validity passes but a domain never reaches minimal positive evidence, or a final admitted domain is nonpositive.",
    "invalid": "Any authority, source identity, heldout contamination, maturity-gate drift, consolidation drift, fixed-capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "validity_criteria": [
    "Exact sealed 021 parent and North Star identities match.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration commit and external manifest.",
    "Execution occurs only on GitHub-hosted compute; verified external bytes are deleted before completion.",
    "Packet schedule and delivered bytes are identical to 020-021.",
    "Maturity uses only delivered cue bytes, frozen baseline, independent state, and unchanged contribution function; heldout bytes never influence admission.",
    "A zero-positive-row domain remains buffered and is not evaluated.",
    "Once admitted, a domain is never removed.",
    "The sixteen-structure matching, seven-active selector, nine-retained encoding, and dormant-retained predictive-authority rule are unchanged.",
    "Every admitted evaluation partitions exactly sixteen structures into seven active and nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter source bytes, split, packet boundaries, schedules, positive-contribution definition, one-row maturity threshold, admission monotonicity, consolidation, active selector, retained encoding, capacity, metrics, thresholds, classification, or authority requirements after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-minimal-evidence-pipeline-022.ice",
    "research/applications/plane/exp-dgr-external-minimal-evidence-pipeline-022.py",
    ".github/workflows/external-minimal-evidence-pipeline-022.yml"
  ]
}
