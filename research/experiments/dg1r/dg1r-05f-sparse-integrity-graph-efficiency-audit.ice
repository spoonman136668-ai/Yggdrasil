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


FINAL DG-1R-05F NON-EVIDENCE CLOSURE — SPARSE INTEGRITY GRAPH EFFICIENCY

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE SPARSE-CAPACITY-EFFICIENCY RESULT /
DEGREE-4 CORRELATED-FAULT SAFETY PASS /
DEGREE-3 CORRELATED-FAULT BOUNDARY CONFIRMED /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

76d2e77fd8c2d5170f77dd6085a66c1326cd544b.

Source SHA-256:

3e6f76b7f83689e32cca13236b440f06cb9f20313cd6006bc255857a1e733e12.

Source bytes:

12919.

OUTPUT

RUN 1 SHA-256:

750f07a03b75c1c584bb67c8674739c08e25cd09823a59286f3f9d0c555c96cf.

RUN 2 SHA-256:

750f07a03b75c1c584bb67c8674739c08e25cd09823a59286f3f9d0c555c96cf.

Byte-identical:

PASS.

MECHANICAL VALIDITY

mechanical_valid:

TRUE.

FROZEN SIGNALS

SPARSE_CAPACITY_EFFICIENCY_SIGNAL:

TRUE.

DEGREE4_TWO_FAULT_SAFETY:

TRUE.

DEGREE3_BOUNDARY_METHODS:

SPARSE18_MAJORITY_48.
SPARSE20_MAJORITY_48.

ALLOCATION_ADVANTAGE:

TRUE.

DISTRIBUTED_SPARSE_REPAIR_SIGNAL:

TRUE.

CAPACITY

CHAIN_HAMMING_48:

48 logical bits.
80 redundancy bits.

SPARSE18_MAJORITY_48:

48 logical bits.
72 active redundancy bits.
8 inert bits.

SPARSE20_MAJORITY_48:

48 logical bits.
80 redundancy bits.

DG-1R-05E four-witness reference:

32 logical bits.
96 redundancy bits.

Thus:

SPARSE20

recovers:

16:
logical bits

relative:
to:
DG-1R-05E

while:
retaining:
selected:
four-witness:
fault tolerance.

BASIC LOCAL REPAIR

LOCAL_DATA2_DEG3.

SPARSE18:

median:
logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

repairs:

8.

false repairs:

0.

SPARSE20:

same:
exact:
result.

Thus:

degree-3:
majority
is:
sufficient
for:
ordinary:
local:
damage

when:
all:
three:
witnesses
are:
healthy.

ONE BAD WITNESS — DEGREE 3

LOCAL_DATA2_PLUS_ONE_WITNESS_DEG3.

SPARSE18:

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

false repairs:

0.

SPARSE20:

same:
exact:
result.

Thus:

2-of-3:
majority
correctly:
repairs:
the:
damaged:
local:
state

despite:

one:
corrupted:
witness.

ONE BAD WITNESS — DEGREE 4

LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4.

SPARSE20:

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

repairs:

8.

false repairs:

0.

The:
degree-4:
region

repairs:
with:
three:
correct:
witnesses
against:
one:
bad:
witness.

SPARSE_CAPACITY_EFFICIENCY_SIGNAL:

PASS.

TWO CORRELATED BAD WITNESSES — DEGREE 3

TWO_CORRELATED_WITNESSES_DEG3.

SPARSE18:

repairs:

8.

false-repair fraction:

1.0.

median:
logical divergence area:

2.916666666666667.

sustained:
exact logical recovery:

0.

SPARSE20:

same:
degree-3:
failure
at:
block 2.

Thus:

a:
degree-3:
region

with:

two:
correlated:
bad:
witnesses

versus:

one:
healthy:
witness

forms:

a:
wrong:
2-of-3:
majority.

This:
is:
the:
expected:
degree-3:
boundary.

TWO CORRELATED BAD WITNESSES — DEGREE 4

TWO_CORRELATED_WITNESSES_DEG4.

SPARSE20:

repairs:

0.

abstentions:

8.

false repairs:

0.

logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

The:
vote:

2 correct
versus:
2 wrong

creates:

no:
strict:
majority.

The:
system
safely:
abstains.

DEGREE4_TWO_FAULT_SAFETY:

PASS.

SPARSE18:

the:
same:
target:
block
has:
only:
degree 3.

It:
repairs:

8.

false-repair fraction:

1.0.

median:
logical divergence area:

3.21875.

Thus:

the:
extra:
two:
graph:
edges
in:
SPARSE20

provide:
real:
fault-tolerance
at:
their:
endpoints.

DISTRIBUTED DAMAGE

DISTRIBUTED_LOCAL_DATA2.

SPARSE20:

two:
separate:
damaged:
logical:
regions.

median:
logical divergence area:

0.

sustained:
exact logical recovery:

1.0.

repairs:

16.

false repairs:

0.

DISTRIBUTED_SPARSE_REPAIR_SIGNAL:

PASS.

CHAIN REFERENCE

CHAIN_HAMMING_48

repairs:
ordinary:
local
and:
distributed:
data damage

exactly

when:
its:
two:
neighbor:
checks
remain:
healthy.

But:

LOCAL_DATA2_PLUS_ONE_WITNESS_DEG3:

median:
logical divergence area:

2.8541666666666665.

sustained:
exact logical recovery:

0.25.

LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4:

median:
logical divergence area:

2.78125.

sustained:
exact logical recovery:

0.125.

The:
chain:
requires:
both:
neighbor:
reconstruction:
channels
to:
agree.

One:
damaged:
channel
removes:
repair:
quorum.

SPARSE20
therefore:
outperforms:
the:
same-capacity:
chain
on:
witness:
damage

without:
degrading:
ordinary:
local:
repair.

ALLOCATION_ADVANTAGE:

PASS.

DETECT-ONLY CONTROL

SPARSE20_DETECT_ONLY:

does NOT:
recover:
local:
data damage.

For example:

LOCAL_DATA2_DEG3:

median:
logical divergence area:

2.8541666666666665.

sustained:
exact logical recovery:

0.25.

DISTRIBUTED_LOCAL_DATA2:

median:
logical divergence area:

5.177083333333333.

sustained:
exact logical recovery:

0.25.

Thus:

the:
positive:
SPARSE20:
result

comes:
from:
active:
majority:
reconstruction,

not:
merely:
from:
the:
graph:
representation.

CORE MECHANISTIC CONCLUSION

DG-1R-05F establishes:

INTEGRITY:
TOPOLOGY

matters:
as:
much
as:

INTEGRITY:
BUDGET.

With:
the:
same:
48:
logical bits

and:
the:
same:
128:
physical bits,

reallocating:
redundancy

from:

local Hamming
+
a:
fragile:
two-neighbor:
chain

to:

a:
sparse:
cross-region:
integrity:
graph

produces:

- exact:
  ordinary:
  local:
  repair;
- exact:
  distributed:
  repair;
- one-bad-witness:
  tolerance;
- selected:
  two-correlated-witness:
  safety;
- without:
  dropping:
  to:
  32:
  logical:
  bits.

The:
fault-tolerance:
boundary

is:
now:
LOCAL:
GRAPH:
DEGREE.

Degree 3:

one:
bad:
witness
is:
tolerable.

two:
correlated:
bad:
witnesses
can:
control:
the:
majority.

Degree 4:

two:
correct
and:
two:
wrong

produce:
safe:
abstention.

Thus:

repair:
strength
can:
be:
allocated:
spatially

rather:
than:
maximized:
uniformly.

IMPORTANT LIMIT

SPARSE20
does NOT:
give:
degree-4:
protection
to:
every:
logical:
region.

20:
edges

provide:

40:
total:
graph-degree:
units

across:
12:
regions.

Average degree:

3.3333333333333335.

Therefore:

with:
48:
logical bits
and:
80:
edge-check:
bits,

uniform:
degree 4
is:
mathematically:
unavailable
under:
this:
full-4-bit:
edge:
representation.

The:
remaining:
question
is:
how:
to:
use:
time /
adaptation /
compressed:
integrity
to:
move:
stronger:
protection
where:
it:
is:
needed

without:
permanently:
paying
for:
degree 4
everywhere.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05G —
TIME-MULTIPLEXED:
INTEGRITY:
WITNESS /
QUARANTINE:
AUDIT.

Keep:

48:
logical bits.

128:
physical bits.

20:
four-bit:
integrity:
edge slots.

Instead:
of:
keeping:
all:
20:
edges
permanently:
mapped
to:
one:
static:
graph,

use:
a:
frozen:
multi-phase:
topology
schedule.

When:
a:
region
becomes:
SUSPECT:

do NOT:
immediately:
overwrite:
all:
incident:
integrity:
evidence.

Temporarily:
quarantine:
that:
region's:
logical:
update

while:

edge slots
rotate
through:
additional:
spatially:
diverse:
witness:
relations.

Question:

can:
TIME

supply:
additional:
witness:
diversity

without:

adding:
more:
persistent:
integrity:
bits

or:

reducing:
logical:
capacity
below:
48?

This:
directly:
connects:

the:
earlier:
multi-timescale:
research

with:

the:
new:
self-repair:
tissue:
line.

PLAIN-SPEAK SUMMARY

This:
was:
a:
very:
useful:
result.

We:
got:
back:
to:
48:
usable:
logical:
bits

without:
giving:
up:
the:
stronger:
repair
everywhere.

The:
trick
was:
how:
we:
wired:
the:
backup:
information.

A:
region
with:
three:
witnesses
can:
survive:
one:
bad:
witness.

But:
if:
two:
of:
the:
three
are:
wrong
the:
same:
way,

they:
become:
the:
majority
and:
the:
repair
is:
wrong.

A:
region
with:
four:
witnesses
behaves:
better.

With:
two:
correct
and:
two:
wrong,

there:
is:
no:
majority,

so:
it:
refuses:
to:
guess.

The:
important:
part
is:

we:
did:
not:
need:
to:
give:
every:
region
four:
witnesses
all:
the:
time.

We:
can:
spend:
stronger:
protection
only:
where:
the:
graph
places:
it.

That:
suggests:
the:
next:
idea:

make:
the:
integrity:
network
move
through:
time.

Instead:
of:
paying:
for:
four:
witnesses
everywhere
permanently,

a:
suspicious:
region
could:
be:
temporarily:
quarantined

while:
the:
same:
backup:
bits
are:
reassigned
to:
collect:
more:
independent:
evidence.

That:
would:
let:
TIME
act:
like:
extra:
repair:
capacity

without:
adding:
more:
persistent:
bits.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05F remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
