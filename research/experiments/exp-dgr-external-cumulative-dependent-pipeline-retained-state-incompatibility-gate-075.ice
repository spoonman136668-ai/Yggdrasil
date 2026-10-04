{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-RETAINED-STATE-INCOMPATIBILITY-GATE-075",
  "program": "Yggdrasil corrective RSI tranche: prospective pre-activation incompatibility gate on a disjoint target context",
  "corrective_tranche_path": "research/experiments/yggdrasil-rsi-corrective-tranche-2026-10-04.ice",
  "question": "Can training-only source-specific discriminativity correctly decide whether to reject or allow retained-state-guided local adaptation before activation on a new disjoint target context?",
  "hypothesis": "Use the disjoint fourth manifest 974ecf... as the new target context. Preserve accepted source retained state [10,32,32,32] / best=32 unchanged. Rebuild the target-local canonical B+C donor with the byte-identical Y70/Y74 construction. Freeze two selectors before evaluation: SOURCE_CONDITIONED uses Y74's source byte-class ranking; LOCAL_ONLY uses Y74's occurrence/argmax/utility ranking. Compute source_specificity_gain = source_selected_key_class_match_count - local_selected_key_class_match_count. Freeze ALLOW_SOURCE_PRIOR iff SOURCE_CONDITIONED and LOCAL_ONLY select distinct rows, source_selected best class matches source best class, and source_specificity_gain>=1. Otherwise freeze REJECT. The operational policy is ORIGINAL when REJECT and SOURCE_CONDITIONED rank-7 activation when ALLOW_SOURCE_PRIOR. After the gate decision is frozen, run shadow SOURCE_CONDITIONED and LOCAL_ONLY arms regardless of decision using the exact 068 activation/scoring. Gate correctness is evaluated only afterward. No outcome may change the gate.",
  "exact_parent_sha": "f0058645552e146a0a1d656e3ac388998954da94",
  "qualification_branch": "research/external-hosted-yggdrasil-dependent-pipeline-retained-state-incompatibility-gate-r1",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "predecessor": {
    "experiment": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-LOCAL-PAYLOAD-INTERACTION-074",
    "github_run_id": 37169020525,
    "classification": "negative",
    "validity_pass": true,
    "exact_predecessor_sha": "f0058645552e146a0a1d656e3ac388998954da94",
    "observation": {
      "donor_row_count": 16,
      "eligible_candidate_count": 2,
      "selectors_same_row_count": 1,
      "source_behavior_change_count": 0,
      "local_behavior_change_count": 0,
      "source_positive_prose_collateral_schedule_count": 0,
      "local_positive_prose_collateral_schedule_count": 0,
      "source_state_mutation_count": 0,
      "persistent_state_write_count": 0
    },
    "eliminated_hypothesis": "the coarse source byte-class structural prior contributes useful discriminative selection on the third context",
    "strengthened_hypothesis": "retained-state guidance should be rejected pre-activation when source-specific diagnostics collapse to the local-only decision"
  },
  "cause_effect_trace": {
    "observed_failure": "Y74 source-conditioned and local-only selectors chose the exact same local row and neither changed behavior.",
    "internal_diagnostic": "source-conditioned versus local-only target-row divergence and source/local key-byte-class specificity",
    "attributed_cause": "the retained source supplied no discriminative information beyond local context in the tested target",
    "candidate_corrective_mechanisms": [
      "pre-activation incompatibility rejection",
      "shadow external validation of the rejected/allowed source-conditioned intervention"
    ],
    "frozen_candidate_selection_rule": "ALLOW_SOURCE_PRIOR only when selectors are distinct, source best class matches, and source key-class positional match count exceeds local-only by >=1; otherwise REJECT",
    "exact_bounded_delta": "decision gate only; accepted source state immutable; candidate pool/rankings/capacity unchanged",
    "qualification": "disjoint exact fourth-manifest identity; deterministic double replay; one-shot READY_RESEARCH; decision frozen before held-out evaluation",
    "held_out_result": "shadow source-conditioned/local-only outcomes opened only after gate decision freezes",
    "retain_revert": "REJECT executes ORIGINAL; ALLOW is ephemeral; accepted source retained state never mutates",
    "next_hypothesis": "if gate prospectively distinguishes useful from incompatible reuse, repeat on another disjoint context; a rejection-only success does not establish transferable retained-state usefulness"
  },
  "target_manifest": {
    "path": "research/experiments/external-future-data-fourth-context-manifest-075.json",
    "sha256": "974ecf332c019ac094ecb7098f371001fa7e37fd4b476ac7513341fff6f812e5",
    "source_count": 3,
    "effective_total_bytes": 57272
  },
  "external_authority": {
    "ckb_plane_main_sha": "c499c28c2c62c675350c56c7301f62c89a0bc1e5",
    "manifest_sha256": "974ecf332c019ac094ecb7098f371001fa7e37fd4b476ac7513341fff6f812e5",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "external_model_calls": false,
    "persistent_corpus": false,
    "production_authority": false
  },
  "source_retained_state": {
    "key": [
      10,
      32,
      32,
      32
    ],
    "best": 32,
    "total": 112,
    "best_count": 112,
    "consistency": 1,
    "utility": 112,
    "cell_index": 12,
    "map_best": 32,
    "immutable": true
  },
  "compatibility_gate": {
    "source_selector": "byte-identical Y74 SOURCE_CONDITIONED ranking",
    "local_control": "byte-identical Y74 LOCAL_ONLY ranking",
    "source_specificity_gain": "source_selected_key_class_match_count - local_selected_key_class_match_count",
    "allow_rule": "selectors distinct AND source_selected_best_class_match==1 AND source_specificity_gain>=1",
    "reject_rule": "otherwise",
    "heldout_gate_input_count": 0,
    "post_result_gate_change_count": 0
  },
  "frozen_reuse": {
    "donor_builder": "byte-identical Y70/Y74 canonical B+C donor generalized only to exact target source identities",
    "schedules": [
      "A-C-B",
      "B-C-A",
      "C-A-B",
      "C-B-A"
    ],
    "split": "60% training cue / 40% evaluation",
    "future_packets": 12,
    "activation_position": 7,
    "guard_injection_scoring": "byte-identical 068/Y74",
    "capacity": "16 total / 7 active / 9 retained",
    "success_rule": "dependent incremental correct >0 AND technical-prose collateral incremental correct >0 AND partner collateral incremental correct >0"
  },
  "classification_rules": {
    "supported": "valid and gate decision is prospectively correct: REJECT with shadow SOURCE_CONDITIONED failing to improve over both ORIGINAL and LOCAL_ONLY, or ALLOW_SOURCE_PRIOR with SOURCE_CONDITIONED improving positive prose collateral over both controls and zero partner failures; no source mutation/persistence/capacity/authority violation",
    "mixed": "valid and gate is directionally protective but shadow outcomes are ambiguous, including SOURCE_CONDITIONED behavior/timing change without clean collateral superiority",
    "negative": "valid and gate decision is wrong: REJECT hides a clean source-conditioned rescue or ALLOW_SOURCE_PRIOR admits a non-improving/harmful intervention",
    "invalid": "any parent, authority, target-manifest identity, source-state identity, donor/selector identity, gate formula, heldout-ordering, deterministic replay, capacity, provenance or accounting requirement fails"
  },
  "rsi_success": false,
  "rsi_success_note": "A supported REJECT demonstrates compatibility diagnosis/safe revert, not retained-state transfer. RSI transfer success still requires useful adapted transfer on multiple disjoint contexts.",
  "no_post_result_tuning_rule": "Do not alter target sources, source state, byte classes, candidate eligibility, selectors, source-specificity formula, allow/reject rule, activation/scoring, schedules, split, packet count, 16/7/9 capacity, classification or authority after primary output.",
  "successor_if_supported_allow": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-INCOMPATIBILITY-GATE-REPLICATION-076",
    "intent": "repeat unchanged gate+source-prior adaptation on another disjoint context; only repeated useful ALLOW outcomes can support transfer"
  },
  "successor_if_supported_reject": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-INCOMPATIBILITY-GATE-REPLICATION-076",
    "intent": "repeat unchanged gate on another disjoint context to establish compatibility-diagnosis generalization while continuing search for a useful adapted transfer"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COMPATIBILITY-DIAGNOSTIC-ATTRIBUTION-076",
    "intent": "attribute gate error without forcing retained-state reuse or changing the accepted source state"
  },
  "changed_paths": [
    "research/experiments/external-future-data-fourth-context-manifest-075.json",
    "research/experiments/exp-dgr-external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.ice",
    "research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.py",
    ".github/workflows/external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.yml"
  ]
}
