TITLE: YGG-C6 Transition-Cell Factorial Interaction Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 577676f3b5129a6c602d1a1ced66b515cdae80c7
PARENT_EXPERIMENT: YGG-C5
SCIENTIFIC_PARENT: YGG-C3 / LU-2V
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc

QUESTION
Is the C5 L10-retained -> L11-failed -> L12-failed -> L13-retained transition caused by a single directional transition-cell effect, or by context-dependent interaction among the three deterministic hash-ranked lesion additions between L10 and L13?

FROZEN
- exact accepted LU-2V source, weights, alpha, ten primary manifests, task, arrivals, programs, corruption, anchors, horizon, recovery semantics, and A0/A25 arms;
- exact C3/C5 deterministic hash ranking:
  h64("YGG-C3-RESOURCE-PRESSURE", seed, cell), then cell index;
- exact inherited L8 lesion set;
- exact C5 L10 base lesion set;
- exact C3 retention criteria relative to L8;
- exact seeds and duplicate execution discipline;
- no model, scheduler, service-capacity, load, horizon, or learned-authority change.

TRANSITION CELLS
For each replicate independently:
- A = the 11th lesion cell: the first ranked cell added after L10;
- B = the 12th lesion cell: the second ranked cell added after L10;
- C = the 13th lesion cell: the third ranked cell added after L10.

The physical cell ids may differ by replicate, but A/B/C are frozen by their rank positions under the same deterministic C3 ordering.

FACTORIAL CONDITIONS
Evaluate all eight subsets added to exact L10:
000 = L10
100 = L10 + A
010 = L10 + B
001 = L10 + C
110 = L10 + A + B
101 = L10 + A + C
011 = L10 + B + C
111 = L10 + A + B + C

No condition may use any lesion cell outside exact L10 plus {A,B,C}.

PRIMARY REPRODUCTION GATE
The original C5 path must reproduce:
000 retained=true
100 retained=false
110 retained=false
111 retained=true

If this path does not reproduce, the run is invalid for mechanistic classification.

INTERACTION CLASSIFICATION
For each transition slot X in {A,B,C}, compute its four paired Boolean retention effects over backgrounds that do not contain X:
effect = retained(background + X) - retained(background)
where true=1 and false=0.

A slot is context-dependent iff its four effects are not all identical.
The transition is INTERACTION_DRIVEN iff:
- the primary C5 path reproduces; and
- at least one of A/B/C is context-dependent.

The transition is SINGLE_DIRECTION_OR_ADDITIVE iff:
- the primary C5 path reproduces; and
- none of A/B/C is context-dependent.

REPORT
For every subset:
- exact lesion set per replicate;
- lesion cardinality;
- aggregate A0/A25 completion area;
- A25 retention ratio vs exact L8;
- correct, incorrect, expired, backlog;
- maturity and matching integrity;
- stream non-collapse;
- retained boolean.

Also report:
- paired retention effects for A, B, C;
- context-dependent slots;
- final interaction classification.

VALIDITY
- exact ten frozen parent manifests;
- exact L8 and L10 lineage;
- A/B/C equal the exact next three C3 hash-ranked cells after L10 for every seed;
- all eight conditions contain only L10 plus their declared subset;
- condition cardinalities are 10 + subset size;
- non-lesion manifest fields frozen;
- L8 parent evidence SHA256 equals 7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1;
- matching integrity exact;
- duplicate complete execution byte-identical.

FAILURE
Failure to support interaction-driven behavior is a valid scientific result.
Do not change subset definitions, ranking, retention criteria, seeds, task, or classification after observing results.

INTERPRETATION
INTERACTION_DRIVEN:
The non-monotonic resource-pressure transition reflects context-dependent reorganization under specific lesion combinations rather than a scalar resource threshold.

SINGLE_DIRECTION_OR_ADDITIVE:
The transition can be explained without higher-order context dependence, narrowing the mechanism to one or more directional lesion-slot effects.

BOUNDARY
No accepted LU-2V mutation.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
No external runtime modification.
