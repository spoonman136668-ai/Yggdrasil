TITLE: DG-1R-05K — Parity-Broken Mixed-Arity Topology Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REPRESENTATION AUDIT
TRACK: DG-1R / SOFTWARE TISSUE / DISTRIBUTED INTEGRITY / TOPOLOGY
BRANCH: dg1a-ar
PARENT: DG-1R-05J

PURPOSE

DG-1R-05J established two distinct limits in frozen HYPER20:

1. an all-even-arity topological nullspace:
   the all-12-region same-plane logical fault is syndrome-invisible;

2. a broader fault-type ambiguity:
   sufficiently coordinated integrity faults can reproduce logical-fault syndromes exactly.

DG-1R-05K addresses only the first limit.

Question:

CAN THE SAME 20 FOUR-BIT INTEGRITY SLOTS
BREAK THE ALL-EVEN PARITY SYMMETRY
WITHOUT LOSING THE LOCAL SEPARATION ALREADY ACHIEVED?

No extra persistent bits.
No new decoder.
No dynamic repair claim.

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

Exact frozen DG-1R-05G/05H/05I/05J HYPER20 incidence matrix.

20 checks.
12 logical regions.
80 total logical-check incidences.
Degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

All 20 baseline checks have arity 4.

BASELINE PRIMARY FACTS FROM CLOSED 05J

These are comparison targets, not tunable thresholds:

GF(2) rank:
11.

Nonzero logical kernel:
all 12 regions.

Single-region exact check-mimic floor:
6.

Two-region exact check-mimic floor:
8.

Maximum pair co-occurrence:
2.

Global minimum positive logical syndrome weight:
3.

CANDIDATE FAMILY — ONE-INCIDENCE TRANSFER

Exhaustively enumerate every ordered triple:

(block b, source check i, target check j)

such that:

- b is present in source check i;
- b is absent from target check j;
- i != j.

Construct candidate topology by:

- removing b from source check i;
- adding b to target check j.

Consequences by construction:

- check count remains 20;
- total incidence remains 80;
- block degree vector remains exactly unchanged;
- source arity becomes 3;
- target arity becomes 5;
- all other checks remain arity 4.

No candidate outside this frozen family may be introduced after execution.

PRIMARY ENUMERATION

For every candidate compute exactly:

- GF(2) rank;
- nonzero logical-kernel count;
- maximum pair co-occurrence;
- minimum single-region syndrome weight;
- minimum two-region syndrome weight;
- global minimum positive syndrome weight across all 4095 nonzero logical masks;
- number of zero-syndrome nonzero logical masks.

FEASIBILITY GATE

A candidate is FEASIBLE iff all are true:

- rank = 12;
- nonzero logical-kernel count = 0;
- maximum pair co-occurrence <= 2;
- minimum single-region syndrome weight >= 6;
- minimum two-region syndrome weight >= 8.

CANDIDATE SELECTION

Among FEASIBLE candidates choose exactly one using this frozen ordering:

1. maximize global minimum positive syndrome weight;
2. maximize minimum two-region syndrome weight;
3. maximize minimum single-region syndrome weight;
4. minimize maximum pair co-occurrence;
5. lexicographically smallest tuple:
   (block, source_check, target_check).

No selection metric may be changed after primary enumeration.

HOLDOUT STATIC VALIDATION

The following metrics are NOT used for candidate selection.

Compare selected candidate versus frozen HYPER20 baseline:

A. logical-only syndrome geometry:
- distinct syndromes;
- multiplicity histogram;
- minimum positive syndrome by logical-fault weight 1..12.

B. equal-cost check-only explanation boundary:
for every check-only syndrome of Hamming weight 1..4,
enumerate all 4096 logical masks using:

cost =
logical_fault_count
+
residual_check_fault_count.

For each check-only weight report:
- d=0 unique minimum;
- d=0 tied minimum;
- all minimum-cost explanations nonzero.

C. frozen CHECK4 incident tests:
- degree-6 block 5, first four incident checks;
- degree-7 block 2, first four incident checks.

Classify true check-only explanation as:
- UNIQUE MINIMUM;
- TIED MINIMUM;
- NOT MINIMUM.

D. cross-plane exact-mimic construction:
repeat 05J exact logical-versus-integrity mimic construction for P=1..4.

This is expected to remain a fault-type ambiguity.
A topology positive must not be misreported as solving arbitrary correlated integrity faults.

PRIMARY SIGNALS

PARITY_BROKEN_FEASIBLE:
TRUE iff at least one FEASIBLE candidate exists.

SELECTED_FULL_RANK:
TRUE iff selected candidate rank = 12.

SELECTED_KERNEL_FREE:
TRUE iff selected candidate has zero nonzero logical kernel masks.

LOCAL_FLOORS_PRESERVED:
TRUE iff selected single-region floor >=6
AND selected two-region floor >=8.

PAIR_COOCCURRENCE_PRESERVED:
TRUE iff selected maximum pair co-occurrence <=2.

GLOBAL_DISTANCE_IMPROVED:
TRUE iff selected global minimum positive syndrome weight > baseline 3.

CHECK4_EQUAL_COST_NOT_WORSE:
TRUE iff selected candidate does not increase
the number of weight-4 check-only patterns
whose equal-cost minimum excludes d=0,
relative to baseline 60 / 4845.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED:
TRUE only if no exact cross-plane logical/check mimic exists for any block and P=1..4.

A positive 05K topology claim requires:

PARITY_BROKEN_FEASIBLE
AND SELECTED_FULL_RANK
AND SELECTED_KERNEL_FREE
AND LOCAL_FLOORS_PRESERVED
AND PAIR_COOCCURRENCE_PRESERVED.

GLOBAL_DISTANCE_IMPROVED is reported separately.

CHECK4_EQUAL_COST_NOT_WORSE is a holdout protection criterion.

CROSSPLANE_ARBITRARY_CORRELATION_SOLVED is expected to remain FALSE
and is not required for the topology claim.

MECHANICAL ASSERTIONS

Harness MUST assert:

- baseline HYPER20 exactly reproduced;
- every candidate differs by exactly one incidence removal and one incidence addition for the same block;
- every candidate has 20 checks;
- every candidate has exactly 80 incidences;
- every candidate preserves the exact baseline degree vector;
- source arity is exactly 3;
- target arity is exactly 5;
- all other arities are exactly 4;
- all 4095 nonzero logical masks are evaluated for every candidate;
- holdout check-only weights 1..4 enumerate exactly 6195 patterns.

These are NON-EVIDENCE mechanical checks.

REPRODUCIBILITY

Deterministic exhaustive audit.
No RNG.

Two complete frozen sweeps.

Serialized output SHA-256 must match exactly.

NO POST-RESULT TUNING

After first primary candidate is evaluated do not alter:

- candidate family;
- feasibility gate;
- selection order;
- holdout metrics;
- baseline comparison;
- CHECK4 definitions;
- cross-plane construction;
- success signals.

PLAIN-SPEAK PREREGISTERED QUESTION

The last test found a blind spot caused by every backup check covering an even number of data regions.

This test makes the smallest possible structural change:
move one region's participation from one backup check to another.

That leaves the number of backup slots, the total amount of stored integrity data,
and every region's number of witnesses unchanged.

But it creates one three-region check and one five-region check,
which breaks the even-parity symmetry.

We will exhaustively test every such one-move topology.

A useful result would remove the global invisible fault
without making local one-region or two-region damage easier to fake.

It will not solve the deeper problem that sufficiently coordinated backup failures
can imitate real data failures.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05K PARITY-BROKEN TOPOLOGY

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE FIRST PRIMARY CANDIDATE ENUMERATION.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05k_parity_broken_v1.py

Harness alignment commit:

51e8612aee637d153af75125015ab438448bfb21.

Git blob SHA:

341ddf20b52bce2b8f2549b29d2630ac3c2e22a2.

Source SHA-256:

a66d292dd4cd8eeec34f366c2fb64df60e977cc67d5394287f2402e6d95ddf36.

Source bytes:

10253.

PRE-FREEZE DEFECT BOUNDING

The first repository harness commit was not frozen and was not executed.

Inspection found:
- a misspelled columns helper reference;
- corrupted source bytes in the holdout section.

Those defects were repaired before freeze and before any primary candidate was evaluated.

No result-driven tuning occurred.

LOCAL PRECHECK — NON-EVIDENCE

Python syntax:

PASS.

Baseline edge count:

20.

Baseline total incidence:

80.

Baseline degree vector:

(7,7,7,7,7,6,6,7,6,7,7,6).

Baseline maximum pair co-occurrence:

2.

Frozen one-incidence-transfer candidate triples:

1064.

For all 1064 mechanically generated candidates:
- check count remained 20;
- total incidence remained 80;
- the baseline degree vector was preserved;
- the source check had arity 3;
- the target check had arity 5;
- the other 18 checks had arity 4.

These are mechanical checks only and are NON-EVIDENCE.

No rank, feasibility, selection, holdout, or primary candidate result was generated before this freeze.

REPRODUCIBILITY

Two complete deterministic exhaustive sweeps.

Serialized output SHA-256 must match exactly.

No RNG.

No post-result tuning.

DG-1R-05 canonical frozen primary remains:

UNSPENT.

canonical_scientific_execution = false.
stab18_r1_touched = false.
