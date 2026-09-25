TITLE: YGG-C7 Paired-Arm Transition Interaction Origin Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: d1bc71b54b0954da561f5ff07a70d00b4cd628b2
PARENT_EXPERIMENT: YGG-C6
SCIENTIFIC_PARENT: YGG-C3 / LU-2V
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Is the context-dependent A/C lesion interaction established by YGG-C6 intrinsic to the fixed substrate/task geometry, specific to the learned U_A25 developmental arm, or modulated by that learned arm?

FROZEN
- exact accepted LU-2V source, weights, alpha, ten primary manifests, task, arrivals, programs, corruption, anchors, horizon, recovery semantics, and paired A0/A25 execution;
- exact C6 L10 base and deterministic A/B/C transition-cell identities for every replicate;
- exact eight C6 factorial conditions 000,100,010,001,110,101,011,111;
- exact C3 retention criteria, now evaluated separately per arm against that arm's exact L8 parent reference;
- exact seeds and duplicate execution discipline;
- no model, scheduler, service capacity, load, horizon, lesion set, or learned-authority change.

ARM-SPECIFIC RETENTION
For each arm independently and each factorial condition, retained=true iff:
- aggregate correct-completion area >= 90% of the matched exact L8 parent area for that same arm;
- incorrect_done total == 0;
- matching duplicate cell/request violations == 0;
- maturity passes in every world;
- stream non-collapse relative to that arm's exact L8 parent:
  for every matched replicate/phase/stream where L8 completes at least 4 requests,
  the factorial condition completes at least 75% of that matched L8 count.

ARM-SPECIFIC INTERACTION
For each arm independently:
- compute the same four paired Boolean retention effects for each slot A/B/C used by C6;
- a slot is context-dependent iff its four effects are not all identical;
- arm classification is INTERACTION_DRIVEN iff its C6 path
  000=true,100=false,110=false,111=true
  reproduces and at least one slot is context-dependent;
- otherwise report PATH_NOT_REPRODUCED or SINGLE_DIRECTION_OR_ADDITIVE exactly as in C6.

PRIMARY ORIGIN CLASSIFICATION
After the two arm classifications are frozen:
SUBSTRATE_SHARED_EXACT:
- both arms are INTERACTION_DRIVEN; and
- retained_by_condition is identical; and
- context-dependent slot sets are identical; and
- all paired Boolean effects are identical.

ARM_MODULATED:
- both arms are INTERACTION_DRIVEN but any retained condition, context-dependent slot, or paired effect differs.

A25_INTERACTION_ONLY:
- U_A25 is INTERACTION_DRIVEN and U_A0 is not.

A0_INTERACTION_ONLY:
- U_A0 is INTERACTION_DRIVEN and U_A25 is not.

NEITHER_INTERACTION:
- neither arm is INTERACTION_DRIVEN.

PRIMARY VALIDITY / REPRODUCTION
- U_A25 arm must exactly reproduce the accepted C6 retained-by-condition map:
  000 T, 100 F, 010 T, 001 T, 110 F, 101 T, 011 T, 111 T;
- exact C6 factorial lesion sets per replicate;
- exact non-lesion manifest lineage;
- exact L8 parent lineage;
- matching integrity exact;
- duplicate complete execution byte-identical.

REPORT
For every arm and condition:
- retained boolean and all component gates;
- aggregate completion area and ratio vs same-arm L8;
- stream non-collapse;
- correct, incorrect, expired, backlog;
- maturity and matching integrity.
Also report each arm's paired effects, context-dependent slots, interaction classification, and the final origin classification.

SUCCESS
YGG_C7_PAIRED_ARM_INTERACTION_ORIGIN=true iff:
- evidence is valid;
- U_A25 exactly reproduces accepted C6;
- a primary origin classification is produced under the preregistered rules.
No particular origin category is required for scientific success.

FAILURE
Invalid lineage, failure to reproduce accepted C6 in U_A25, or nondeterministic duplicate execution is an invalid/failed experiment.
Any valid origin category is a scientific result and must not be retuned.

BOUNDARY
No accepted LU-2V mutation.
No shared-baseline promotion from C7 alone.
No online adaptation.
No recursive self-modification.
No external runtime modification.
