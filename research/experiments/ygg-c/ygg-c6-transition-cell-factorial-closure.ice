TITLE: YGG-C6 Transition-Cell Factorial Interaction Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-C
PREREGISTRATION: bd9b7ee416868afb2cca7ec2804b1744b522fce8
PARENT_CLOSURE: 577676f3b5129a6c602d1a1ced66b515cdae80c7
EXECUTION_HEAD: 7e5625aacd04b10292ae490cf3556f5c93ece3fd
WORKFLOW_RUN_ID: 36121823302
DUPLICATE_SHA256: a8c9f9e0e8737cb5dbb4d6a20a05d4decf809a18ca8e337b4128b6b99ea0129e

VALIDITY
valid=true
mechanistic_classification_valid=true
duplicate_complete_execution_byte_identical=true
factorial_lesion_sets_exact=true
nonlesion_manifest_fields_frozen=true
parent_reference_hash_exact=true
all_matching_integrity=true

QUALIFICATION
YGG_C6_TRANSITION_INTERACTION=true
c5_path_reproduced=true
classification=INTERACTION_DRIVEN
context_dependent_slots=A,C

RETAINED BY CONDITION
000=true
100=false
010=true
001=true
110=false
101=true
011=true
111=true

PAIRED BOOLEAN EFFECTS
A:
000 -> 100 = -1
010 -> 110 = -1
001 -> 101 = 0
011 -> 111 = 0

B:
000 -> 010 = 0
100 -> 110 = 0
001 -> 011 = 0
101 -> 111 = 0

C:
000 -> 001 = 0
100 -> 101 = +1
010 -> 011 = 0
110 -> 111 = +1

INTERPRETATION
The C5 L10-to-L13 resource-pressure transition is not a scalar lesion-count threshold.
Transition slot A is harmful only when C is absent.
Transition slot C is restorative only when A is present.
Transition slot B is neutral in every factorial background.
The apparent recovery after additional resource loss therefore reflects context-dependent reorganization under the A/C lesion interaction.

NEXT QUESTION
Repeat the exact C6 factorial separately under U_A0 and U_A25 and compare the Boolean interaction structure.
This distinguishes an interaction intrinsic to the fixed substrate/task geometry from one created or modulated by the learned developmental U_A25 dynamics.

BOUNDARY
Do not retune C6 subsets, ranking, retention criteria, task, seeds, or thresholds.
No accepted LU-2V mutation.
No shared-baseline promotion from C6 alone.
No online adaptation.
No recursive self-modification.
No external runtime modification.
