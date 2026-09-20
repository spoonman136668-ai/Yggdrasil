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


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05M GLOBAL DISTANCE-4 FRONTIER

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST 05M PRIMARY CANDIDATE METRIC EVALUATION.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05m_distance4_frontier_v1.py

Harness commit:

eab365a6627edf43de4710d1db66abc1bac46d32.

Git blob SHA:

046499ab7498b753ff1d1f85e3a6eb84bccea7ab.

Source SHA-256:

15b19de7d76cd93f67f8a63e2c7a2031abd42a4a908cedc6e69c7997b3717f64.

Source bytes:

13100.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Regenerated closed 05L frontier parents:

49.

This exactly matches the closed 05L result and is prior-result consistency,
not new 05M evidence.

Valid third-move paths from those parents:

32782.

Unique normalized 05M final topologies:

32408.

For all mechanically generated 05M final topologies:

- check count remained 20;
- total incidence remained 80;
- exact baseline degree vector was preserved;
- exactly three checks had arity 3;
- exactly three checks had arity 5;
- exactly fourteen checks had arity 4.

These are mechanical candidate-family checks only and are NON-EVIDENCE.

No 05M candidate rank,
kernel,
pair co-occurrence,
local floor,
global distance,
distance-4 feasibility,
selection,
or holdout result
was evaluated before this freeze.

REPRODUCIBILITY

Two complete deterministic exhaustive sweeps.

Serialized output SHA-256 must match exactly.

No RNG.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05M NON-EVIDENCE CLOSURE — FIXED-BUDGET GLOBAL DISTANCE 4

DATE:
2026-09-20.

STATUS:
COMPLETE /
UNIQUE DISTANCE-4 TOPOLOGY FOUND IN FROZEN FAMILY /
FULL RANK /
KERNEL FREE /
LOCAL FLOORS PRESERVED /
TWO BYTE-IDENTICAL EXHAUSTIVE SWEEPS /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

046499ab7498b753ff1d1f85e3a6eb84bccea7ab.

Source SHA-256:

15b19de7d76cd93f67f8a63e2c7a2031abd42a4a908cedc6e69c7997b3717f64.

Source bytes:

13100.

OUTPUT

Sweep 1 SHA-256:

2e5a8ab4a8eba62ef3b0d818a5b522a03bf9331d0e7c180fedfa2bbe84ba48e6.

Sweep 2 SHA-256:

2e5a8ab4a8eba62ef3b0d818a5b522a03bf9331d0e7c180fedfa2bbe84ba48e6.

Byte-identical:

PASS.

Mechanical validity:

TRUE.

PRIMARY ENUMERATION

Regenerated closed 05L frontier parents:

49.

Third-move paths:

32782.

Unique final topologies:

32408.

Candidates reaching frozen global-distance evaluation:

161.

DISTANCE4-FEASIBLE topologies:

1.

DISTANCE4_FEASIBLE:

TRUE.

SELECTED WITNESS

05L parent move 1:

block 6,
source check 19,
target check 7.

05L parent move 2:

block 8,
source check 3,
target check 14.

Third move:

block 11,
source check 6,
target check 2.

Selected arity profile:

three arity-3 checks,
three arity-5 checks,
fourteen arity-4 checks.

Persistent budget:

unchanged.

20 checks.

80 incidences.

12 logical regions.

128 persistent bits total.

SELECTED TOPOLOGY

check 0:
(0,2,7,9).

check 1:
(1,3,6,11).

check 2:
(4,5,9,10,11).

check 3:
(2,3,5).

check 4:
(0,1,4,8).

check 5:
(6,7,8,10).

check 6:
(2,4,6).

check 7:
(0,3,5,6,7).

check 8:
(1,7,10,11).

check 9:
(1,5,6,9).

check 10:
(3,8,9,10).

check 11:
(0,4,8,11).

check 12:
(0,2,6,10).

check 13:
(1,3,4,7).

check 14:
(2,5,7,8,11).

check 15:
(2,3,4,10).

check 16:
(0,1,5,10).

check 17:
(0,3,9,11).

check 18:
(1,2,8,9).

check 19:
(4,7,9).

SELECTED LOGICAL GEOMETRY

GF(2) rank:

12 of 12.

SELECTED_FULL_RANK:

TRUE.

Nonzero logical kernel masks:

0.

SELECTED_KERNEL_FREE:

TRUE.

Distinct logical-only syndromes:

4096 of 4096.

Multiplicity histogram:

4096 syndromes with multiplicity exactly 1.

Single-region minimum syndrome weight:

6.

Two-region minimum syndrome weight:

8.

LOCAL_FLOORS_PRESERVED:

TRUE.

Maximum pair co-occurrence:

2.

PAIR_COOCCURRENCE_PRESERVED:

TRUE.

Global minimum positive logical syndrome weight:

4.

GLOBAL_DISTANCE_AT_LEAST_4:

TRUE.

Minimum positive syndrome weight by logical-fault weight:

weight 1:
6.

weight 2:
8.

weight 3:
7.

weight 4:
4.

weight 5:
4.

weight 6:
4.

weight 7:
4.

weight 8:
4.

weight 9:
4.

weight 10:
6.

weight 11:
4.

weight 12:
6.

Thus every nonzero logical fault pattern produces at least four syndrome bits.

HOLDOUT — EQUAL-COST CHECK-ONLY BOUNDARY

Weights 1 through 3:

all check-only patterns retain d=0 as unique minimum.

Weight 4 selected topology:

4503 / 4845:
d=0 unique minimum.

282 / 4845:
d=0 tied minimum.

60 / 4845:
all minimum-cost explanations nonzero.

This exactly matches frozen HYPER20 baseline:

4503 unique,
282 tied,
60 all-minima nonzero.

CHECK4_EQUAL_COST_NOT_WORSE:

TRUE.

FROZEN CHECK4 INCIDENT TESTS

Degree-6 block 5:

selected:
TRUE_EXPLANATION_NOT_MINIMUM.

Degree-7 block 2:

selected:
TRUE_EXPLANATION_TIED_MINIMUM.

These match the baseline local prior-sensitive boundary.

CROSS-PLANE EXACT COLLISION

All frozen logical-versus-incident-integrity constructions remain exact.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED:

FALSE.

As preregistered,
topology distance improvement does not solve arbitrary correlated integrity-fault identifiability.

TECHNICAL INTERPRETATION

DG-1R-05M establishes that global logical syndrome distance 4 is achievable under the existing fixed representation budget and frozen local structural constraints.

The result simultaneously provides:

- rank 12;
- zero logical kernel;
- 4096 unique logical-only syndromes;
- single-region floor 6;
- two-region floor 8;
- maximum pair co-occurrence 2;
- global logical syndrome floor 4;
- unchanged frozen weight-4 check-only false-preference count.

No extra persistent state was added.
No decoder was changed.

The result is also highly selective:

only 1 of 32408 unique 05M final topologies passed the complete distance-4 gate.

That rarity matters.

It suggests the distance-4 geometry is not a generic consequence of merely adding more odd-arity checks.
It requires a specific arrangement of the preserved witness budget.

Therefore the representation research has reached a meaningful design point:

the original HYPER20 budget was sufficient for stronger observability than its initial topology exposed.

The next scientific question is transfer:

does the static distance-4 improvement produce better dynamic localization and repair under the already-frozen decoder family,
or is it mainly a static coding-theoretic advantage?

PLAIN-SPEAK INTERPRETATION

We found the stronger layout.

Out of more than thirty-two thousand layouts in this frozen search,
only one did everything we asked.

It uses exactly the same amount of stored backup information as before,
but now every possible nonzero logical fault creates at least four warning bits.

Nothing is invisible.
Nothing falls to the weaker two-bit warning seen in 05K.
The one-region and two-region protection stays at six and eight warning bits.

And we did not add memory or invent a smarter decoder to get there.

That means the original storage budget was not the limiting factor.
The arrangement of the same information was.

The important caution is that this is still a representation result.
Perfectly coordinated backup failures can still fake logical damage.

So the next test should stop optimizing the matrix in isolation
and ask whether this one stronger layout actually helps the existing repair system behave better over time.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05N —
DISTANCE-4 TOPOLOGY DYNAMIC REPAIR TRANSFER AUDIT.

Question:

Using the exact frozen 05M topology
and the already-established DG-1R-05H / 05I decoder family,
does stronger static logical separation improve:

- fault localization;
- false-repair suppression;
- logical recovery;
- distributed multi-region repair;

under the same dynamic worlds and damage families,
without changing decoder logic,
persistent-state budget,
or repair timing?

The audit should compare:

- original HYPER20;
- frozen 05L distance-3 selected topology;
- frozen 05M distance-4 topology;

under identical disjoint worlds.

No new repair heuristic is justified before that transfer question is answered.

No post-result tuning was performed.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
