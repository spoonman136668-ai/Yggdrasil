TITLE: DG-1R-05L — Fixed-Budget Double-Transfer Topology Distance Frontier Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REPRESENTATION AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / TOPOLOGY
BRANCH: dg1a-ar
PARENT: DG-1R-05K

PURPOSE

DG-1R-05K proved that one incidence transfer can remove the HYPER20 logical kernel
without adding persistent state, but the selected one-transfer topology lowered
the global minimum positive logical syndrome weight from 3 to 2.

DG-1R-05L asks whether the same fixed state budget can remove the kernel
WITHOUT accepting that global-distance regression.

No decoder change is permitted.

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

FIXED STATE BUDGET

12 logical regions.
20 integrity checks.
4 bit planes.
80 integrity bits total.
80 total region-check incidences.
Exact baseline region-degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

BASELINE COMPARATORS

Frozen HYPER20:
rank 11;
one nonzero logical kernel mask;
single-region floor 6;
two-region floor 8;
global minimum positive logical syndrome weight 3;
maximum pair co-occurrence 2;
weight-4 equal-cost check-only false-exclusion count 60 / 4845.

Frozen 05K selected one-transfer topology:
rank 12;
zero logical kernel;
single-region floor 6;
two-region floor 8;
global minimum positive logical syndrome weight 2;
maximum pair co-occurrence 2;
weight-4 equal-cost check-only false-exclusion count 60 / 4845.

CANDIDATE FAMILY — DISJOINT DOUBLE TRANSFER

A primitive transfer is a triple:

(block b, source check i, target check j)

with:
- b present in baseline source i;
- b absent from baseline target j;
- i != j.

A DG-1R-05L candidate is an unordered canonical pair of primitive transfers:

t1 < t2 lexicographically,

subject to all of the following:

- transferred logical blocks are distinct;
- the four involved check indices are all distinct;
- both transfers are applied to the frozen HYPER20 baseline;
- no final check contains a duplicate logical region;
- all 20 final check sets are unique.

By construction every valid candidate must preserve:

- 20 checks;
- 80 total incidences;
- the exact baseline logical-region degree vector;
- two arity-3 checks;
- two arity-5 checks;
- sixteen arity-4 checks.

The four distinct odd-arity checks make the all-12-region logical mask
produce a syndrome of weight exactly 4.

No candidate outside this family may be introduced after first primary evaluation.

PRIMARY TOPOLOGY GATE

For every candidate compute exactly:

- GF(2) rank;
- nonzero logical-kernel count;
- maximum pair co-occurrence;
- single-region exact check-mimic floor;
- two-region exact check-mimic floor.

The global-distance condition:

global minimum positive logical syndrome weight >= 3

may be tested exactly by proving that the candidate logical-syndrome subspace
contains no nonzero vector of Hamming weight 1 or 2.

Because rank 12 is required,
absence of all weight-1 and weight-2 codewords is exactly equivalent
to minimum positive syndrome weight >= 3.

A candidate is TOPOLOGY_FEASIBLE iff all are true:

- rank = 12;
- nonzero logical-kernel count = 0;
- maximum pair co-occurrence <= 2;
- single-region floor >= 6;
- two-region floor >= 8;
- no logical syndrome of Hamming weight 1 or 2 exists.

PRIMARY CHECK4 PROTECTION GATE

For TOPOLOGY_FEASIBLE candidates, in canonical lexicographic candidate order,
evaluate the frozen equal-cost check-only protection metric.

For every check-only syndrome of weight 4,
enumerate all 4096 logical masks under frozen equal cost:

cost =
logical_fault_count
+
residual_check_fault_count.

A candidate passes CHECK4_PROTECTION iff:

all minimum-cost explanations nonzero
for no more than 60 of the 4845 weight-4 check-only patterns.

The first lexicographic TOPOLOGY_FEASIBLE candidate that passes CHECK4_PROTECTION
is the SELECTED candidate.

This ordering is frozen before execution.

If no such candidate exists,
the result is negative for this complete candidate family.

SELECTION MAY NOT BE RETUNED AFTER RESULTS.

POST-SELECTION HOLDOUTS

These are reported after selection and are not used to choose among passing candidates.

1. FULL LOGICAL GEOMETRY

Enumerate all 4096 logical masks and report:
- distinct syndrome count;
- multiplicity histogram;
- exact global minimum positive syndrome weight;
- minimum positive syndrome weight by logical-fault weight 1..12;
- zero-syndrome counts.

2. CHECK-ONLY WEIGHTS 1..4

Report equal-cost:
- d=0 unique minimum;
- d=0 tied minimum;
- all minima nonzero.

3. FROZEN CHECK4 INCIDENT CASES

Degree-6 block 5, first four incident checks.
Degree-7 block 2, first four incident checks.

Classify true check-only explanation:
- UNIQUE MINIMUM;
- TIED MINIMUM;
- NOT MINIMUM.

4. CROSS-PLANE EXACT COLLISION LIFT

Repeat the 05J/05K exact logical-versus-incident-integrity construction
for every block and P=1..4.

This ambiguity is expected to remain.
05L must not claim to solve arbitrary correlated integrity faults.

PRIMARY SIGNALS

DOUBLE_TRANSFER_FEASIBLE:
TRUE iff at least one candidate passes both the topology and CHECK4 protection gates.

SELECTED_FULL_RANK:
TRUE iff selected rank = 12.

SELECTED_KERNEL_FREE:
TRUE iff selected nonzero kernel count = 0.

LOCAL_FLOORS_PRESERVED:
TRUE iff selected single floor >=6 and two-region floor >=8.

PAIR_COOCCURRENCE_PRESERVED:
TRUE iff selected maximum pair co-occurrence <=2.

GLOBAL_DISTANCE_PRESERVED:
TRUE iff selected exact global minimum positive syndrome weight >=3.

CHECK4_PROTECTION_PRESERVED:
TRUE iff selected weight-4 false-exclusion count <=60.

ALL_REGION_SIGNAL_STRENGTH:
exact syndrome weight of logical mask 4095.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED:
TRUE only if no exact cross-plane logical/check mimic remains.

A positive 05L representation result requires:

DOUBLE_TRANSFER_FEASIBLE
AND SELECTED_FULL_RANK
AND SELECTED_KERNEL_FREE
AND LOCAL_FLOORS_PRESERVED
AND PAIR_COOCCURRENCE_PRESERVED
AND GLOBAL_DISTANCE_PRESERVED
AND CHECK4_PROTECTION_PRESERVED.

MECHANICAL ASSERTIONS

Before primary output the harness MUST assert:

- frozen HYPER20 baseline reproduced exactly;
- each candidate uses exactly two primitive transfers;
- transferred blocks are distinct;
- four affected checks are distinct;
- final check count = 20;
- final total incidence = 80;
- exact baseline region-degree vector preserved;
- exactly two checks have arity 3;
- exactly two checks have arity 5;
- exactly sixteen checks have arity 4;
- no duplicate logical region appears within a check;
- all final check sets are unique;
- candidate pair ordering is canonical and duplicate-free.

Mechanical checks are NON-EVIDENCE.

REPRODUCIBILITY

Deterministic exhaustive audit.
No RNG.

Two complete frozen sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After first primary candidate is evaluated do not change:

- candidate family;
- candidate ordering;
- topology gate;
- CHECK4 protection threshold;
- selection rule;
- holdouts;
- success signals.

PLAIN-SPEAK PREREGISTERED QUESTION

One structural move fixed the invisible global fault,
but made that fault show up through only two warning bits.

This test makes the next-smallest structural change:
two independent moves affecting four different backup checks.

That creates four odd-sized checks while keeping the same number of checks,
the same total stored integrity information,
and the same number of witnesses per data region.

The goal is to get all three things at once:

- no invisible logical fault;
- no weaker-than-before global warning pattern;
- no loss of the strong one-region and two-region protection.

We also require the known four-check ambiguity not to get worse.

If this works, it means the 128-bit representation has more useful topology headroom
than the one-move experiment exposed.

It still will not solve the deeper case where coordinated backup corruption
creates exactly the same evidence as real data corruption.

canonical_scientific_execution = false.
stab18_r1_touched = false.
