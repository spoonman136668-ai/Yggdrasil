TITLE: DG-1R-05M — Fixed-Budget Global-Distance-4 Frontier Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REPRESENTATION AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / TOPOLOGY DISTANCE
BRANCH: dg1a-ar
PARENT: DG-1R-05L

PURPOSE

DG-1R-05L established that the same fixed 20-check / 80-incidence / 128-bit budget can simultaneously provide:

- GF(2) rank 12;
- zero logical kernel;
- single-region syndrome floor 6;
- two-region syndrome floor 8;
- maximum pair co-occurrence <=2;
- global minimum positive logical syndrome weight 3.

Forty-nine 05L topologies met that frozen frontier.

DG-1R-05M asks:

IS GLOBAL MINIMUM POSITIVE LOGICAL SYNDROME WEIGHT 4
ACHIEVABLE
WITHOUT ADDING PERSISTENT STATE
OR CHANGING THE DECODER?

BOUNDARY

Synthetic software only.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL / NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains UNSPENT.

BASE REPRESENTATION

Exact frozen HYPER20 baseline:

20 checks.
12 logical regions.
80 incidences.
128 persistent bits.

Frozen logical-region degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

Maximum allowed pair co-occurrence:

2.

05L PARENT SET

Regenerate the exact DG-1R-05L family mechanically from baseline:

- exactly two atomic incidence transfers;
- four distinct affected source/target check indices;
- final arity profile:
  two arity-3,
  two arity-5,
  sixteen arity-4;
- normalized final topology deduplication;
- lexicographically smallest witness retained.

Then retain every topology satisfying the exact closed 05L primary frontier:

- rank = 12;
- nonzero logical kernel count = 0;
- maximum pair co-occurrence <=2;
- single-region floor >=6;
- two-region floor >=8;
- global minimum positive logical syndrome weight >=3.

The closed 05L result reported 49 such parent topologies.

The harness MUST regenerate this set from the frozen rules.
It must not load a hand-selected parent list.

05M CANDIDATE FAMILY — THIRD DISJOINT TRANSFER

For every regenerated 05L frontier parent:

apply exactly one additional atomic incidence transfer:

m3 = (block b, source check i, target check j)

subject to:

- b is present in source check i;
- b is absent from target check j;
- i != j;
- source check i has arity exactly 4 in the parent;
- target check j has arity exactly 4 in the parent.

Therefore the third transfer touches two checks not already altered by the parent.

Final frozen arity profile:

- three arity-3 checks;
- three arity-5 checks;
- fourteen arity-4 checks.

Consequences by construction:

- check count remains 20;
- total incidence remains 80;
- exact logical-region degree vector remains unchanged;
- six checks have odd arity.

Candidate identity is the normalized final topology.

If multiple parent / third-move paths generate the same final topology:

evaluate the final topology exactly once
and retain the lexicographically smallest canonical witness:

(
parent_05L_witness,
third_move
).

No candidate outside this frozen family may be introduced after primary execution begins.

PRIMARY ENUMERATION

For every unique 05M candidate compute exactly:

- GF(2) rank;
- nonzero logical-kernel count;
- maximum pair co-occurrence;
- minimum single-region syndrome weight;
- minimum two-region syndrome weight;
- global minimum positive logical syndrome weight across all 4095 nonzero logical masks;
- number of zero-syndrome nonzero logical masks.

DISTANCE-4 FEASIBILITY GATE

A candidate is DISTANCE4-FEASIBLE iff all are true:

- rank = 12;
- nonzero logical-kernel count = 0;
- maximum pair co-occurrence <=2;
- minimum single-region syndrome weight >=6;
- minimum two-region syndrome weight >=8;
- global minimum positive logical syndrome weight >=4.

CANDIDATE SELECTION

Among DISTANCE4-FEASIBLE candidates select exactly one using frozen ordering:

1. maximize global minimum positive logical syndrome weight;
2. maximize minimum two-region syndrome weight;
3. maximize minimum single-region syndrome weight;
4. minimize maximum pair co-occurrence;
5. lexicographically smallest canonical witness.

No holdout metric participates in primary selection.

HOLDOUT STATIC VALIDATION

For the selected candidate compare against:

- frozen HYPER20 baseline;
- frozen DG-1R-05K selected topology;
- frozen DG-1R-05L selected topology.

A. LOGICAL-ONLY GEOMETRY

Report:

- distinct logical-only syndromes;
- multiplicity histogram;
- kernel masks;
- minimum positive syndrome weight by logical-fault weight 1..12.

B. EQUAL-COST CHECK-ONLY BOUNDARY

For every check-only syndrome of Hamming weight 1..4,
enumerate all 4096 logical masks under:

cost =
logical fault count
+
residual check fault count.

For each check-only weight report:

- d=0 unique minimum;
- d=0 tied minimum;
- all minimum-cost explanations nonzero.

Frozen protection reference:

HYPER20 weight-4 all-minima-nonzero:
60 / 4845.

05K selected:
60 / 4845.

05L selected:
60 / 4845.

C. FROZEN CHECK4 INCIDENT TESTS

Use:

- block 5, first four incident checks;
- block 2, first four incident checks.

Classify true check-only explanation as:

- TRUE_EXPLANATION_UNIQUE_MINIMUM;
- TRUE_EXPLANATION_TIED_MINIMUM;
- TRUE_EXPLANATION_NOT_MINIMUM.

D. CROSS-PLANE EXACT-COLLISION LIFT

Repeat the 05J/05K/05L exact logical-versus-incident-integrity construction for P=1..4.

This remains a distinct fault-type identifiability question.

A positive topology-distance result must not be reported as solving arbitrary correlated integrity faults.

PRIMARY SIGNALS

DISTANCE4_FEASIBLE:

TRUE iff at least one DISTANCE4-FEASIBLE candidate exists.

SELECTED_FULL_RANK:

TRUE iff selected rank = 12.

SELECTED_KERNEL_FREE:

TRUE iff selected nonzero logical-kernel count = 0.

LOCAL_FLOORS_PRESERVED:

TRUE iff selected single-region floor >=6
AND selected two-region floor >=8.

PAIR_COOCCURRENCE_PRESERVED:

TRUE iff selected maximum pair co-occurrence <=2.

GLOBAL_DISTANCE_AT_LEAST_4:

TRUE iff selected global minimum positive logical syndrome weight >=4.

CHECK4_EQUAL_COST_NOT_WORSE:

TRUE iff selected weight-4 check-only all-minima-nonzero count <=60.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED:

TRUE only if no exact logical/check mimic exists for any block and P in 1..4.

A positive 05M fixed-budget distance-4 claim requires:

DISTANCE4_FEASIBLE
AND SELECTED_FULL_RANK
AND SELECTED_KERNEL_FREE
AND LOCAL_FLOORS_PRESERVED
AND PAIR_COOCCURRENCE_PRESERVED
AND GLOBAL_DISTANCE_AT_LEAST_4
AND CHECK4_EQUAL_COST_NOT_WORSE.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED is expected FALSE
and is not part of the distance-4 topology claim.

MECHANICAL ASSERTIONS

Before primary output the harness MUST assert:

- exact HYPER20 baseline;
- exact regeneration of the 05L candidate rules;
- exactly 49 regenerated 05L frontier parents;
- each third move is valid against the parent topology;
- third-move source and target both have parent arity 4;
- each final topology has 20 checks;
- each final topology has exactly 80 incidences;
- exact baseline logical-region degree vector is preserved;
- exactly three checks have arity 3;
- exactly three checks have arity 5;
- exactly fourteen checks have arity 4;
- duplicate final topologies are evaluated once;
- all 4095 nonzero logical masks are evaluated for every candidate reaching global-distance evaluation;
- holdout check-only weights 1..4 enumerate exactly 6195 patterns.

These are NON-EVIDENCE mechanical checks.

REPRODUCIBILITY

Deterministic exhaustive audit.

No RNG.
No seed family.

Execute two complete sweeps from the frozen harness.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After the first primary candidate is evaluated do not alter:

- 05L parent regeneration;
- parent eligibility rules;
- third-transfer rule;
- arity-4 source/target constraint;
- deduplication rule;
- distance-4 feasibility gate;
- selection ordering;
- holdout metrics;
- baseline references;
- CHECK4 definitions;
- cross-plane construction;
- success signals.

PLAIN-SPEAK PREREGISTERED QUESTION

05L proved we can remove the blind spot
and keep the original worst-case warning strength of three bits.

Now we are asking whether the same memory budget can do better.

We start from every one of the 49 good 05L layouts,
then make one more small participation move using two previously untouched four-region checks.

That gives six odd-sized checks
without changing:

- the number of backup slots;
- the total number of links;
- how many witnesses each logical region has;
- or the total 128 stored bits.

The target is a minimum warning strength of four bits
for every nonzero logical fault pattern,
while keeping the strong one-region and two-region protection we already have.

If no candidate reaches four,
that is useful evidence that distance 3 may be near the frontier for this constrained architecture.

If one does,
we will have strengthened the representation again without spending more persistent memory.

canonical_scientific_execution = false.
stab18_r1_touched = false.
