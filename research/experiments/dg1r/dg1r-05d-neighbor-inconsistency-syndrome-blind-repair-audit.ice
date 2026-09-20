TITLE: DG-1R-05D — Neighbor-Inconsistency Trigger / Syndrome-Blind Repair Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DISTRIBUTED-DIAGNOSIS PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / SELF-DIAGNOSIS
BRANCH: dg1a-ar
PARENT: DG-1R-05C

PURPOSE

DG-1R-05C showed:

- overlapping neighbor redundancy can exactly reconstruct two-bit and four-bit local data loss;
- distributed separated lesions can be repaired in parallel;
- two-sided agreement prevents false repair when one recovery channel is damaged;
- a three-data-bit lesion remained unrepaired because its local Hamming syndrome was zero.

The three-bit failure was therefore:

not:
missing:
repair information,

but:

missing:
damage:
triggering.

DG-1R-05D asks:

CAN:
NEIGHBOR:
INCONSISTENCY

DIAGNOSE:
A:
LOCALLY:
SILENT:
CORRUPTION

AND:
TRIGGER:
REPAIR

WITHOUT:
CREATING:
UNACCEPTABLE:
FALSE:
REPAIRS?

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

Exact:
DG-1R-05C:
tissue representation.

128:
persistent bits.

48:
logical:
data bits.

12:
logical:
blocks
x
4:
data bits.

Local:
Hamming(7,4)
storage:

84 bits.

Neighbor:
cross-block:
XOR checks:

44 bits.

Total:

128.

LOGICAL DYNAMICS

Exact:
DG-1R-05C:

one:
MIXED5:
CA update
per:
external input
over:
48:
logical:
bits.

Pre-damage:

1024 steps.

Post-damage:

32 steps.

METHOD 1 — SYNDROME_TRIGGER

Exact:
DG-1R-05C:
TISSUE74_XOR_BOTH.

For:
an:
interior:
block:

compute:

local:
Hamming:
syndrome.

Compute:

left:
neighbor-derived:
candidate.

Compute:

right:
neighbor-derived:
candidate.

Repair only if:

local syndrome
!=0

AND:

left candidate
==
right candidate.

Purpose:

frozen:
parent:
reference.

METHOD 2 — NEIGHBOR_TRIGGER

For:
every:
interior:
block:

decode:
current:
local:
data.

Derive:

left candidate.

Derive:

right candidate.

If:

left candidate
==
right candidate

AND:

current local data
!=
neighbor candidate,

then:

repair:
the:
local:
data
to:
the:
neighbor:
candidate

regardless:
of:
local:
Hamming:
syndrome.

Thus:

neighbor:
consensus

can:
flag:
a:
locally:
silent:
corruption.

If:

left candidate
!=
right candidate:

ABSTAIN.

METHOD 3 — HYBRID_TRIGGER

Repair if:

A.
local syndrome
!=0
AND
left == right;

OR:

B.
local syndrome
==0
AND
left == right
AND
current != left.

This is:
operationally:
equivalent:
to:
NEIGHBOR_TRIGGER
for:
repair decisions,

but:

telemetry
must:
separate:

SYNDROME-LED repairs

from:

SYNDROME-BLIND:
neighbor-led:
repairs.

Purpose:

make:
the:
mechanistic:
path
explicit.

METHOD 4 — ONE_SIDE_TRIGGER

For:
an:
interior:
block:

derive:
left:
neighbor:
candidate.

If:

current local
!=
left candidate:

repair:
to:
left candidate

regardless:
of:
syndrome.

Purpose:

negative:
confidence:
control.

METHOD 5 — DETECT_ONLY

Compute:

- local syndrome;
- left candidate;
- right candidate;
- current mismatch;
- left/right agreement.

Perform:

NO:
repair.

Purpose:

representation /
diagnostic:
control.

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
logical:
48-bit:
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
recompute:
local:
Hamming:
codewords;

7.
recompute:
neighbor:
XOR:
checks.

INPUT MAPPING

Exact:
DG-1R-05C.

Mapped blocks:

1,
3,
5,
7,
9,
11.

Primary damage blocks:

2,
6,
10.

DAMAGE FAMILIES

Harness MUST:
assert:
actual:
lesion:
cardinality.

THREE_DATA3_SILENT

Inside:
one:
primary:
damage:
block

flip:

d1,
d2,
d3

at:
Hamming:
physical:
positions:

3,
5,
6.

Actual lesion size:

3.

Frozen property:

local:
Hamming:
syndrome
=
0.

Purpose:

primary:
syndrome-blind:
repair target.

TWO_DATA2

Flip:

d1,
d2.

Actual lesion size:

2.

Purpose:

confirm:
ordinary:
neighbor reconstruction
remains:
intact.

LEFT_CHECK1_ONLY

No:
local:
data damage.

Flip:

left:
cross-check:
bit
for:
d1.

Actual lesion size:

1.

Expected:

left candidate
!=
right candidate.

Two-sided:
methods
should:
ABSTAIN.

ONE_SIDE_TRIGGER
is:
expected:
to:
risk:
false repair.

BOTH_CHECK1_CORRELATED

No:
local:
data damage.

Flip:

left:
cross-check:
bit
for:
d1

AND:

right:
cross-check:
bit
for:
d1.

Actual lesion size:

2.

This:
creates:

two:
independent:
reconstruction:
channels

that:
now:
agree
on:
the:
same:
WRONG:
d1:
value.

Purpose:

test:
the:
boundary
of:
two-source:
consensus.

This is:

CORRELATED:
INTEGRITY:
DAMAGE.

DATA3_PLUS_LEFT_CHECK1

Flip:

local:
d1,
d2,
d3

plus:

left:
cross-check:
d1.

Actual lesion size:

4.

Purpose:

test:
whether:
the:
two-sided:
method
abstains
when:

the:
block
is:
silent-corrupt

and:

one:
reconstruction:
source
is:
also:
damaged.

DISTRIBUTED_SILENT3

Simultaneously:

block 2:
d1,d2,d3.

block 10:
d1,d2,d3.

Actual lesion size:

6.

Purpose:

test:
parallel:
syndrome-blind:
diagnosis.

PRIMARY METRICS

Counterfactual:
physical
and:
logical:
divergence
at:

1,
4,
8,
16,
32.

Also:

- logical:
  divergence area;
- physical:
  divergence area;
- sustained:
  exact:
  logical:
  recovery;
- recovery time;
- repair count;
- false repair count;
- abstentions;
- syndrome-led repairs;
- syndrome-blind repairs;
- neighbor:
  agreement count;
- neighbor:
  disagreement count.

FALSE REPAIR

A:
proposed:
logical:
repair vector

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
block

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
evaluation:
label.

SYNDROME-BLIND REPAIR SIGNAL

TRUE
if:

on:
THREE_DATA3_SILENT:

NEIGHBOR_TRIGGER
or:
HYBRID_TRIGGER

has:

1.
median:
logical divergence
at:
h1
=
0;

2.
sustained:
exact logical recovery
>=0.90;

3.
false repair fraction
<=0.01;

4.
median:
logical divergence area
=
0.

DISTRIBUTED SELF-DIAGNOSIS SIGNAL

TRUE
if:

on:
DISTRIBUTED_SILENT3:

HYBRID_TRIGGER

has:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact logical recovery
>=0.75.

ONE-SOURCE DAMAGE SAFETY

TRUE
if:

on:
LEFT_CHECK1_ONLY:

HYBRID_TRIGGER:

false repair count
=
0

AND:

median:
logical divergence
at:
h4
=
0.

CORRELATED-CONSENSUS FAILURE

Flag:
a:
two-sided:
method

if:

on:
BOTH_CHECK1_CORRELATED:

false repair fraction
>0.10.

This:
is:
expected
to:
bound:
the:
two-neighbor:
consensus:
model.

It tests:

whether:
two:
matching:
integrity:
channels

can:
still:
fail
under:
correlated:
damage.

PRIMARY INTERPRETATION

A:
positive:
syndrome-blind:
result
would show:

damage:
diagnosis

does NOT:
need:
to:
originate
inside:
the:
damaged:
region.

Healthy:
neighbors

can:
identify:

"your:
state
is:
inconsistent
with:
the:
state
we:
both:
independently:
expect."

A:
correlated-consensus:
failure

would:
show:

agreement:
alone
is:
not:
absolute:
proof.

The:
next:
architecture
would:
need:

- more:
  independent:
  witnesses;
- confidence:
  weighting;
- spatial:
  diversity;
- or:
  repair:
  quorum.

WORLD FAMILY

8:
worlds.

Seeds:

20260926054000
through:
20260926054007.

No:
prior:
DG-1R:
seed reuse.

NO POST-RUN TUNING

After:
the:
first:
scenario:

do not alter:

- trigger definitions;
- cross-check relations;
- damage geometry;
- damage blocks;
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

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
software tissue
could:
repair:
a:
damaged:
block

if:
the:
block
knew:
it:
was:
damaged.

But:
one:
three-bit:
damage pattern
fooled:
the:
block's:
own:
check.

The:
block
thought:
it:
was:
fine.

Its:
neighbors,
however,
both:
had:
enough:
information
to:
see:

"Your:
four:
data bits
do not:
match:
what:
both:
of:
us
say:
they:
should:
be."

This:
experiment
lets:
the:
neighbors
trigger:
the:
repair.

We:
also:
damage:
the:
neighbor:
checks
themselves.

One:
bad:
neighbor
should:
cause:
disagreement
and:
make:
the:
tissue
refuse:
to:
guess.

But:
if:
both:
neighbor:
checks
are:
damaged
in:
the:
same:
way,

they:
may:
agree
on:
the:
same:
wrong:
answer.

That:
tests:
how:
far:
two-source:
consensus
can:
be:
trusted.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05D SYNDROME-BLIND NEIGHBOR DIAGNOSIS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05D:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05d_syndrome_blind_v1.py

Harness commit:

c0e249b58bdeaebc6a4bfab5588d343922875ca8.

Git blob SHA:

3b908ac1f6d0fe70b319174be7be9e109a8ee95b.

Source SHA-256:

58786992dbb9c7ca11e16ca9e68df0617a0abb35b8cd5e208696291c880aea91.

Source bytes:

11012.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python:
syntax:

PASS.

No:
DG-1R-05D:
scenario
was:
executed
before:
this:
freeze.

FROZEN WORLD FAMILY

20260926054000..20260926054007.

8 worlds.

FROZEN DAMAGE FAMILIES

THREE_DATA3_SILENT.

TWO_DATA2.

LEFT_CHECK1_ONLY.

BOTH_CHECK1_CORRELATED.

DATA3_PLUS_LEFT_CHECK1.

DISTRIBUTED_SILENT3.

DG-1R-05 CANONICAL STATUS

Still:

UNSPENT.

DG-1R-05D:

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
