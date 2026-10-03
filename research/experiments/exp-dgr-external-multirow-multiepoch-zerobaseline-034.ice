{
  "schema": "yggdrasil.direct-preregistration.v1",
  "experiment_id": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-ZEROBASELINE-034",
  "program": "Yggdrasil fixed-capacity simultaneous dormant-capability preservation across repeated reconsolidation with defined zero-baseline scoring",
  "question": "When a non-target capability has zero unprotected heldout benefit before maturity, does the multirow preservation mechanism remain valid if zero-baseline cases are explicitly outside the retention-ratio domain while still being required not to become harmful?",
  "hypothesis": "Repeat the exact 033 preservation mechanism, schedules, target pairs, and packet-4/8/12 non-target epochs. For a non-target case with unprotected incremental benefit greater than zero, compute preserved/unprotected retention and require at least 0.95. For a case with unprotected incremental benefit equal to zero, mark the ratio not-applicable, count the case separately, and require preserved incremental benefit to remain nonnegative. The exact frozen matrix is expected to contain 12 zero-baseline cases and 42 ratio-applicable cases; all 108 target reactivation evaluations and all 36 final-epoch target evaluations must remain positive.",
  "exact_parent_sha": "397aea454edfc7914a305c63e1b5796874c825ca",
  "north_star_path": "research/architecture/yggdrasil-north-star.ice",
  "north_star_sha256": "57aa9418059fad959a1a038598576c8148f792209855fa2d7f3c05833493497c",
  "qualification_branch": "research/external-hosted-yggdrasil-multirow-multiepoch-zerobaseline-r1",
  "prior_evidence": {
    "experiment": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-COMPETITION-033",
    "github_run_id": "37118980845",
    "classification": "invalid",
    "invalid_reason": "zero_baseline_retention_semantics_underspecified",
    "observation": {
      "competition_epoch_case_count": 54,
      "target_reactivation_evaluation_count": 108,
      "positive_target_reactivation_evaluation_count": 108,
      "final_epoch_positive_target_evaluation_count": 36,
      "minimum_target_preserved_incremental_correct_count": 1,
      "invalid_evaluation_rows": 12
    },
    "diagnosis": "All preservation outcomes were positive, but six schedules times the packet-4 and packet-8 A/B-target cases used C as the sole non-target before C matures at packet 11. In those 12 cases both unprotected and preserved increments were zero, and 033 had not preregistered zero-denominator retention semantics."
  },
  "scientific_reuse": {
    "mechanism_change": false,
    "allowed_change": "evaluation-domain contract and explicit zero-baseline diagnostics only",
    "forbidden": "changes to sources, packet epochs, schedules, target pairs, protected rows, deduplication, interference construction, eviction ranking, active selector, capacity, or heldout scoring values"
  },
  "external_authority": {
    "ckb_plane_main_sha": "36d99a0257120ede57bb96638660d35014dd529e",
    "manifest_sha256": "75cdb3b97dbb7017299f573d506f07095ed89c06264b29724b78f29c909d4da4",
    "research_decision_required": "READY_RESEARCH",
    "execution_host_policy": "GitHub-hosted compute only; host distinct from LINKDEADKB",
    "persistent_corpus": false,
    "external_model_calls": false,
    "production_authority": false
  },
  "frozen_reuse": {
    "sources": "byte-identical 033 external manifest",
    "external_split": "byte-identical first 60% cue / final 40% heldout",
    "schedules": "all six frozen permutations",
    "target_pairs": [["A","B"],["A","C"],["B","C"]],
    "epoch_packet_indices": [4,8,12],
    "maturity_rule": "byte-identical twelve-packet maturity cue",
    "all_domain_state": "byte-identical 033 all-domain reconstruction",
    "protected_row_rule": "byte-identical 033 per-target rule",
    "protected_key_deduplication": "byte-identical 033",
    "eviction_ranking": "byte-identical 033 non-target cue contribution, lower utility, lexicographically larger key",
    "active_selector": "byte-identical seven-active cue contribution selector",
    "capacity": "16 total / 7 active / 9 retained"
  },
  "zero_baseline_contract": {
    "applicable_ratio_condition": "unprotected non-target incremental heldout benefit > 0",
    "applicable_ratio": "preserved incremental benefit divided by unprotected incremental benefit",
    "applicable_ratio_floor": 0.95,
    "zero_baseline_condition": "unprotected non-target incremental heldout benefit == 0",
    "zero_baseline_ratio": "not applicable and excluded from minimum retention ratio",
    "zero_baseline_safety": "preserved non-target incremental heldout benefit must be >= 0",
    "expected_zero_baseline_case_count": 12,
    "expected_ratio_applicable_case_count": 42,
    "selection_use": "heldout increments affect scoring/classification only and never row selection, eviction, active selection, epoch choice, or stopping"
  },
  "metrics_and_thresholds": [
    ["source_identity_mismatch_count","==",0],
    ["source_count","==",3],
    ["total_source_bytes","==",57272],
    ["base_training_identity_mismatch_count","==",0],
    ["schedule_count","==",6],
    ["target_pair_count","==",3],
    ["epoch_count","==",3],
    ["competition_epoch_case_count","==",54],
    ["target_reactivation_evaluation_count","==",108],
    ["positive_target_reactivation_evaluation_count","==",108],
    ["final_epoch_positive_target_evaluation_count","==",36],
    ["minimum_target_preserved_incremental_correct_count",">=",1],
    ["zero_baseline_non_target_case_count","==",12],
    ["ratio_applicable_non_target_case_count","==",42],
    ["zero_baseline_preserved_negative_count","==",0],
    ["minimum_applicable_non_target_preserved_to_unprotected_fraction",">=",0.95],
    ["preserved_state_structure_count_min","==",16],
    ["preserved_state_structure_count_max","==",16],
    ["active_structure_count_min","==",7],
    ["active_structure_count_max","==",7],
    ["retained_structure_count_min","==",9],
    ["retained_structure_count_max","==",9],
    ["target_interference_leakage_count","==",0],
    ["heldout_selection_use_count","==",0],
    ["capacity_growth_event_count","==",0],
    ["tokenizer_use_count","==",0],
    ["external_model_call_count","==",0],
    ["invalid_evaluation_rows","==",0]
  ],
  "classification_rules": {
    "supported": "Validity passes, all target/final target thresholds pass, all 12 zero-baseline cases remain nonnegative, and every one of the 42 applicable non-target retention ratios is at least 0.95.",
    "mixed": "Validity passes and all final target evaluations are positive, but an intermediate target, zero-baseline safety, or applicable retention threshold fails.",
    "negative": "Validity passes but at least one final-epoch target evaluation is nonpositive.",
    "invalid": "Any sealed-parent, authority, scientific-reuse identity, source, zero-baseline domain accounting, capacity, determinism, or heldout-isolation criterion fails."
  },
  "validity_criteria": [
    "Exact sealed invalid-033 parent and North Star identities match.",
    "Fresh READY_RESEARCH is bound to this exact preregistration and external manifest.",
    "The scientific preservation mechanism is unchanged from 033; only zero-baseline metric-domain handling and diagnostics change.",
    "Exactly 54 non-target epoch cases are partitioned once into 12 zero-baseline and 42 ratio-applicable cases; no case is omitted or counted twice.",
    "Heldout increments are used only after all training-side row/preservation decisions are frozen.",
    "Every epoch retains exactly sixteen structures / seven active / nine retained.",
    "Duplicate complete executions are byte-identical and all numeric outputs are finite.",
    "No tokenizer, external model, persistent corpus, capacity/radius change, LINKDEADKB execution, production authority, or post-result tuning occurs."
  ],
  "no_post_result_tuning_rule": "Do not alter sources, split, schedules, target pairs, epochs, maturity cues, protected-row rule, deduplication, eviction ranking, selectors, zero-baseline definition, expected case counts, 0.95 floor, capacity, metrics, thresholds, classification, or authority after primary output.",
  "successor_if_supported": {
    "experiment_family": "EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-HORIZON-035",
    "intent": "extend simultaneous fixed-capacity preservation across a longer preregistered cumulative horizon with zero-baseline scoring already defined"
  },
  "successor_if_mixed_or_negative": {
    "experiment_family": "EXP-DGR-EXTERNAL-MULTIROW-MULTIEPOCH-ATTRIBUTION-035",
    "intent": "attribute temporal target loss, zero-baseline harm, or applicable non-target eviction cost before changing fixed capacity"
  },
  "changed_paths": [
    "research/experiments/exp-dgr-external-multirow-multiepoch-zerobaseline-034.ice",
    "research/applications/plane/exp-dgr-external-multirow-multiepoch-zerobaseline-034.py",
    ".github/workflows/external-multirow-multiepoch-zerobaseline-034.yml"
  ]
}
