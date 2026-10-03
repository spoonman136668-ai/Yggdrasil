{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-INTERLEAVED-PIPELINE-020",
  "program": "Yggdrasil external pipelined cumulative consolidation",
  "question": "Can Yggdrasil absorb three independent external domains as interleaved sequential information packets while preserving already-acquired useful capability under the fixed sixteen-cell, seven-active, nine-retained memory discipline?",
  "hypothesis": "Delivering each domain's frozen 60% adaptation cue in three contiguous packets, interleaved in both A-B-C and C-B-A schedules, will produce valid fixed-capacity states at every stage; once a domain first achieves positive heldout active benefit it will not later fall to nonpositive benefit as additional packets arrive, all three domains will be positive at the final stage, and active benefit will retain at least 0.50 of independently adapted benefit whenever the independent arm is positive.",
  "exact_parent_sha": "ea6c89cd0043156e9ad4217eeceffaac9d94fd9a",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-pipeline-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-FINAL-CUE-REACTIVATION-019",
    "qualification_run_id": "37083741409",
    "classification": "mixed",
    "observation": "All six order-by-domain aggregate active reactivation benefits were positive. The two nonpositive individual C/H2 windows were also nonpositive under independent adaptation, while C/H1 interference was rescued by seven-active cue reactivation."
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
  "frozen_input_protocol": {
    "sources": "byte-identical three-source manifest used by 017-019",
    "adaptation_region": "first floor(0.60*N) bytes per source, identical to 017-019",
    "packetization": "split each adaptation region into three contiguous prefix increments using boundaries floor(M/3), floor(2M/3), M; no byte is reordered or duplicated",
    "schedules": [
      ["A1","B1","C1","A2","B2","C2","A3","B3","C3"],
      ["C1","B1","A1","C2","B2","A2","C3","B3","A3"]
    ],
    "heldout": "the final 40% of each source remains sealed from adaptation, consolidation, active selection, thresholds, and stopping rules"
  },
  "frozen_reuse": {
    "base_training": "byte-identical 016-019 baseline initialization",
    "candidate_statistics": "byte-identical four-byte candidate statistics and eligibility",
    "minimax_ranking": "byte-identical 017-019 minimax contribution ranking",
    "local_assignment": "byte-identical radius-two deterministic feasibility-preserving matching",
    "active_selector": "byte-identical cue-side seven-active contribution selector from 017-019",
    "retained_encoding": "byte-identical six-byte retained records",
    "predictive_authority": "only the seven cue-selected active structures predict; nine retained structures are dormant storage"
  },
  "capacity": {
    "total_structures": 16,
    "active_structures": 7,
    "retained_structures": 9,
    "capacity_growth": false,
    "radius": 2
  },
  "primary_evaluation": {
    "pipeline_stage_count": 18,
    "evaluation_rule": "after every packet, evaluate every domain that has received at least one packet on that domain's full frozen 40% heldout region using only its currently available cue prefix to select seven active structures",
    "controls": "same-stage independent adaptation using the same available cue prefix and the frozen generic baseline",
    "retention_rule": "for each schedule/domain, after the first stage at which active heldout benefit is positive, no later stage may become nonpositive"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["pipeline_stage_count","==",18],
    ["valid_pipeline_state_count","==",18],
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
    "pipeline_evaluation_count",
    "first_positive_stage_by_schedule_domain",
    "minimum_active_incremental_correct_count",
    "minimum_final_active_incremental_correct_count",
    "per-stage admitted packet, available cue bytes, baseline, independent, and active correct counts"
  ],
  "classification_rules": {
    "supported": "All validity criteria and frozen thresholds pass.",
    "mixed": "Validity passes and all final domains are positive, but at least one previously positive domain becomes nonpositive during the pipeline or the 0.50 independent-retention threshold fails.",
    "negative": "Validity passes but at least one domain is nonpositive at the final pipeline stage in either schedule.",
    "invalid": "Any authority, source identity, contamination, mechanism drift, fixed-capacity, partition, record-integrity, determinism, or host-isolation criterion fails.",
    "incomplete": "Authority, source retrieval, or hosted compute interruption prevents the frozen pipeline."
  },
  "validity_criteria": [
    "The exact sealed 019 head is the parent and all 017-019 scientific evidence remains unchanged.",
    "A fresh CKB-plane READY_RESEARCH receipt is bound to this exact preregistration commit and frozen external manifest.",
    "Execution occurs only on GitHub-hosted compute; source bytes are SHA-256 verified and deleted before completion.",
    "At each stage only the admitted prefix bytes are available; future packet bytes and all heldout bytes remain unavailable to adaptation, consolidation, active selection, thresholds, and stopping.",
    "The sixteen-cell minimax-matched mechanism, seven-active selector, nine-retained record format, and dormant-retained predictive-authority rule are unchanged.",
    "Each stage has exactly sixteen matched structures partitioned into seven active and nine retained structures for every evaluated domain.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter packet boundaries, schedules, source bytes, heldout region, cumulative state construction, active selector, retained encoding, predictive-authority rule, capacity, metrics, thresholds, classification, or authority requirements after any primary output.",
  "changed_paths": [
    "research/experiments/exp-dgr-external-interleaved-pipeline-020.ice",
    "research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py",
    ".github/workflows/external-interleaved-pipeline-020.yml"
  ]
}
