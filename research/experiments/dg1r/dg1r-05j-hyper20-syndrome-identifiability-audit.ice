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
