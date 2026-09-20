TITLE: DG-1R-05E — Sparse Three-Witness Quorum / Correlated-Damage Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE THREE-WITNESS REPAIR PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / REPAIR QUORUM
BRANCH: dg1a-ar
PARENT: DG-1R-05D

PURPOSE

DG-1R-05D established:

- healthy neighbors can repair local syndrome-silent corruption;
- two-sided neighbor diagnosis repaired distributed silent damage exactly;
- one bad witness is safely rejected by two-sided disagreement;
- two correlated bad witnesses can agree on the same wrong candidate and drive false repair.

DG-1R-05E asks:

CAN:
THREE:
DIRECT:
WITNESSES

inside:
the:
same:
128-bit:
state budget

extend:
the:
fault-tolerance:
boundary

from:

ZERO:
bad:
witnesses
required
for:
two-source:
agreement

to:

ONE:
bad:
witness
tolerated
under:
2-of-3:
quorum?

BOUNDARY

Synthetic software-only pilot.

No:
living tissue.
No:
wetware.
No:
biological nanotechnology.
No:
production modification.
No:
canonical H191 execution.
No:
STAB-18-R1 execution.

NON-CANONICAL /
NON-EVIDENCE.

DG-1R-05:
canonical frozen primary
remains:
UNSPENT.

STATE BUDGET

12:
logical:
blocks.

4:
logical:
data bits
per:
block.

Logical data:

48 bits.

Local:
Hamming(7,4):

12 * 7
=
84 bits.

Cross-integrity:

11:
four-bit:
XOR:
relations

=
44 bits.

Total:

84 + 44
=
128:
persistent bits.

No:
hidden:
memory.

CHECK GRAPH

Use:
11:
undirected:
four-bit:
XOR:
check edges:

E0:
(2,0).

E1:
(2,1).

E2:
(2,3).

E3:
(6,4).

E4:
(6,5).

E5:
(6,7).

E6:
(10,8).

E7:
(10,9).

E8:
(10,11).

E9:
(3,4).

E10:
(7,8).

The:
graph
is:
connected.

PRIMARY REPAIR BLOCKS

2.
6.
10.

Each:
has:

three:
direct:
witness:
neighbors.

Block 2 witnesses:

0,
1,
3.

Block 6 witnesses:

4,
5,
7.

Block 10 witnesses:

8,
9,
11.

For:
edge:
(t,n),

stored check:

C_tn
=
X_t
XOR
X_n.

Candidate:
for:
target t
from:
neighbor n:

Xhat_t_from_n
=
X_n
XOR
C_tn.

Thus:

each:
primary:
target
has:

three:
direct:
four-bit:
reconstruction:
candidates.

LOGICAL DYNAMICS

One:
MIXED5:
CA update

per:
external:
input

over:
the:
48:
logical:
bits.

After:
each:
logical:
update:

- recompute:
  all:
  local:
  Hamming:
  codewords;

- recompute:
  all:
  11:
  cross-check:
  vectors.

REPAIR ORDER

1.
inspect:
persistent:
pre-input:
local:
and:
cross:
state;

2.
perform:
allowed:
diagnosis /
repair /
abstention;

3.
decode:
48-bit:
logical:
state;

4.
apply:
current:
input;

5.
one:
MIXED5:
logical:
update;

6.
re-encode:
local:
Hamming:
state;

7.
recompute:
cross-check:
graph.

INPUT MAPPING

Mapped logical blocks:

1,
3,
5,
7,
9,
11.

One:
world-specific:
logical:
bit
inside:
each:
mapped:
block.

Primary repair blocks:

2,
6,
10

are:
not:
input mapped.

METHOD 1 — PAIR2

For:
each:
primary:
block:

use:
the:
first:
two:
frozen:
witnesses.

If:
candidate 1
==
candidate 2

and:
current local
!=
candidate:

repair:
to:
candidate.

If:
the:
two:
candidates
disagree:

ABSTAIN.

Purpose:

two-source:
reference
analogous:
to:
DG-1R-05D.

METHOD 2 — UNANIMOUS3

If:

candidate 1
==
candidate 2
==
candidate 3

and:
current local
!=
candidate:

repair.

Otherwise:

ABSTAIN.

Purpose:

maximum:
three-source:
conservatism.

METHOD 3 — MAJORITY3

If:

at least:
two:
of:
the:
three:
four-bit:
candidate vectors

are:
exactly:
equal,

that:
vector
is:
the:
quorum:
candidate.

If:
current local
!=
quorum candidate:

repair.

If:

all:
three:
candidate vectors
differ:

ABSTAIN.

Purpose:

tolerate:
one:
bad:
witness
while:
retaining:
syndrome-blind:
repair.

METHOD 4 — DETECT_ONLY

Compute:

three:
candidates,
agreement:
pattern,
local:
mismatch.

Perform:

NO:
repair.

Purpose:

diagnostic:
control.

LOCAL SYNDROME

Local:
Hamming:
syndrome

is:
reported
as:
telemetry

but:

PAIR2,
UNANIMOUS3,
and:
MAJORITY3

do NOT:
require:
a:
nonzero:
local:
syndrome.

Thus:

syndrome-silent:
repair
remains:
possible.

PRE-DAMAGE DEVELOPMENT

1024:
external:
input:
steps.

Then:

clone:

REFERENCE.

DAMAGED.

Continue:

32:
external:
steps

under:
identical:
future:
input.

WORLD FAMILY

8:
worlds.

Seeds:

20260926055000
through:
20260926055007.

No:
prior:
DG-1R:
seed reuse.

DAMAGE GEOMETRY

Primary target blocks:

2,
6,
10.

For:
each:
target:

define:
its:
three:
incident:
witness:
edges
in:
the:
order
listed
above.

Harness MUST:
assert:

- exact:
  lesion cardinality;
- unique:
  lesion indices;
- no:
  local:
  damage:
  overlaps:
  mapped:
  physical:
  positions.

DAMAGE FAMILY A — SILENT_DATA3

Local:
target:
damage only.

Flip:
target:
Hamming:
physical:
data positions:

3,
5,
6

corresponding to:

d1,
d2,
d3.

Actual lesion size:

3.

Frozen property:

local:
Hamming:
syndrome
=
0.

DAMAGE FAMILY B — SILENT_DATA3_PLUS_ONE_WITNESS1

Apply:

SILENT_DATA3

plus:

flip:
the:
d1:
bit
of:
the:
first:
incident:
cross-check:
edge.

Actual lesion size:

4.

Expected:

one:
wrong:
witness.

two:
healthy:
witnesses.

DAMAGE FAMILY C — SILENT_DATA3_PLUS_TWO_WITNESS2

Apply:

SILENT_DATA3

plus:

flip:
the:
d1:
bit
of:
the:
first
and:
second:
incident:
cross-check:
edges.

Actual lesion size:

5.

Expected:

two:
correlated:
wrong:
witnesses

agree
on:
the:
same:
wrong:
d1.

One:
healthy:
witness
remains.

Purpose:

frozen:
2-of-3:
failure:
boundary.

DAMAGE FAMILY D — ONE_WITNESS1_ONLY

No:
local:
target:
damage.

Flip:
d1:
cross-check:
bit
on:
the:
first:
incident:
edge.

Actual lesion size:

1.

Purpose:

test:
healthy:
target:
safety
with:
one:
bad:
witness.

DAMAGE FAMILY E — TWO_WITNESS2_ONLY

No:
local:
target:
damage.

Flip:
d1:
cross-check:
bit
on:
the:
first
and:
second:
incident:
edges.

Actual lesion size:

2.

Purpose:

test:
whether:
a:
2-of-3:
quorum

can:
be:
turned
against:
a:
healthy:
target

by:
two:
correlated:
bad:
witnesses.

DAMAGE FAMILY F — DISTRIBUTED_SILENT3

Simultaneously:

block 2:
SILENT_DATA3.

block 6:
SILENT_DATA3.

block 10:
SILENT_DATA3.

Actual lesion size:

9.

DAMAGE FAMILY G — DISTRIBUTED_ONE_BAD_WITNESS

For:
blocks:

2,
6,
10:

apply:

SILENT_DATA3

plus:

one:
bad:
first:
witness:
d1:
cross-check:
bit.

Actual lesion size:

12.

Purpose:

test:
parallel:
one-witness:
fault tolerance.

PRIMARY METRICS

At:
horizons:

1,
4,
8,
16,
32:

- logical:
  divergence;
- whole:
  physical:
  divergence;
- outside-lesion:
  divergence;
- exact:
  logical:
  match rate.

Also:

- logical:
  divergence area;
- physical:
  divergence area;
- sustained:
  exact:
  logical:
  recovery rate;
- repair count;
- false repair count;
- abstention count;
- unanimous:
  candidate:
  count;
- two-of-three:
  majority:
  count;
- all-different:
  count;
- local:
  syndrome-positive:
  count.

FALSE REPAIR

A:
repair:
proposal

is:
FALSE

if:

it:
does NOT:
match:

the:
counterfactual:
reference:
logical:
target:
block

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
label.

THREE-WITNESS REPAIR SIGNAL

TRUE
if:

on:
SILENT_DATA3:

MAJORITY3:

1.
median:
h1:
logical divergence
=
0;

2.
sustained:
exact:
logical:
recovery
>=0.90;

3.
false-repair:
fraction
<=0.01;

4.
median:
logical:
divergence area
=
0.

ONE-BAD-WITNESS TOLERANCE SIGNAL

TRUE
if:

on:
SILENT_DATA3_PLUS_ONE_WITNESS1:

MAJORITY3:

1.
median:
h1:
logical divergence
=
0;

2.
sustained:
exact:
logical:
recovery
>=0.90;

3.
false-repair:
fraction
<=0.01;

AND:

UNANIMOUS3:

sustained:
exact:
logical:
recovery
is:
lower
than:
MAJORITY3.

This:
tests:
whether:
2-of-3:
quorum

adds:
useful:
fault tolerance

beyond:
strict:
unanimity.

ONE-BAD-WITNESS HEALTHY-TARGET SAFETY

TRUE
if:

on:
ONE_WITNESS1_ONLY:

MAJORITY3:

false repairs:

0

AND:

median:
h4:
logical divergence
=
0.

DISTRIBUTED QUORUM SIGNAL

TRUE
if:

on:
DISTRIBUTED_ONE_BAD_WITNESS:

MAJORITY3:

median:
h4:
logical divergence
=
0

AND:

sustained:
exact:
logical:
recovery
>=0.75.

TWO-BAD-WITNESS BOUNDARY

Flag:
a:
method

if:

on:

SILENT_DATA3_PLUS_TWO_WITNESS2

or:

TWO_WITNESS2_ONLY:

false-repair:
fraction
>
0.10.

Expected:

MAJORITY3

should:
reach:
its:
2-of-3:
fault:
boundary

when:
two:
witnesses
are:
correlated:
wrong.

UNANIMOUS SAFETY SIGNAL

TRUE
if:

UNANIMOUS3:

on:
TWO_WITNESS2_ONLY

has:

false repairs
=
0

and:

median:
h4:
logical divergence
=
0.

Interpretation:

unanimity
may:
sacrifice:
repair:
availability

in:
exchange
for:
greater:
correlated-witness:
safety.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05E:
scenario:

do not alter:

- check graph;
- witness order;
- quorum definitions;
- mapped blocks;
- damage blocks;
- lesion geometry;
- thresholds;
- world family;
- metrics.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

NEXT

If:
ONE_BAD_WITNESS_TOLERANCE_SIGNAL
and:
DISTRIBUTED_QUORUM_SIGNAL
pass:

the:
three-witness:
quorum
extends:
repair:
fault tolerance

under:
the:
same:
128-bit:
budget.

Then:

test:
confidence:
weighting
using:
witness:
health
and:
local:
syndrome
rather:
than:
raw:
equal:
votes.

If:
two-bad:
correlated:
witnesses
break:
MAJORITY3:

treat:
that:
as:
the:
expected:
quorum:
boundary,

not:
as:
a:
failure
of:
the:
one-bad:
witness:
hypothesis.

PLAIN-SPEAK PRE-REGISTERED QUESTION

Two:
neighbors
worked:
beautifully

until:
both:
neighbors
were:
wrong
in:
the:
same:
way.

So:
we:
are:
giving:
the:
important:
repair:
regions

three:
independent:
neighbors

without:
adding:
a:
single:
extra:
persistent:
bit.

If:
one:
neighbor
is:
wrong,

the:
other:
two
should:
outvote:
it.

If:
two:
neighbors
are:
wrong
together,

the:
vote
should:
fail.

That:
would:
give:
us:
a:
clean:
fault-tolerance:
rule:

three:
witnesses

can:
survive:
one:
bad:
witness,

but:
not:
two.

That:
is:
exactly:
the:
kind:
of:
bounded:
local:
repair:
logic

a:
self-checking:
software:
tissue
could:
use.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05E THREE-WITNESS QUORUM

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05E:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05e_three_witness_v1.py

Harness commit:

22d4adb28cc859e68d41a52f56785f7981d033bf.

Git blob SHA:

51504187dee59803a60620aa6966ba1e1839afd4.

Source SHA-256:

3b8305dcf1c56f9a4b3c9ec0c88b669a82bcc97bd0c25126245de555d0e94450.

Source bytes:

12960.

LOCAL PRECHECK

Execution copy:

matches:
the:
authoritative:
remote:
Git blob identity.

Python syntax:

PASS.

No:
DG-1R-05E:
scenario
was:
executed
before:
this:
freeze.

FROZEN CHECK GRAPH

(2,0).
(2,1).
(2,3).

(6,4).
(6,5).
(6,7).

(10,8).
(10,9).
(10,11).

(3,4).
(7,8).

Total:

11:
four-bit:
cross-check:
relations.

Persistent state:

128 bits.

FROZEN WORLD FAMILY

20260926055000..20260926055007.

8 worlds.

REPRODUCIBILITY

Two:
complete:
8-world:
sweeps.

Output SHA-256
must:
match exactly.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05E:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
