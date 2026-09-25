TITLE: YGG-C8 Learned-Blend Interaction Dose Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: c19a8f5bb5f0f446bf6b09dbd711b41b58ecbb4a
PARENT_EXPERIMENT: YGG-C7
SCIENTIFIC_PARENT: YGG-C6 / LU-2V

QUESTION
Is the A/C resource-pressure interaction isolated by C7 dependent on the magnitude of the learned U blend, and is the accepted U_A25 interaction map stable when learned-control strength is increased?

NORTH-STAR TARGET
Identify the mechanism behind non-monotonic resource-pressure reorganization before broader scaling or integration.

FROZEN
- exact accepted LU-2V weights and task semantics;
- exact ten C6 primary manifests;
- exact C6 L10 base and transition cells A/B/C;
- exact eight C6 factorial lesion conditions;
- exact task, arrivals, programs, corruption, anchors, horizon, recovery, service capacity, and seeds;
- exact retention definition;
- exact learned weights;
- no retraining or adaptation;
- duplicate complete execution.

SCIENTIFIC CHANGE
Vary only the runtime convex-blend coefficient used by the learned U arm.

Test exactly:
alpha=0.00
alpha=0.25
alpha=0.50

The fixed A0 arm remains descriptive and unchanged.
The learned weight bytes remain exact and frozen.
No model weights, observations, task semantics, lesions, or thresholds change.

ANCHOR
alpha=0.25 must exactly reproduce the accepted C7 A25 retained map:
000 T
100 F
010 T
001 T
110 F
101 T
011 T
111 T

For each alpha, evaluate all eight factorial lesion conditions and classify the learned-arm map using the exact C6 interaction rule:
- path reproduced iff 000=true,100=false,110=false,111=true;
- a slot is context-dependent iff its paired Boolean effects vary by background;
- INTERACTION_DRIVEN iff the path reproduces and at least one slot is context-dependent.

PRIMARY CLASSIFICATION
Report:
- alpha0 classification and retained map;
- alpha025 classification and retained map;
- alpha050 classification and retained map;
- whether alpha0 and alpha025 maps differ;
- whether alpha025 and alpha050 maps are identical;
- context-dependent slots and paired effects at each alpha.

Then assign one descriptive mechanism category:
BLEND_REQUIRED_STABLE:
alpha0 is not interaction-driven; alpha025 and alpha050 are interaction-driven with identical maps and context-dependent slots.

BLEND_REQUIRED_DOSE_MODULATED:
alpha0 is not interaction-driven; alpha025 and alpha050 are interaction-driven but their maps or context-dependent slots differ.

THRESHOLD_ABOVE_025:
alpha0 and alpha025 are not interaction-driven; alpha050 is interaction-driven.

INTERACTION_AT_ZERO_BLEND:
alpha0 is interaction-driven.

INTERACTION_LOST_AT_050:
alpha025 is interaction-driven and alpha050 is not.

OTHER_VALID_PATTERN:
any other valid deterministic pattern.

VALIDITY
- exact alpha levels only;
- alpha=0.25 reproduces accepted C7 map exactly;
- C6 lesion sets exact at every alpha;
- non-lesion manifest lineage exact;
- learned weight identity unchanged;
- matching integrity exact;
- duplicate complete execution byte-identical for each alpha;
- runtime alpha restored after each condition.

SUCCESS
YGG_C8_LEARNED_BLEND_INTERACTION_DOSE=true iff evidence is valid and one preregistered mechanism category is produced.
No particular category is required.

FAILURE
Invalid lineage, failure of alpha=.25 to reproduce accepted C7, changed weights, nondeterministic duplicate execution, or unregistered alpha is experiment invalidity.
A surprising valid category is a scientific result and must not be retuned.

BOUNDARY
No accepted LU-2V mutation.
No shared-baseline promotion from C8 alone.
No online adaptation.
No recursive self-modification.
No external runtime modification.
