TITLE: DG-1R-05L — Fixed-Budget Topology Distance Frontier Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REPRESENTATION AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / TOPOLOGY DISTANCE
BRANCH: dg1a-ar
PARENT: DG-1R-05K

PURPOSE

DG-1R-05K showed that one incidence transfer can:
- restore GF(2) rank 12;
- remove the HYPER20 logical kernel;
- preserve the frozen single-region floor 6;
- preserve the frozen two-region floor 8;
- preserve maximum pair co-occurrence <=2;
- leave the CHECK4 equal-cost holdout no worse.

But the selected one-transfer topology reduced the global minimum positive logical syndrome weight
from baseline 3 to 2.

DG-1R-05L asks:

CAN THE SAME
20 CHECKS,
80 INCIDENCES,
12 LOGICAL REGIONS,
AND 128 PERSISTENT BITS

ACHIEVE:

FULL RANK
AND
KERNEL-FREE LOGICAL OBSERVABILITY
AND
THE EXISTING LOCAL FLOORS
AND
GLOBAL MINIMUM POSITIVE SYNDROME WEIGHT >=3

WITHOUT A DECODER CHANGE?

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

BASELINE

Exact frozen HYPER20 representation.

20 checks.
12 logical regions.
80 incidences.

Degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

Baseline facts from closed 05J:

rank:
11.

kernel:
all-region mask 4095.

single-region floor:
6.

two-region floor:
8.

maximum pair co-occurrence:
2.

global minimum positive logical syndrome weight:
3.

05K selected facts:

rank:
12.

kernel:
none.

single-region floor:
6.

two-region floor:
8.

maximum pair co-occurrence:
2.

global minimum positive logical syndrome weight:
2.

STRUCTURAL FACT

For the all-region same-plane logical vector,
syndrome weight equals the number of odd-arity checks.

Because total incidence is even,
the count of odd-arity checks must be even.

The 05K one-transfer family creates exactly two odd checks:
one arity 3 and one arity 5.

Therefore its former global blind mode becomes a weight-2 syndrome by construction.

DG-1R-05L expands the topology family minimally to four odd checks.

CANDIDATE FAMILY — TWO DISJOINT INCIDENCE TRANSFERS

Begin from exact HYPER20.

An atomic move is:

(block b, source check i, target check j)

such that:
- b is present in source i;
- b is absent from target j;
- i != j.

A 05L candidate consists of exactly two atomic moves:

m1 = (b1,i1,j1)
m2 = (b2,i2,j2)

with frozen structural constraints:

- i1, j1, i2, j2 are four distinct check indices;
- applying both moves creates no duplicate logical region inside any check;
- both source checks have final arity 3;
- both target checks have final arity 5;
- the other 16 checks retain arity 4;
- check count remains 20;
- total incidence remains 80;
- every logical-region degree remains exactly the baseline degree vector.

Candidate identity is the normalized final topology.

If multiple move pairs produce the same final topology,
evaluate that topology exactly once and retain the lexicographically smallest canonical move-pair witness.

No candidate outside this frozen family may be introduced after primary execution begins.

PRIMARY ENUMERATION

For every unique candidate topology compute exactly:

- GF(2) rank;
- nonzero logical-kernel count;
- maximum pair co-occurrence;
- minimum single-region syndrome weight;
- minimum two-region syndrome weight;
- global minimum positive syndrome weight across all 4095 nonzero logical masks;
- number of zero-syndrome nonzero logical masks.

PRIMARY FRONTIER GATE

A candidate is FRONTIER-FEASIBLE iff all are true:

- rank = 12;
- nonzero logical-kernel count = 0;
- maximum pair co-occurrence <=2;
- minimum single-region syndrome weight >=6;
- minimum two-region syndrome weight >=8;
- global minimum positive logical syndrome weight >=3.

CANDIDATE SELECTION

Among FRONTIER-FEASIBLE candidates choose exactly one using frozen ordering:

1. maximize global minimum positive syndrome weight;
2. maximize minimum two-region syndrome weight;
3. maximize minimum single-region syndrome weight;
4. minimize maximum pair co-occurrence;
5. lexicographically smallest canonical move-pair witness.

No holdout metric participates in primary selection.

HOLDOUT STATIC VALIDATION

For the selected candidate compare against:
- frozen HYPER20 baseline;
- frozen 05K selected topology.

A. LOGICAL-ONLY GEOMETRY

Report:
- distinct logical-only syndromes;
- multiplicity histogram;
- minimum positive syndrome weight by logical-fault weight 1..12;
- kernel masks.

B. EQUAL-COST CHECK-ONLY BOUNDARY

For every check-only syndrome of Hamming weight 1..4,
enumerate all 4096 logical masks under:

cost =
logical fault count
+
residual check fault count.

Report for each check-only weight:
- d=0 unique minimum;
- d=0 tied minimum;
- all minimum-cost explanations nonzero.

Frozen protection reference:

HYPER20 weight-4 all-minima-nonzero:
60 / 4845.

05K selected weight-4 all-minima-nonzero:
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

Repeat the 05J/05K logical-versus-incident-integrity construction for P=1..4.

This is expected to remain an information-theoretic fault-type ambiguity.

05L must not claim that topology alone solves arbitrary correlated integrity faults.

PRIMARY SIGNALS

DISTANCE_FRONTIER_FEASIBLE:

TRUE iff at least one FRONTIER-FEASIBLE candidate exists.

SELECTED_FULL_RANK:

TRUE iff selected rank = 12.

SELECTED_KERNEL_FREE:

TRUE iff selected nonzero logical-kernel count = 0.

LOCAL_FLOORS_PRESERVED:

TRUE iff selected single-region floor >=6
AND selected two-region floor >=8.

PAIR_COOCCURRENCE_PRESERVED:

TRUE iff selected maximum pair co-occurrence <=2.

GLOBAL_DISTANCE_AT_LEAST_BASELINE:

TRUE iff selected global minimum positive syndrome weight >=3.

GLOBAL_DISTANCE_IMPROVED_OVER_BASELINE:

TRUE iff selected global minimum positive syndrome weight >3.

CHECK4_EQUAL_COST_NOT_WORSE:

TRUE iff selected weight-4 check-only all-minima-nonzero count <=60.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED:

TRUE only if no exact logical/check mimic exists for any block and P=1..4.

A positive 05L topology-frontier claim requires:

DISTANCE_FRONTIER_FEASIBLE
AND SELECTED_FULL_RANK
AND SELECTED_KERNEL_FREE
AND LOCAL_FLOORS_PRESERVED
AND PAIR_COOCCURRENCE_PRESERVED
AND GLOBAL_DISTANCE_AT_LEAST_BASELINE
AND CHECK4_EQUAL_COST_NOT_WORSE.

GLOBAL_DISTANCE_IMPROVED_OVER_BASELINE is reported separately.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED is expected FALSE
and is not part of the topology-frontier claim.

MECHANICAL ASSERTIONS

Before primary output the harness MUST assert:

- exact HYPER20 baseline;
- each atomic move is valid against baseline membership;
- each candidate uses four distinct source/target check indices;
- each final candidate has 20 checks;
- each final candidate has exactly 80 incidences;
- exact baseline degree vector is preserved;
- exactly two checks have arity 3;
- exactly two checks have arity 5;
- exactly sixteen checks have arity 4;
- duplicate final topologies are evaluated once;
- all 4095 nonzero logical masks are evaluated for every primary candidate that reaches global-distance evaluation;
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

- candidate family;
- four-distinct-check constraint;
- deduplication rule;
- frontier gate;
- selection ordering;
- holdout metrics;
- baseline references;
- CHECK4 definitions;
- cross-plane construction;
- success signals.

PLAIN-SPEAK PREREGISTERED QUESTION

05K proved we can remove the invisible global fault,
but the smallest possible parity break made that fault show up in only two backup checks.

This experiment makes the next-smallest structural change:
two independent participation moves instead of one.

That creates four odd-sized backup checks while keeping:
the same 20 backup slots,
the same 80 total region-to-check links,
the same number of witnesses per region,
and the same 128 stored bits.

The goal is to see whether we can keep the global blind spot gone
without weakening the worst-case warning strength below the original HYPER20 level.

We are still not changing the decoder
and we are still not claiming topology can distinguish data damage
from perfectly coordinated backup damage.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05L TOPOLOGY DISTANCE FRONTIER

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY TOPOLOGY METRIC EVALUATION.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05l_topology_distance_frontier_v1.py

Harness commit:

ecd48585f6e6eea3521211b3680f4a68361ed742.

Git blob SHA:

c388b95f1c83609bf31221ab71285befa2c02848.

Source SHA-256:

6bee913941c0d87c20d333f0a6176284f91af341371b74243b20f22d995ea980.

Source bytes:

12412.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Atomic baseline-valid moves:

1064.

Structurally valid unordered move pairs with four distinct affected checks:

455924.

Unique normalized final topologies:

437360.

For every structurally enumerated final topology:
- check count remained 20;
- total incidence remained 80;
- exact baseline degree vector was preserved;
- exactly two checks had arity 3;
- exactly two checks had arity 5;
- exactly sixteen checks had arity 4.

These are mechanical candidate-family checks only and are NON-EVIDENCE.

No candidate rank,
kernel,
pair-cooccurrence result,
local floor,
global distance,
frontier feasibility,
selection,
or holdout result
was computed before this freeze.

REPRODUCIBILITY

Two complete deterministic exhaustive sweeps.

Serialized output SHA-256 must match exactly.

No RNG.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05L NON-EVIDENCE CLOSURE — FIXED-BUDGET TOPOLOGY DISTANCE FRONTIER

DATE:
2026-09-20.

STATUS:
COMPLETE /
FULL-RANK KERNEL-FREE TOPOLOGY FOUND /
BASELINE GLOBAL DISTANCE RESTORED /
LOCAL FLOORS PRESERVED /
TWO BYTE-IDENTICAL EXHAUSTIVE SWEEPS /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

c388b95f1c83609bf31221ab71285befa2c02848.

Source SHA-256:

6bee913941c0d87c20d333f0a6176284f91af341371b74243b20f22d995ea980.

Source bytes:

12412.

OUTPUT

Sweep 1 SHA-256:

934e2ac6abe12f2a9db6d3cc99bca93aa781f542826d3a2f8d00343b76724419.

Sweep 2 SHA-256:

934e2ac6abe12f2a9db6d3cc99bca93aa781f542826d3a2f8d00343b76724419.

Byte-identical:

PASS.

Mechanical validity:

TRUE.

PRIMARY ENUMERATION

Atomic moves:

1064.

Structurally valid two-move pairs with four distinct affected checks:

455924.

Unique normalized final topologies:

437360.

Candidates reaching frozen global-distance evaluation:

107.

FRONTIER-FEASIBLE topologies:

49.

DISTANCE_FRONTIER_FEASIBLE:

TRUE.

SELECTED WITNESS

Move 1:

block 1,
source check 8,
target check 14.

Move 2:

block 5,
source check 16,
target check 11.

Selected arity profile:

two arity-3 checks,
two arity-5 checks,
sixteen arity-4 checks.

Persistent budget:

unchanged.

20 checks.

80 incidences.

12 logical regions.

128 persistent bits total.

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

GLOBAL DISTANCE

Frozen HYPER20 baseline global minimum positive logical syndrome weight:

3.

Frozen DG-1R-05K selected topology:

2.

DG-1R-05L selected topology:

3.

GLOBAL_DISTANCE_AT_LEAST_BASELINE:

TRUE.

GLOBAL_DISTANCE_IMPROVED_OVER_BASELINE:

FALSE.

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
3.

weight 6:
4.

weight 7:
4.

weight 8:
3.

weight 9:
4.

weight 10:
6.

weight 11:
4.

weight 12:
4.

The old all-region kernel is therefore not merely made weakly visible.
Under the selected 05L topology, the all-region same-plane fault has syndrome weight 4.

The global floor of 3 is instead attained by some weight-5 and weight-8 logical patterns.

HOLDOUT — EQUAL-COST CHECK-ONLY BOUNDARY

Weights 1 through 3:

all check-only patterns retain d=0 as unique minimum.

Weight 4 selected topology:

4502 / 4845:
d=0 unique minimum.

283 / 4845:
d=0 tied minimum.

60 / 4845:
all minimum-cost explanations nonzero.

Frozen HYPER20 baseline:

4503 unique,
282 tied,
60 all-minima nonzero.

Frozen 05K selected:

4504 unique,
281 tied,
60 all-minima nonzero.

CHECK4_EQUAL_COST_NOT_WORSE:

TRUE.

The frozen false-logical-preference count remains exactly 60 / 4845.

FROZEN CHECK4 INCIDENT TESTS

Degree-6 block 5:

selected:
TRUE_EXPLANATION_NOT_MINIMUM.

baseline:
TRUE_EXPLANATION_NOT_MINIMUM.

05K:
TRUE_EXPLANATION_NOT_MINIMUM.

Degree-7 block 2:

selected:
TRUE_EXPLANATION_TIED_MINIMUM.

baseline:
TRUE_EXPLANATION_TIED_MINIMUM.

05K:
TRUE_EXPLANATION_TIED_MINIMUM.

The known local prior-sensitive boundary is unchanged.

CROSS-PLANE EXACT COLLISION

All frozen logical-versus-incident-integrity constructions remain exact.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED:

FALSE.

This remains an information-theoretic fault-type ambiguity and was not a 05L success criterion.

TECHNICAL INTERPRETATION

DG-1R-05L establishes that the 05K distance-2 tradeoff was not forced by the fixed 20-check / 80-incidence / 128-bit budget.

Within a bounded two-transfer mixed-arity family,
49 topologies jointly satisfy:

- rank 12;
- zero logical kernel;
- single-region floor >=6;
- two-region floor >=8;
- maximum pair co-occurrence <=2;
- global minimum positive logical syndrome weight >=3.

The selected topology exactly restores the original HYPER20 global distance of 3 while eliminating HYPER20's rank-11 blind mode.

Therefore:

KERNEL ELIMINATION
AND
BASELINE WORST-CASE LOGICAL DETECTION DISTANCE

can coexist at the same persistent-state budget.

However:

the bounded 05L family did not produce a selected global distance above 3,
and the deeper logical-versus-integrity exact-collision family remains untouched.

The representation frontier is therefore now:

topological observability is materially improvable without more persistent bits,
but stronger distance and independent fault-type evidence remain separate objectives.

PLAIN-SPEAK INTERPRETATION

This is the topology result we were looking for after 05K.

We do not have to choose between:
seeing every logical fault at all,
and keeping the original worst-case warning strength.

With two tiny rewiring moves,
we found 49 layouts that remove the invisible global fault
while keeping the original local protection and the original worst-case distance.

The chosen layout makes every one of the 4096 logical fault patterns distinct.

It also keeps:
one-region damage at least six warning bits away,
two-region damage at least eight warning bits away,
and the overall worst case at three warning bits,
which matches the original system instead of dropping to two like 05K.

What it does not do is make corrupted backup information magically trustworthy.
If backup failures coordinate perfectly,
they can still imitate real data damage.

So topology has now fixed the structural blind spot without extra memory.
The next question is whether the same fixed budget can push the minimum distance above 3,
or whether distance 3 is the practical frontier under the existing degree and pair-overlap constraints.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05M —
FIXED-BUDGET GLOBAL-DISTANCE UPPER-BOUND / FRONTIER AUDIT.

Question:

Under the same:

- 20 checks;
- 80 incidences;
- 12 logical regions;
- exact frozen degree vector;
- maximum pair co-occurrence <=2;
- single-region floor >=6;
- two-region floor >=8;
- rank 12;
- kernel-free constraint;

is global minimum positive logical syndrome weight 4 achievable in a materially broader bounded topology family?

The next experiment should test the feasibility boundary directly,
not introduce a new decoder.

No post-result tuning was performed.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
