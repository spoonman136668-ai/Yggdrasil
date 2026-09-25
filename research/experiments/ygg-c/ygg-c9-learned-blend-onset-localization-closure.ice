TITLE: YGG-C9 Learned-Blend Interaction Onset Localization Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-C
PREREGISTRATION: 2e9d62453b77e62bcd02f482980be7e33962c5e5
PARENT_CLOSURE: a104e7a23107c56262572b0a2dcf89c07da8a263
EXECUTION_HEAD: ee7f7f58ab15c33831a7677e49f38adf188d959a
WORKFLOW_RUN_ID: 36143688978

VALIDITY
valid=true
alpha025_accepted_c7_map_exact=true
alpha025_context_slots_exact_A_C=true
alpha025_parent_reference_hash_exact=true
base_manifests_identical_across_alpha=true
factorial_and_matching_valid_each_alpha=true
learned_weight_identity_exact=true
dose_allowlist_restored_final=true
runtime_alpha_restored_final=true

RESULT
alpha=0.0625 interaction_driven=false
alpha=0.125 interaction_driven=false
alpha=0.1875 interaction_driven=true
alpha=0.25 interaction_driven=true
first_tested_interaction_alpha=0.1875
onset_classification=ONSET_BETWEEN_0125_AND_01875

At alpha=0.1875 and 0.25 the retained map is identical:
000 T, 100 F, 010 T, 001 T, 110 F, 101 T, 011 T, 111 T
with context-dependent slots A,C.

INTERPRETATION
The learned developmental interaction has a sharp onset somewhere between alpha=0.125 and alpha=0.1875 under the frozen C6 factorial design.

NEXT QUESTION
Bisect the bracket using alpha=0.15625, with exact alpha=0.125 and alpha=0.1875 anchors, to determine which half contains the onset.

BOUNDARY
No accepted source mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion.
No recursive self-modification.
