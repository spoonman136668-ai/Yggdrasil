TITLE: DG-1R-05F — Sparse Integrity Graph / Fault-Tolerance-per-Bit Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REDUNDANCY-EFFICIENCY PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / CAPACITY EFFICIENCY
BRANCH: dg1a-ar
PARENT: DG-1R-05E

PURPOSE

DG-1R-05E showed:
- four witnesses with 3-of-4 quorum tolerate one bad witness;
- two correlated bad witnesses become a safe 2-vs-2 abstention;
- three correlated bad witnesses can still fool the quorum;
- this strength reduced logical capacity to 32 bits inside 128 physical bits.

DG-1R-05F asks:

CAN:
A:
SPARSE:
INTEGRITY:
GRAPH

RECOVER:
MORE:
LOGICAL:
CAPACITY

WHILE:
RETAINING:
MEANINGFUL:
WITNESS:
FAULT:
TOLERANCE?

BOUNDARY

Synthetic software-only pilot.

No living tissue.
No wetware.
No biological nanotechnology.
No production modification.
No canonical H191 execution.
No STAB-18-R1 execution.

NON-CANONICAL / NON-EVIDENCE.

DG-1R-05 canonical frozen primary remains UNSPENT.

FIXED PHYSICAL BUDGET

128 persistent bits for every method.

FIXED LOGICAL CAPACITY

48 logical data bits.

12 logical blocks x 4 bits.

Therefore:
all primary methods preserve
the DG-1R-05C/D logical capacity.

LOGICAL DYNAMICS

One MIXED5 CA update per external input
over the same 48-bit periodic logical ring.

Pre-damage:
1024 steps.

Post-damage:
32 steps.

Input-mapped blocks:
1,4,7,10.

Primary damage blocks:
2,3,8.

METHOD 1 — CHAIN_HAMMING_48

Exact DG-1R-05C-style allocation:

12 Hamming(7,4) local codewords:
84 bits.

11 adjacent-block XOR edges:
44 bits.

Total:
128 bits.

Repair:
local syndrome nonzero
AND
left/right neighbor candidates agree.

Purpose:
same-capacity reference.

METHOD 2 — SPARSE18_MAJORITY_48

Store raw 48 logical data bits directly.

Integrity graph:
18 undirected edges.

Graph:
12-cycle:
(0,1),(1,2),...,(10,11),(11,0)

plus opposite matching:
(0,6),(1,7),(2,8),(3,9),(4,10),(5,11).

Every block degree:
3.

Each edge stores:
4 XOR check bits
between its endpoint data vectors.

Integrity bits:
18 * 4 = 72.

Total used:
48 + 72 = 120 bits.

Remaining:
8 bits are frozen inert zeros.

Repair:
derive one 4-bit candidate from each incident edge.
If a strict majority of incident witnesses
agree on one candidate
and current local data differs,
repair to that candidate.
Otherwise abstain.

METHOD 3 — SPARSE20_MAJORITY_48

Same raw 48 logical bits.

Same 18-edge graph
plus:
(0,3)
and:
(6,9).

Total edges:
20.

Integrity bits:
80.

Total:
128 bits.

Degrees:
0,3,6,9 have degree 4.
All others have degree 3.

Repair:
strict majority of all incident witnesses.

Thus:
degree-3 block:
2-of-3 required.

degree-4 block:
3-of-4 required.

METHOD 4 — SPARSE20_DETECT_ONLY

Same 48+80 representation.

Compute witness candidates and vote structure.

Perform no repair.

Purpose:
representation-only control.

REPAIR ORDER

1. inspect persistent pre-input data/check state;
2. perform allowed repair/abstention;
3. read 48 logical bits;
4. apply current input overwrite;
5. one MIXED5 update;
6. rewrite raw logical data;
7. recompute all integrity edges.

DAMAGE FAMILIES

Harness MUST assert actual lesion cardinality.

LOCAL_DATA2_DEG3

Target block:
2.

Flip:
d1,d2.

Actual lesion size:
2.

LOCAL_DATA2_PLUS_ONE_WITNESS_DEG3

Block:
2.

Flip:
d1,d2
plus:
the d1 check bit
on edge (1,2).

Actual lesion size:
3.

TWO_CORRELATED_WITNESSES_DEG3

Healthy block:
2.

Flip:
the d1 check bit
on edges:
(1,2)
and
(2,3).

Actual lesion size:
2.

Expected:
SPARSE18/20 degree-3 majority
has:
2 wrong witnesses
versus:
1 correct witness.

This is:
the degree-3 majority failure boundary.

LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4

Target block:
3.

Flip:
d1,d2
plus:
d1 check
on edge (2,3).

Actual lesion size:
3.

Only:
SPARSE20
gives block 3:
four witnesses.

TWO_CORRELATED_WITNESSES_DEG4

Healthy block:
3.

Flip:
d1 check
on edges:
(2,3)
and
(3,4).

Actual lesion size:
2.

Expected:
SPARSE20:
2 correct
versus:
2 wrong.

No strict majority.

It should abstain.

CHAIN_HAMMING_48:
its two adjacent witnesses
are both corrupted
and may false-repair.

SPARSE18:
block 3 has degree 3;
two corrupted witnesses
may form a wrong majority.

DISTRIBUTED_LOCAL_DATA2

Damage:
block 2:
d1,d2.

block 8:
d1,d2.

Actual lesion size:
4.

PRIMARY METRICS

Counterfactual logical/physical divergence:
h1,h4,h8,h16,h32.

Also:
- logical divergence area;
- physical divergence area;
- sustained exact logical recovery;
- recovery time;
- repairs;
- false repairs;
- abstentions;
- witness degree;
- winning vote count.

FALSE REPAIR

A proposed logical repair is FALSE
if it does not match
the counterfactual reference block
immediately before repair.

Repair logic never sees this label.

SPARSE CAPACITY-EFFICIENCY SIGNAL

TRUE if:

SPARSE20_MAJORITY_48
on
LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4

has:
- h1 median logical divergence = 0;
- sustained exact logical recovery >= 0.90;
- false repair fraction <= 0.01;
- logical divergence area = 0;

while retaining:
48 logical bits.

DEGREE-4 TWO-FAULT SAFETY

TRUE if:

TWO_CORRELATED_WITNESSES_DEG4:

SPARSE20_MAJORITY_48:
- false repairs = 0;
- h4 median logical divergence = 0.

DEGREE-3 BOUNDARY

Flag:
SPARSE18_MAJORITY_48
and/or
SPARSE20_MAJORITY_48

if:
TWO_CORRELATED_WITNESSES_DEG3

false repair fraction > 0.10.

ALLOCATION ADVANTAGE

TRUE if:
SPARSE20_MAJORITY_48
outperforms CHAIN_HAMMING_48
on at least one frozen correlated-witness family
while:
- using the same 128 physical bits;
- retaining the same 48 logical bits;
- not degrading LOCAL_DATA2_DEG3 exact recovery.

DISTRIBUTED SPARSE REPAIR SIGNAL

TRUE if:

DISTRIBUTED_LOCAL_DATA2:

SPARSE20_MAJORITY_48:
- h4 median logical divergence = 0;
- sustained exact logical recovery >= 0.75.

EFFICIENCY ACCOUNTING

Report:

CHAIN_HAMMING_48:
48 logical / 80 redundancy.

SPARSE18:
48 logical / 72 active redundancy / 8 inert.

SPARSE20:
48 logical / 80 redundancy.

DG-1R-05E reference:
32 logical / 96 redundancy.

Interpret:
repair strength per redundancy bit
and:
logical capacity retained.

WORLD FAMILY

8 worlds.

Seeds:
20260926056000..20260926056007.

No prior DG-1R seed reuse.

NO POST-RUN TUNING

After first scenario,
do not alter:
- graph edges;
- majority rules;
- damage blocks;
- damage geometry;
- logical capacity;
- thresholds;
- world family;
- metrics.

REPRODUCIBILITY

Two complete 8-world sweeps.

Output SHA-256 must match exactly.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The four-witness tissue was robust,
but it used so much backup structure
that only 32 of 128 bits
were left as independent logical data.

This test tries to wire the backup network
more efficiently.

Instead of giving every region
a large local code plus four full witnesses,
we keep 48 logical bits
and connect regions through a sparse graph.

Most regions get three independent witnesses.
A few get four.

The question is:

can clever connectivity
give us much of the repair strength
without sacrificing so much useful state?

If yes,
Yggdrasil does not need
maximum redundancy everywhere.

It needs:
the right integrity topology.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05F SPARSE INTEGRITY GRAPH HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05F:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05f_sparse_integrity_v1.py

Exact-byte commit:

2560a2c44acbc59008b2e695724dc1e27e27a564.

Git blob SHA:

76d2e77fd8c2d5170f77dd6085a66c1326cd544b.

Source SHA-256:

3e6f76b7f83689e32cca13236b440f06cb9f20313cd6006bc255857a1e733e12.

Source bytes:

12919.

PACKAGING RECONCILIATION

Initial:
repository:
transfer

omitted:
the:
source's:
final:
newline.

Initial remote blob:

d22927cf3192decf67053ce9b4bf0b497c75ad27.

No:
DG-1R-05F:
world
was:
executed
from:
that:
artifact.

The:
newline
was:
restored.

Corrected:
remote:
Git blob:

76d2e77fd8c2d5170f77dd6085a66c1326cd544b.

Local:
git hash-object:

76d2e77fd8c2d5170f77dd6085a66c1326cd544b.

Exact byte identity:

PASS.

Python syntax:

PASS.

No:
DG-1R-05F:
world
was:
executed
before:
this:
freeze.

FROZEN WORLD FAMILY

20260926056000..20260926056007.

8 worlds.

FROZEN CAPACITY

48:
logical bits.

128:
physical bits.

FROZEN GRAPH METHODS

CHAIN_HAMMING_48.

SPARSE18_MAJORITY_48.

SPARSE20_MAJORITY_48.

SPARSE20_DETECT_ONLY.

DG-1R-05 CANONICAL STATUS

Still:

UNSPENT.

DG-1R-05F:

NON-CANONICAL /
NON-EVIDENCE.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

canonical_scientific_execution = false.
stab18_r1_touched = false.
