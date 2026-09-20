TITLE: DG-1R-05C — Overlapping Local Redundancy / Neighbor Reconstruction Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DISTRIBUTED-REPAIR PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED INTEGRITY / SELF-REPAIR
BRANCH: dg1a-ar
PARENT: DG-1R-05B

PURPOSE

DG-1R-05B established:

- single-bit local repair can be exact;
- a same-budget parity guardian detects true two-bit local damage;
- plain Hamming repair confidently misrepairs two-bit damage;
- abstention prevents known-unsafe repair but does not reconstruct lost state;
- therefore:
  repair beyond the local code's capacity requires independent recovery information.

DG-1R-05C asks:

CAN:
NEIGHBORING:
SOFTWARE-CELL:
REGIONS

CARRY:
OVERLAPPING:
CONSISTENCY:
INFORMATION

THAT:
ALLOWS:
A:
LOCALLY:
UNCORRECTABLE:
BLOCK

TO:
RECONSTRUCT:
ITS:
LOST:
STATE?

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

FIXED TOTAL STATE BUDGET

128:
persistent:
bits
for:
every:
method.

FIXED LOGICAL CAPACITY

48:
logical:
data bits
for:
every:
method.

Logical layout:

12:
blocks

x:

4:
data bits.

The:
12:
logical blocks
form:
a:
periodic:
developmental:
chain
for:
CA:
state evolution.

INPUT MAPPING

6:
fixed:
logical:
input positions.

Mapped blocks:

1,
3,
5,
7,
9,
11.

One:
world-specific:
data:
position
inside:
each:
mapped block.

Primary:
damage blocks:

2,
6,
10.

Thus:

primary:
damaged:
logical blocks

are:
not:
directly:
input mapped.

LOGICAL DYNAMICS

One:
MIXED5:
CA update
per:
external:
input

over:
the:
48-bit:
periodic:
logical:
ring.

Rules:

90,
150,
110,
22,
30

with:
world-specific:
frozen:
approximately:
equal:
counts.

Pre-damage:

1024:
external:
steps.

Post-damage:

32:
steps.

Reference
and:
damaged:
clones

receive:
identical:
future:
inputs.

METHOD 1 — LOCAL84_GUARD

12:
SECDED84:
local:
codewords.

12 * 8
=
96 bits.

Remaining:

32 bits

are:
frozen:
inert:
zeros.

Total:

128 bits.

Purpose:

same:
48-bit:
logical:
capacity

with:
strong:
isolated:
local:
integrity

but:

NO:
cross-block:
reconstruction:
relations.

Repair:

- correct:
  single:
  SECDED:
  errors;
- detect:
  double:
  local:
  errors;
- abstain:
  on:
  detected:
  double:
  errors.

METHOD 2 — TISSUE74_XOR_BOTH

Each:
logical:
block:

Hamming(7,4).

Local storage:

12 * 7
=
84 bits.

For:
each:
adjacent:
block pair

j
and:
j+1

for:

j = 0..10

store:

4:
cross-block:
XOR:
check bits:

X_j,k
=
D_j,k
XOR
D_(j+1),k.

11 * 4
=
44:
cross-block:
check bits.

Total:

84 + 44
=
128 bits.

There is:
NO:
wraparound:
cross-check
between:
block 11
and:
block 0.

Primary:
damage blocks
are:

2,
6,
10,

all:
interior:
blocks

with:
both:
left
and:
right:
cross-check:
neighbors.

RECONSTRUCTION RULE

Before:
current:
input:

for:
each:
interior:
logical:
block:

derive:
candidate:
data:
vector
from:
left neighbor:

D_from_left[k]
=
D_left[k]
XOR
X_left_edge[k].

Derive:
candidate
from:
right neighbor:

D_from_right[k]
=
D_right[k]
XOR
X_right_edge[k].

If:

the:
local:
Hamming syndrome
is:
nonzero

AND:

D_from_left
==
D_from_right

for:
all:
4:
logical:
bits,

then:

replace:
the:
block's:
4:
decoded:
data bits

with:
the:
agreed:
neighbor-derived:
vector

and:
re-encode:
its:
local:
Hamming(7,4):
codeword.

If:

left
and:
right:
inferences
disagree:

ABSTAIN.

No:
counterfactual:
reference
is:
visible
to:
the:
repair logic.

METHOD 3 — TISSUE74_XOR_LEFT

Same:
84 + 44:
physical:
representation.

But:
if:
local:
syndrome
is:
nonzero:

reconstruct:
the:
4:
data bits

using:
ONLY:
the:
left:
neighbor /
left:
cross-check.

Purpose:

negative:
robustness control.

It:
tests:

whether:
requiring:
two:
independent:
neighbor:
agreements

adds:
value.

METHOD 4 — TISSUE74_DETECT_ONLY

Same:
84 + 44:
representation.

Compute:

- local:
  Hamming:
  syndrome;
- left:
  inferred:
  data;
- right:
  inferred:
  data;
- agreement:
  state.

But:

perform:
NO:
repair.

Purpose:

separate:
distributed:
representation

from:
active:
neighbor:
reconstruction.

REPAIR / INPUT ORDER

1.
inspect:
persistent:
pre-input:
local:
and:
cross-block:
checks;

2.
perform:
allowed:
repair /
abstention;

3.
decode:
48:
logical:
data bits;

4.
apply:
current:
external:
input:
overwrite;

5.
one:
logical:
MIXED5:
CA:
update;

6.
recompute:
all:
12:
local:
codewords;

7.
recompute:
all:
11:
cross-block:
XOR:
relations;

8.
persist:
the:
new:
128-bit:
state.

DAMAGE FAMILIES

Harness MUST:
assert:
actual:
lesion:
cardinality
before:
evolution.

Per:
primary:
damage block:

TWO_DATA2

Flip:
the:
physical:
Hamming:
positions
holding:

d1
and:
d2.

Actual:
lesion size:

2.

THREE_DATA3

Flip:
positions
holding:

d1,
d2,
d3.

Actual:
lesion size:

3.

ALL_DATA4

Flip:
positions
holding:

d1,
d2,
d3,
d4.

Actual:
lesion size:

4.

DATA2_PLUS_LEFT_CHECK1

Flip:

d1,
d2

inside:
the:
damaged:
local:
block

plus:

the:
left:
cross-check:
bit
for:
d1.

Actual:
lesion size:

3.

Purpose:

test:
whether:
two-sided:
agreement
detects:
corruption
of:
one:
reconstruction:
source.

DISTRIBUTED_TWO_DATA2

Damage:

block 2:
d1,
d2.

block 10:
d1,
d2.

Actual:
lesion size:

4.

Purpose:

test:
simultaneous:
multi-block:
neighbor:
reconstruction.

COUNTERFACTUAL METRICS

At:

1,
4,
8,
16,
32:
steps

report:

- whole-state divergence;
- damaged-site recovery;
- logical-data divergence;
- outside-lesion divergence;
- spread count;
- exact physical-state match;
- exact logical-state match.

Also:

- physical:
  divergence area;
- logical:
  divergence area;
- sustained:
  exact logical recovery rate;
- recovery time.

REPAIR TELEMETRY

Per:
method /
family:

- local syndrome positives;
- neighbor:
  reconstruction attempts;
- left/right:
  agreement count;
- disagreement /
  abstention count;
- repairs;
- false repairs;
- repair:
  logical-bit:
  change count.

FALSE REPAIR

A:
repair
is:
FALSE

if:

the:
proposed:
neighbor-derived:
logical:
data vector

does NOT:
match:

the:
counterfactual:
reference:
logical:
data vector

immediately:
before:
repair.

Repair logic:

never:
sees:
this:
evaluation:
label.

PRIMARY SIGNAL — NEIGHBOR RECONSTRUCTION

TRUE
if:

TISSUE74_XOR_BOTH

on:
TWO_DATA2:

1.
median:
logical divergence
at:
h1
=
0;

2.
sustained:
exact logical:
recovery rate
>=0.90;

3.
median:
logical divergence area
at least:
75%:
lower

than:
LOCAL84_GUARD;

4.
false-repair fraction
<=0.01.

BLOCK RECONSTRUCTION SIGNAL

TRUE
if:

TISSUE74_XOR_BOTH

on:

THREE_DATA3
or:
ALL_DATA4

has:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact logical recovery rate
>=0.75.

DISTRIBUTED TISSUE SIGNAL

TRUE
if:

DISTRIBUTED_TWO_DATA2:

TISSUE74_XOR_BOTH

has:

median:
logical divergence
at:
h4
=
0

AND:

sustained:
exact logical recovery rate
>=0.75.

TWO-SIDED VALIDATION VALUE

TRUE
if:

on:
DATA2_PLUS_LEFT_CHECK1:

TISSUE74_XOR_BOTH

has:

false-repair fraction

at least:
50%:
lower

than:

TISSUE74_XOR_LEFT.

Interpretation:

two:
independent:
neighbor:
relations

help:
the:
repair system
recognize:
when:
one:
reconstruction:
source
has:
also:
been:
damaged.

REDUNDANCY-CAPACITY TRADEOFF

This:
experiment
uses:

48:
logical:
data bits

inside:
128:
physical:
bits.

DG-1R-05A/B
used:

64:
logical:
data bits

inside:
128:
physical:
bits.

Therefore:

a:
positive:
result
must:
be:
interpreted
with:
the:
explicit:
cost:

more:
repair:
redundancy

for:

less:
independent:
logical:
state.

No:
claim
may:
hide:
this:
capacity:
tradeoff.

WORLD FAMILY

8:
worlds.

Seeds:

20260926053000
through:
20260926053007.

No:
prior:
DG-1R:
seed reuse.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05C:
scenario:

do not alter:

- 48-bit:
  logical:
  capacity;
- local:
  Hamming:
  code;
- cross-block:
  XOR:
  relations;
- damage blocks;
- lesion:
  geometry;
- two-sided:
  agreement:
  rule;
- method:
  definitions;
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
parity guardian
can:
say:

"I know:
this:
block
is:
too:
damaged
for:
me
to:
repair
safely."

But:
it:
still:
does not:
know:
the:
missing:
bits.

So:
now:
neighboring:
blocks
carry:
small:
consistency:
checks
about:
each:
other.

A:
damaged:
block
can:
ask:

"My:
left:
neighbor
says:
my:
four:
data bits
should:
look:
like:
this.

My:
right:
neighbor
independently
says:
the:
same:
thing.

Do:
they:
agree?"

If:
both:
neighbors:
independently:
reconstruct:
the:
same:
local:
state,

the:
block
can:
repair:
itself.

If:
they:
disagree,

it:
abstains.

This:
costs:
logical:
capacity.

We:
are:
using:
more:
of:
the:
same:
128:
bits
for:
integrity

and:
fewer:
for:
independent:
data.

But:
if:
it:
works,

we:
will:
have:
moved
from:

isolated:
repair:

to:

distributed:
software:
tissue
where:
neighboring:
regions
help:
reconstruct:
one:
another.

canonical_scientific_execution = false.
stab18_r1_touched = false.
