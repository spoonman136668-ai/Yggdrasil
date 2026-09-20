TITLE: DG-1R-05J — HYPER20 Snapshot Fault Identifiability / Syndrome-Collision Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE INFORMATION-BOUNDARY AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / IDENTIFIABILITY
BRANCH: dg1a-ar
PARENT: DG-1R-05I

PURPOSE

DG-1R-05I established that cross-bit-plane agreement is useful fault-type confidence,
but not independent truth.

It suppresses one-plane integrity masquerades while preserving the frozen two-plane
logical-repair positives.

It also misses true single-plane logical faults and remains vulnerable when integrity
damage is itself correlated across bit planes.

DG-1R-05J asks a more fundamental question:

WHICH FAULT CLASSES ARE DISTINGUISHABLE FROM THE CURRENT 128-BIT SNAPSHOT IN PRINCIPLE?

No new repair heuristic is tested here.

BOUNDARY

Synthetic software-only audit.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL / NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains UNSPENT.

REPRESENTATION

Exact frozen DG-1R-05G/05H/05I HYPER20 representation.

12 logical regions x 4 bit planes = 48 logical bits.
20 hyperchecks x 4 bit planes = 80 integrity bits.
128 persistent bits total.

Exact frozen hyperedge set:

(0,2,7,9)
(1,3,6,11)
(4,5,9,10)
(2,3,5,8)
(0,1,4,8)
(6,7,8,10)
(2,4,6,11)
(0,3,5,7)
(1,7,10,11)
(1,5,6,9)
(3,8,9,10)
(0,4,8,11)
(0,2,6,10)
(1,3,4,7)
(2,5,7,11)
(2,3,4,10)
(0,1,5,10)
(0,3,9,11)
(1,2,8,9)
(4,6,7,9)

PER-PLANE MODEL

Let H be the frozen 20 x 12 binary incidence matrix.

For one bit plane:

d = 12-bit logical-fault vector.
c = 20-bit integrity-fault vector.

Observed syndrome:

s = H d XOR c.

The decoder sees s only.
It does not see d or c.

PRIMARY AUDIT A — LOGICAL-ONLY MAP

Exhaustively enumerate all 2^12 = 4096 logical masks.

For every mask d record:

- logical fault weight;
- 20-bit syndrome H d;
- syndrome Hamming weight.

Measure:

- GF(2) rank of H;
- number and identity of nonzero logical kernel masks;
- number of distinct logical-only syndromes;
- multiplicity of logical-only syndrome collisions;
- minimum and maximum syndrome weight by logical-fault weight 1..12;
- full syndrome-weight histogram by logical-fault weight.

PRIMARY AUDIT B — EXACT CHECK-ONLY MIMIC COST

For every logical mask d:

the unique check-only vector that exactly reproduces the same syndrome is:

c_mimic = H d.

Therefore:

CHECK_MIMIC_WEIGHT(d) = popcount(H d).

Report:

- every single-logical-region mimic weight;
- all 66 two-logical-region mimic weights;
- minimum exact check-only mimic weight for each logical-fault weight;
- global minimum nonzero mimic weight;
- any zero-syndrome nonzero logical masks.

This is an information-theoretic collision statement, not a decoder heuristic.

PRIMARY AUDIT C — WEIGHTED EXPLANATION BOUNDARIES

For a syndrome s and candidate logical mask d':

residual check vector:

r = s XOR H d'.

Frozen weighted explanation cost:

C(d' | s) =
LOGICAL_COST * popcount(d')
+
CHECK_COST * popcount(r).

Enumerate all 4096 candidate logical masks exactly.

Frozen cost pairs:

COST_CHECK_1_7:
LOGICAL_COST = 7
CHECK_COST = 1.

COST_CHECK_1_6:
LOGICAL_COST = 6
CHECK_COST = 1.

COST_CHECK_1_2:
LOGICAL_COST = 2
CHECK_COST = 1.

COST_EQUAL:
LOGICAL_COST = 1
CHECK_COST = 1.

COST_CHECK_2:
LOGICAL_COST = 1
CHECK_COST = 2.

For each cost pair, classify selected frozen syndrome families as:

- TRUE_EXPLANATION_UNIQUE_MINIMUM;
- TRUE_EXPLANATION_TIED_MINIMUM;
- TRUE_EXPLANATION_NOT_MINIMUM.

Frozen selected families:

1. SINGLE_LOGICAL_D6:
one logical fault at block 5.

2. SINGLE_LOGICAL_D7:
one logical fault at block 2.

3. TWO_LOGICAL_MINPAIR:
the pair of logical regions with the minimum exact check-only mimic weight.
The harness must derive the pair mechanically from H and record it.

4. CHECK4_INCIDENT_D6:
four incident integrity faults for block 5.

5. CHECK4_INCIDENT_D7:
four incident integrity faults for block 2.

For check-only families, the true explanation is d = 0.
For logical-only families, the true explanation is the exact logical mask.

Additionally, for every check-only syndrome of Hamming weight 1..4
over all C(20,w) patterns, report under every frozen cost pair:

- fraction with d=0 as unique minimum;
- fraction with d=0 tied for minimum;
- fraction where all minimum-cost explanations have nonzero logical masks.

No threshold or ratio may be changed after execution.

PRIMARY AUDIT D — CROSS-PLANE EXACT-COLLISION LIFT

The HYPER20 state stores four independent instances of the same per-plane syndrome relation.

For every logical block b and plane count P in 1..4 construct two fault explanations:

LOGICAL_P:
logical bit b is flipped in planes 0..P-1;
no integrity faults.

CHECK_MIMIC_P:
no logical faults;
every hypercheck incident to block b is flipped in planes 0..P-1.

Assert and report whether the full 20 x 4 observed syndrome matrices are byte-identical.

Report for every b and P:

- logical fault-bit count;
- integrity fault-bit count;
- integrity channel-event count if one event may corrupt the selected planes of one check slot;
- exact syndrome equality.

This directly tests whether cross-plane agreement adds information under arbitrary correlated integrity faults,
as distinct from adding statistical confidence under an independence assumption.

MECHANICAL ASSERTIONS

The harness MUST assert before producing primary output:

- exact HYPER20 edge count = 20;
- exact degree vector = (7,7,7,7,7,6,6,7,6,7,7,6);
- maximum pair co-occurrence <= 2;
- 4096 logical masks are enumerated exactly once;
- all 66 two-region masks are enumerated exactly once;
- all check-only patterns of weights 1..4 are enumerated exactly once;
- weighted-minimum ties are preserved rather than broken arbitrarily.

These are mechanical checks, not scientific evidence.

FROZEN OUTPUT SIGNALS

SNAPSHOT_LOGICAL_ONLY_FULL_RANK:
TRUE iff rank(H) = 12.

NONZERO_LOGICAL_KERNEL:
TRUE iff any nonzero d has H d = 0.

SINGLE_REGION_EXACT_CHECK_MIMIC_FLOOR:
minimum CHECK_MIMIC_WEIGHT among the 12 weight-1 logical masks.

TWO_REGION_EXACT_CHECK_MIMIC_FLOOR:
minimum CHECK_MIMIC_WEIGHT among the 66 weight-2 logical masks.

GLOBAL_NONZERO_EXACT_CHECK_MIMIC_FLOOR:
minimum positive CHECK_MIMIC_WEIGHT over all nonzero logical masks.

CROSSPLANE_EXACT_MIMIC_EXISTS:
TRUE iff at least one CHECK_MIMIC_P construction is syndrome-identical to LOGICAL_P.

CROSSPLANE_ADDS_INFORMATION_UNDER_ARBITRARY_CORRELATION:
TRUE only if no such exact cross-plane mimic exists for any block and P in 1..4.

INTERPRETATION RULES

If two distinct fault explanations generate exactly the same syndrome,
no snapshot-only decoder can distinguish them without additional assumptions or state.

Weighted-cost results are prior-sensitive decision boundaries.
They do not remove exact information-theoretic collisions.

Cross-plane coherence may remain useful statistically even if
CROSSPLANE_ADDS_INFORMATION_UNDER_ARBITRARY_CORRELATION is FALSE.

A negative identifiability result is not a decoder failure.
It is a representation boundary.

REPRODUCIBILITY

Deterministic exhaustive audit.
No RNG.
No seed family.

Execute two complete sweeps from the frozen harness.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After first primary execution do not alter:

- hypergraph;
- fault classes;
- cost pairs;
- selected blocks;
- check-only weight range;
- cross-plane construction;
- metrics;
- classifications;
- output signals.

PLAIN-SPEAK PREREGISTERED QUESTION

The last experiment showed that asking for two bit-plane votes can stop some bad repairs,
but coordinated backup failures can still fake those votes.

This experiment stops trying new repair tricks.

Instead, it asks whether two different kinds of damage can produce exactly the same evidence.

If they can, then no smarter snapshot-only decoder can solve that case reliably,
because the information needed to tell them apart simply is not present.

We will also measure how much backup corruption is required to imitate one or two real data faults,
and whether looking across several bit planes actually creates new information
or merely gives confidence when failures happen independently.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05J IDENTIFIABILITY

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY AUDIT.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05j_identifiability_v1.py

Harness commit:

c4746d4f4ef2a1897cd96e4b4f8705aabcf491f3.

Git blob SHA:

00e6d2adcb929be43f95116c55e19d5a08f0b561.

Source SHA-256:

55d0c075a00be6c9a3677b7ca9d760743e0cac41a6c0c4574fc21fe72b5a5749.

Source bytes:

12734.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Frozen hypergraph edge count:

20.

Frozen degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

Maximum pair co-occurrence:

2.

Logical masks enumerated:

4096.

Two-region masks enumerated:

66.

Check-only weight-1-to-4 patterns:

6195.

These checks are mechanical only and are NON-EVIDENCE.

No DG-1R-05J primary output was generated before this freeze.

REPRODUCIBILITY

Two complete deterministic exhaustive sweeps.

Output SHA-256 must match exactly.

No RNG.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-05J NON-EVIDENCE CLOSURE — SNAPSHOT IDENTIFIABILITY

DATE:
2026-09-20.

STATUS:
COMPLETE /
INFORMATION-BOUNDARY MAPPED /
TWO BYTE-IDENTICAL EXHAUSTIVE SWEEPS /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

00e6d2adcb929be43f95116c55e19d5a08f0b561.

Source SHA-256:

55d0c075a00be6c9a3677b7ca9d760743e0cac41a6c0c4574fc21fe72b5a5749.

Source bytes:

12734.

OUTPUT

Sweep 1 SHA-256:

e4ee7e2996aa70f79a3fef56c56b648082e4cbf54b8ff2cfff1fa8634800a612.

Sweep 2 SHA-256:

e4ee7e2996aa70f79a3fef56c56b648082e4cbf54b8ff2cfff1fa8634800a612.

Byte-identical:

PASS.

Mechanical validity:

TRUE.

PRIMARY SIGNALS

SNAPSHOT_LOGICAL_ONLY_FULL_RANK:

FALSE.

GF(2) rank:

11 of 12.

NONZERO_LOGICAL_KERNEL:

TRUE.

The sole nonzero logical-only kernel mask is:

4095.

Blocks:

0,1,2,3,4,5,6,7,8,9,10,11.

Logical weight:

12.

Thus:

flipping the same bit plane in all 12 logical regions produces zero HYPER20 syndrome.

Distinct logical-only syndromes:

2048.

Logical masks:

4096.

Syndrome multiplicity:

all 2048 observed logical-only syndromes have multiplicity exactly 2.

MECHANISTIC CAUSE

Every frozen HYPER20 check contains exactly four logical regions.

Therefore the all-ones 12-region logical vector intersects every check with even parity.

That makes the all-region same-plane fault a structural kernel vector.

This is not a decoder defect.

It follows directly from the all-even check arity.

LOCAL EXACT CHECK-ONLY MIMIC FLOORS

SINGLE_REGION_EXACT_CHECK_MIMIC_FLOOR:

6 integrity bits.

Per-block single-region mimic weights match degree:

degree-6 blocks:
5,6,8,11 -> 6.

degree-7 blocks:
0,1,2,3,4,7,9,10 -> 7.

TWO_REGION_EXACT_CHECK_MIMIC_FLOOR:

8 integrity bits.

Minimum pair:

blocks 6 and 11.

GLOBAL_NONZERO_EXACT_CHECK_MIMIC_FLOOR:

3 integrity bits.

This global floor occurs only for larger multi-region logical patterns;
the frozen one-region and two-region local fault classes remain substantially better separated.

WEIGHTED EXPLANATION BOUNDARIES

SINGLE_LOGICAL_D6:

check/logical cost ratio 1/7:
true logical explanation NOT minimum.

ratio 1/6:
true logical explanation TIED minimum.

ratio 1/2:
true logical explanation UNIQUE minimum.

equal cost:
true logical explanation UNIQUE minimum.

check cost 2x logical:
true logical explanation UNIQUE minimum.

SINGLE_LOGICAL_D7:

ratio 1/7:
true logical explanation TIED minimum.

ratio 1/6 and above:
true logical explanation UNIQUE minimum.

CHECK4_INCIDENT_D6:

check/logical ratio 1/7:
true check-only explanation UNIQUE minimum.

ratio 1/6:
UNIQUE minimum.

ratio 1/2:
TIED minimum.

equal cost:
true check-only explanation NOT minimum.

check cost 2x logical:
true check-only explanation NOT minimum.

CHECK4_INCIDENT_D7:

ratios 1/7, 1/6, and 1/2:
true check-only explanation UNIQUE minimum.

equal cost:
true check-only explanation TIED minimum.

check cost 2x logical:
true check-only explanation NOT minimum.

Thus the DG-1R-05H/05I CHECK4 boundary is prior-sensitive exactly as expected:
the same syndrome can make a logical-plus-check explanation cheaper than the true check-only explanation
even when there is not yet an exact information-theoretic collision.

ALL CHECK-ONLY PATTERNS — EQUAL COST

Weight 1:

20 / 20 retain d=0 as unique minimum.

Weight 2:

190 / 190 retain d=0 as unique minimum.

Weight 3:

1140 / 1140 retain d=0 as unique minimum.

Weight 4:

4503 / 4845:
d=0 unique minimum.

282 / 4845:
d=0 tied for minimum.

60 / 4845:
all minimum-cost explanations have nonzero logical masks.

Fractions at weight 4:

92.94117647058824% unique correct check-only.

5.820433436532508% tied.

1.238390092879257% minimum-cost preference excludes the true check-only explanation.

At check cost 2x logical for weight-4 check-only patterns:

4005 / 4845 unique correct.

351 / 4845 tied.

489 / 4845 all minima nonzero.

This confirms that weighted minimum decoding is a prior-sensitive decision mechanism,
not an identifiability proof.

CROSS-PLANE EXACT COLLISION

CROSSPLANE_EXACT_MIMIC_EXISTS:

TRUE.

CROSSPLANE_ADDS_INFORMATION_UNDER_ARBITRARY_CORRELATION:

FALSE.

For every logical block
and every plane count P in 1..4:

a logical fault in that block across the selected planes

and

integrity faults in every incident hypercheck across the same selected planes

produce exactly the same 20 x 4 syndrome observation.

All 48 frozen constructed block/plane-count comparisons were exact.

For a degree-6 block:

P=1:
1 logical fault bit can be exactly mimicked by 6 integrity fault bits.

P=2:
2 logical fault bits can be exactly mimicked by 12 integrity fault bits.

P=3:
3 logical fault bits can be exactly mimicked by 18 integrity fault bits.

P=4:
4 logical fault bits can be exactly mimicked by 24 integrity fault bits.

If one integrity-channel event may corrupt multiple selected bit planes in the same check slot,
the exact mimic uses 6 channel events for a degree-6 block regardless of P.

Degree-7 blocks analogously require 7 channel events.

MECHANISTIC CONCLUSION

DG-1R-05I's cross-plane gate is a useful statistical confidence mechanism.

It is not an information-theoretic discriminator.

Under arbitrary correlated integrity faults,
cross-plane agreement factorizes and exact fault-type collisions remain possible.

More fundamentally,
the current all-four-region topology has an independent logical-only blind mode:
the all-region same-plane complement is invisible to syndrome.

Therefore the current HYPER20 architecture has two distinct limits:

1. TOPOLOGICAL NULLSPACE:
   all-even check arity creates a global logical blind mode.

2. FAULT-TYPE NON-IDENTIFIABILITY:
   because integrity bits directly span syndrome coordinates,
   sufficiently coordinated integrity faults can reproduce logical-fault observations exactly.

These limits must not be conflated.

The first can potentially be improved by topology without adding persistent state.

The second requires an independent source of evidence, a stronger fault model,
temporal structure, integrity-of-integrity structure, or another orthogonal constraint.

PLAIN-SPEAK INTERPRETATION

We found the line between a smarter decoder and missing information.

For small local damage, HYPER20 is actually fairly strong.
One bad data region takes six or seven corrupted backup bits to imitate exactly.
Two bad regions take at least eight.

But the current layout has a hidden global weakness:
because every backup check covers exactly four regions,
flipping the same bit across all twelve data regions cancels out perfectly.
The backup system sees nothing wrong.

There is also a second, unavoidable snapshot problem.
If enough backup bits fail in the right coordinated pattern,
they can produce exactly the same evidence as real data damage.
Looking across two, three, or four bit planes does not make that ambiguity disappear
when the backup failures themselves are allowed to coordinate.

So another static confidence cutoff cannot solve the whole problem.

The good news is that one defect is architectural and cheap to attack:
the all-even topology itself causes the global blind spot.
A mixed-arity or otherwise parity-broken topology can be tested at the same 128-bit state budget.

The harder data-versus-backup ambiguity will still require genuinely independent evidence.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05K —
PARITY-BROKEN MIXED-ARITY TOPOLOGY AUDIT.

Question:

Can the same 20 four-bit integrity slots be rewired into a mixed-arity incidence matrix that:

- restores full logical-only rank;
- removes the all-region kernel;
- preserves or improves the 6-bit single-region exact-mimic floor;
- preserves or improves the 8-bit two-region floor;
- does not worsen pair co-occurrence;
- reduces equal-cost CHECK4 false logical preference;

without adding persistent state?

This is a representation audit only.

It does not claim to solve arbitrary data-versus-integrity collision.

No post-result tuning was performed.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
