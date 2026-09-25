TITLE: YGG-C9 Learned-Blend Interaction Onset Localization Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: a104e7a23107c56262572b0a2dcf89c07da8a263
PARENT_EXPERIMENT: YGG-C8
SCIENTIFIC_PARENT: YGG-C6 / LU-2V

QUESTION
At what sub-0.25 learned-control blend does the A/C resource-pressure interaction first appear under the exact frozen C6 factorial lesion design?

NORTH-STAR TARGET
Locate the control-strength boundary of the learned developmental reorganization mechanism before integration or broader scaling.

FROZEN
- exact accepted LU-2V learned weights;
- exact ten C6 manifests;
- exact C6 L10 base and transition cells A/B/C;
- exact eight factorial lesion conditions;
- exact task, arrivals, programs, corruption, anchors, horizon, recovery semantics, matching, service capacity, seeds, and retention definition;
- no retraining or online adaptation;
- duplicate complete execution.

SCIENTIFIC CHANGE
Vary only the runtime convex learned-control blend coefficient.

Test exactly:
alpha=0.0625
alpha=0.125
alpha=0.1875
alpha=0.25

The alpha=0.25 condition is the accepted C7/C8 anchor.

INTERACTION CLASSIFICATION
For each alpha use the exact C6 rule:
- path reproduced iff 000=true,100=false,110=false,111=true;
- a slot is context-dependent iff its paired Boolean effects vary by background;
- INTERACTION_DRIVEN iff the path reproduces and at least one slot is context-dependent.

ANCHOR GATE
At alpha=0.25:
retained map must exactly equal:
000=true
100=false
010=true
001=true
110=false
101=true
011=true
111=true

classification must be INTERACTION_DRIVEN and context-dependent slots must be exactly A,C.

ONSET CLASSIFICATION
Let the first tested interaction-driven alpha be a*.

If a*=0.0625:
ONSET_AT_OR_BELOW_00625

If a*=0.125:
ONSET_BETWEEN_00625_AND_0125

If a*=0.1875:
ONSET_BETWEEN_0125_AND_01875

If a*=0.25:
ONSET_BETWEEN_01875_AND_025

Any other valid deterministic pattern:
OTHER_VALID_PATTERN

REPORT
For every alpha:
- retained map;
- interaction classification;
- context-dependent slots;
- paired Boolean effects;
- L8 parent output hash;
- completion/stream/maturity summaries;
- duplicate evidence hash.
Also report first tested interaction alpha and onset classification.

VALIDITY
- alpha levels exact and ordered;
- exact C6 factorial lesions at every alpha;
- non-lesion manifest lineage exact;
- learned weight identity exact;
- matching integrity exact;
- duplicate execution byte-identical at every alpha;
- runtime alpha restored after every condition;
- alpha=0.25 accepted map exact;
- alpha=0.25 context slots exactly A,C;
- alpha=0.25 parent reference hash exact.

SUCCESS
YGG_C9_LEARNED_BLEND_ONSET_LOCALIZATION=true iff all validity gates pass and one preregistered onset category is produced.
No particular scientifically valid onset category is required.

FAILURE
Do not change alpha levels, lesions, weights, thresholds, manifests, seeds, task semantics, or classification rules after observing results.

BOUNDARY
No accepted LU-2V mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion from C9 alone.
No recursive self-modification.
No external runtime modification.
