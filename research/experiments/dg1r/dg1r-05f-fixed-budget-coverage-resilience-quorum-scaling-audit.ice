TITLE: DG-1R-05F — Fixed-Budget Coverage / Resilience Quorum-Scaling Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE QUORUM-SCALING PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / COVERAGE-RESILIENCE TRADEOFF
BRANCH: dg1a-ar
PARENT: DG-1R-05E

PURPOSE

DG-1R-05E established:

- 3 witnesses with 2-of-3 quorum repair syndrome-silent damage;
- one bad witness is tolerated;
- two correlated bad witnesses defeat 2-of-3 quorum;
- unanimity remains safer but loses repair availability.

DG-1R-05F asks:

UNDER:
THE:
SAME:
128-BIT:
PERSISTENT:
STATE BUDGET,

can:
the:
organism

spend:
more:
integrity:
relations

on:
fewer:
regions

to:
increase:
local:
fault:
tolerance?

Specifically:

compare:

3-witness:
2-of-3:
quorum

against:

5-witness:
3-of-5:
quorum.

The:
expected:
fault:
boundary:

2-of-3:
tolerates:
1:
bad:
witness.

3-of-5:
tolerates:
2:
bad:
witnesses.

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
bits
per:
block.

48:
logical:
data bits.

12:
Hamming(7,4):
local:
codewords.

84:
local:
physical:
bits.

11:
four-bit:
cross-integrity:
relations.

44:
cross:
bits.

Total:

128:
persistent:
bits.

No:
hidden:
memory.

FIVE-WITNESS CHECK GRAPH

PRIMARY TARGET A:

block 2.

Direct witnesses:

0,
1,
3,
4,
5.

Edges:

E0:
(2,0).

E1:
(2,1).

E2:
(2,3).

E3:
(2,4).

E4:
(2,5).

PRIMARY TARGET B:

block 9.

Direct witnesses:

6,
7,
8,
10,
11.

Edges:

E5:
(9,6).

E6:
(9,7).

E7:
(9,8).

E8:
(9,10).

E9:
(9,11).

CONNECTOR:

E10:
(5,6).

Total:

11:
four-bit:
relations.

44:
integrity bits.

PRIMARY PROTECTED REGION COUNT

2.

DG-1R-05E:
protected:

3:
regions
with:
3:
witnesses
each.

DG-1R-05F:
protects:

2:
regions
with:
5:
witnesses
each.

Thus:

resilience
is:
increased

by:
reducing:
coverage

under:
the:
same:
integrity:
budget.

LOGICAL DYNAMICS

One:
MIXED5:
CA update

per:
external:
input

over:
48:
logical:
bits.

After:
each:
step:

recompute:

- all:
  local:
  Hamming:
  codewords;

- all:
  11:
  cross-integrity:
  vectors.

REPAIR ORDER

1.
inspect:
persistent:
pre-input:
state;

2.
perform:
allowed:
quorum:
repair /
abstention;

3.
decode:
logical:
state;

4.
apply:
current:
input;

5.
one:
logical:
MIXED5:
update;

6.
re-encode:
local:
state;

7.
recompute:
cross-integrity:
relations.

INPUT MAPPING

Mapped logical blocks:

1,
3,
5,
6,
8,
11.

Primary targets:

2,
9

are:
not:
input mapped.

METHOD 1 — MAJORITY3_FIRST3

For:
each:
target:

use:
the:
first:
three:
frozen:
witnesses.

If:
at least:
2:
of:
3:
candidate:
vectors

are:
identical:

that:
is:
the:
repair:
candidate.

If:
current:
target
differs:

repair.

Purpose:

within-architecture:
2-of-3:
reference.

METHOD 2 — MAJORITY5

Use:
all:
five:
witnesses.

Count:
exact:
four-bit:
candidate:
vectors.

If:
one:
candidate:
vector
appears:

at least:
3:
times,

it:
is:
the:
repair:
candidate.

If:
no:
candidate
reaches:
3:

ABSTAIN.

If:
current:
target
differs:
from:
candidate:

repair.

Purpose:

3-of-5:
two-fault:
tolerant:
quorum.

METHOD 3 — UNANIMOUS5

Repair only if:

all:
five:
candidate:
vectors

are:
identical

and:
current:
target
differs.

Otherwise:

ABSTAIN.

Purpose:

high-safety /
low-availability:
control.

METHOD 4 — DETECT_ONLY

Compute:
all:
candidate:
vectors
and:
vote:
distribution.

Perform:

NO:
repair.

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
post-damage:
steps.

WORLD FAMILY

8:
worlds.

Seeds:

20260926056000
through:
20260926056007.

DAMAGE TARGETS

2.
9.

Harness MUST:
assert:

- exact:
  lesion:
  cardinality;
- unique:
  lesion:
  indices;
- no:
  local:
  lesion:
  overlaps:
  mapped:
  physical:
  input:
  positions.

SILENT LOCAL DAMAGE

For:
a:
target:

flip:
local:
Hamming:
data positions:

3,
5,
6

corresponding:

d1,
d2,
d3.

Actual local lesion:

3 bits.

Frozen property:

local:
Hamming syndrome
=
0.

WITNESS DAMAGE

For:
target:
T,

the:
five:
incident:
witness:
edges

are:
ordered:
as:
listed.

A:
bad:
witness
is:
created
by:

flipping:
the:
d1:
bit
of:
that:
edge's:
four-bit:
cross-check.

Multiple:
bad:
witnesses

use:
the:
same:
d1:
flip

so:

their:
wrong:
candidate:
vectors

are:
correlated
and:
agree.

DAMAGE FAMILY A — SILENT_DATA3

Local:
silent:
damage only.

Actual lesion size:

3.

DAMAGE FAMILY B — DATA3_PLUS_ONE_BAD

Local:
silent:
damage

plus:

first:
bad:
witness.

Actual lesion size:

4.

DAMAGE FAMILY C — DATA3_PLUS_TWO_BAD

Local:
silent:
damage

plus:

first
and:
second:
bad:
witness.

Actual lesion size:

5.

Primary:
3-of-5:
recovery:
test.

DAMAGE FAMILY D — DATA3_PLUS_THREE_BAD

Local:
silent:
damage

plus:

first,
second,
third:
bad:
witness.

Actual lesion size:

6.

Expected:

3-of-5:
failure:
boundary.

DAMAGE FAMILY E — TWO_BAD_ONLY

Healthy:
target.

First
and:
second:
witnesses
corrupted.

Actual lesion size:

2.

Purpose:

healthy-target:
safety
under:
two:
bad:
witnesses.

DAMAGE FAMILY F — THREE_BAD_ONLY

Healthy:
target.

First,
second,
third:
witnesses
corrupted.

Actual lesion size:

3.

Expected:

3-of-5:
false-consensus:
boundary.

DAMAGE FAMILY G — DISTRIBUTED_TWO_BAD

Both:
target:
blocks:

2
and:
9

receive:

SILENT_DATA3

plus:

two:
bad:
witnesses
each.

Actual lesion size:

10.

Purpose:

parallel:
two-fault:
quorum:
repair.

PRIMARY METRICS

At:

1,
4,
8,
16,
32:

- logical divergence;
- whole-state divergence;
- outside-lesion divergence;
- exact logical match.

Also:

- logical divergence area;
- physical divergence area;
- sustained exact logical recovery;
- repair count;
- false repair count;
- abstentions;
- maximum vote count;
- 5-0 unanimous count;
- 4-1 count;
- 3-2 count;
- no-quorum count.

FALSE REPAIR

A:
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
target

immediately:
before:
repair.

TWO-BAD-WITNESS TOLERANCE SIGNAL

TRUE
if:

on:
DATA3_PLUS_TWO_BAD:

MAJORITY5:

1.
median:
h1:
logical divergence
=
0;

2.
sustained:
exact:
logical recovery
>=0.90;

3.
false-repair:
fraction
<=0.01;

4.
median:
logical divergence area
=
0;

AND:

MAJORITY3_FIRST3

does NOT:
meet:
all:
four:
conditions.

HEALTHY-TARGET TWO-BAD SAFETY

TRUE
if:

on:
TWO_BAD_ONLY:

MAJORITY5:

false repairs:

0

AND:

median:
h4:
logical divergence
=
0.

DISTRIBUTED TWO-BAD QUORUM SIGNAL

TRUE
if:

on:
DISTRIBUTED_TWO_BAD:

MAJORITY5:

median:
h4:
logical divergence
=
0

AND:

sustained:
exact:
logical recovery
>=0.75.

THREE-BAD-WITNESS BOUNDARY

Flag:
MAJORITY5

if:

on:
DATA3_PLUS_THREE_BAD

or:
THREE_BAD_ONLY:

false-repair fraction
>
0.10.

Expected:

3:
correlated:
bad:
witnesses

can:
outvote:
2:
healthy:
witnesses.

UNANIMOUS5 SAFETY SIGNAL

TRUE
if:

on:
THREE_BAD_ONLY:

UNANIMOUS5:

false repairs:

0

AND:

median:
h4:
logical divergence
=
0.

COVERAGE / RESILIENCE REPORT

Report:

DG-1R-05E architecture:

protected regions:

3.

witnesses per protected region:

3.

faulty witnesses tolerated by majority quorum:

1.

DG-1R-05F architecture:

protected regions:

2.

witnesses per protected region:

5.

faulty witnesses tolerated by majority quorum:

2.

Persistent state:

128 bits
for:
both.

Cross-integrity state:

44 bits
for:
both.

This:
is:
a:
descriptive:
resource:
tradeoff,

not:
a:
winner:
claim.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05F:
scenario:

do not alter:

- graph;
- target blocks;
- witness order;
- quorum definitions;
- input blocks;
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
TWO_BAD_WITNESS_TOLERANCE_SIGNAL
and:
DISTRIBUTED_TWO_BAD_QUORUM_SIGNAL
pass:

the:
fixed:
integrity:
budget

supports:
a:
real:
coverage /
resilience:
tradeoff.

Next:

test:
developmental:
allocation:

can:
the:
organism
decide:

which:
regions
deserve:

3:
witnesses

versus:

5:
witnesses

based:
on:
damage:
history /
functional:
importance /
repair:
load

without:
a:
global:
designer?

PLAIN-SPEAK PRE-REGISTERED QUESTION

We:
already:
proved:

three:
witnesses
can:
survive:
one:
bad:
witness.

Now:

we:
spend:
the:
same:
amount:
of:
integrity:
memory

differently.

Instead:
of:
protecting:
three:
regions
with:
three:
witnesses
each,

we:
protect:
two:
regions
with:
five:
witnesses
each.

A:
3-of-5:
vote
should:
survive:
two:
bad:
witnesses.

Three:
bad:
witnesses
should:
still:
break:
it.

If:
that:
happens,

we:
will:
have:
measured:
a:
real:
resource:
tradeoff:

protect:
more:
of:
the:
organism
less:
strongly,

or:

protect:
less:
of:
the:
organism
more:
strongly.

That:
is:
the:
kind:
of:
resource:
allocation
a:
developmental:
self-healing:
system
eventually:
needs:
to:
learn:
for:
itself.

canonical_scientific_execution = false.
stab18_r1_touched = false.
