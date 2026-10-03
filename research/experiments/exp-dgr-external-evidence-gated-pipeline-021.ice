{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-EVIDENCE-GATED-PIPELINE-021",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "Can Yggdrasil preserve fixed-capacity cumulative memory under interleaved external packet delivery when immature domain packets are buffered until the cue itself supports a full seven-active wake set?",
  "hypothesis": "Reuse the exact three-packet A-B-C and C-B-A schedules, external sources, 16-structure consolidation, seven-active selector, nine-retained storage, and dormant-retained predictive authority from 020. Before a domain first enters shared consolidation, compute its independent cue-side contribution scores only from currently delivered cue bytes; admit it only when at least seven of its sixteen independent rows have strictly positive contribution relative to the frozen baseline. Once admitted, it remains admitted and receives later packets normally. Supported requires all three domains to mature in both schedules, no pre-admission evaluation, no positive-to-nonpositive retention collapse after admission, all final admitted domains positive, and at least 0.50 active-to-independent benefit whenever the independent arm is positive.",
  "exact_parent_sha": "6e258a6ef8e025d80015e81ccea11506baea5e3c",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-evidence-gated-pipeline-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-INTERLEAVED-PIPELINE-020",
    "github_run_id": "37084317130",
    "classification": "mixed",
    "observation": {
      "pipeline_evaluation_count": 48,
      "positive_then_nonpositive_transition_count": 0,
      "final_nonpositive_domain_count": 0,
      "minimum_final_active_incremental_correct_count": 1,
      "minimum_active_to_independent_fraction_when_independent_positive": -1
    },
    "diagnosis": "The pipeline retained acquired capability. The mixed result came from technical-prose C being independently only +1 at sparse 290/581-byte cue prefixes while shared seven-active reads were 0/-1; after the full 872-byte cue, C became positive and never relapsed."
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
    "sources": "byte-identical external source manifest from 017-020",
    "external_split": "byte-identical first 60% cue / final 40% heldout split",
    "packetization": "byte-identical three contiguous prefix increments from 020",
    "schedules": [["A","B","C"],["C","B","A"]],
    "base_training": "byte-identical baseline initialization from 016-020",
    "candidate_statistics": "byte-identical candidate construction and eligibility",
    "independent_adaptation": "byte-identical independent adaptation mechanics",
    "cumulative_consolidation": "byte-identical minimax ranking and radius-two matching",
    "active_selector": "byte-identical cue-side seven-active contribution selector",
    "retained_encoding": "byte-identical six-byte retained records",
    "predictive_authority": "only seven cue-selected active structures predict; nine retained structures are dormant storage"
  },
  "maturity_gate": {
    "scope": "training-side cue only; heldout bytes and heldout accuracy are unavailable",
    "calculation": "for the currently delivered cue prefix, build the frozen independent sixteen-structure map and known rows, score each row with the unchanged error-guided cue contribution function relative to the frozen baseline",
    "criterion": "positive_contribution_row_count >= 7",
    "architectural_basis": "seven is the already-frozen active-structure ceiling; the gate asks whether the cue can positively support a complete active set before entering shared consolidation",
    "before_maturity": "the domain's delivered bytes remain buffered and do not enter shared consolidation, active selection against the shared state, or heldout evaluation",
    "after_maturity": "the domain is permanently admitted for the remainder of that schedule and later packets update it normally",
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
    ["minimum_positive_contribution_rows_at_admission",">=",7],
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
    "positive contribution row count at every packet",
    "buffered packet count before admission",
    "post-admission evaluation count",
    "minimum active incremental correct count after admission",
    "per-stage baseline, independent, active increments for admitted domains only"
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass.",
    "mixed": "Validity passes and every domain matures and finishes positive, but at least one post-admission 0.50 retention threshold or positive-to-nonpositive criterion fails.",
    "negative": "Validity passes but a domain never reaches the training-side maturity criterion, or any final admitted domain is nonpositive.",
    "invalid": "Any authority, source identity, heldout contamination, maturity-gate drift, consolidation drift, fixed-capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen matrix."
  },
  "validity_criteria": [
    "Exact sealed 020 parent and North Star identities match.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration commit and external manifest.",
    "Execution occurs only on GitHub-hosted compute; verified external bytes are deleted before completion.",
    "The packet schedule and bytes delivered at every packet are identical to 020.",
    "Maturity uses only the delivered cue prefix, frozen baseline, independent state, and unchanged contribution function; no heldout byte or heldout metric participates.",
    "A not-yet-mature domain contributes no bytes to the shared consolidated state and receives no heldout evaluation.",
    "Once mature, admission is monotonic and the domain is never removed from the shared state.",
    "The sixteen-structure minimax matching, seven-active selector, nine-retained record format, and dormant-retained predictive-authority rule are unchanged from 020.",
    "Every admitted evaluation partitions exactly sixteen structures into seven active and nine retained records.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter source bytes, split, packet boundaries, schedules, positive-contribution definition, seven-row maturity threshold, admission monotonicity, consolidation, active selector, retained encoding, capacity, metrics, thresholds, classification, or authority requirements after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-evidence-gated-pipeline-021.ice",
    "research/applications/plane/exp-dgr-external-evidence-gated-pipeline-021.py",
    ".github/workflows/external-evidence-gated-pipeline-021.yml"
  ]
}
