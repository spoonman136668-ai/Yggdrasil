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


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05C NEIGHBOR RECONSTRUCTION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE:
THE:
FIRST:
DG-1R-05C:
SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05c_neighbor_reconstruction_v1.py

Harness commit:

beafdbfcbde60cfbad7f4d69e4f67b92799b68d3.

Git blob SHA:

e1171314c4448555b5893e80ce22387d70be511d.

Source SHA-256:

94f4825aab9bffbd67f6aaff03ac3e3fa7925e03c86eaeb67a25614614f7b049.

Source bytes:

13208.

LOCAL PRECHECK

Exact:
Git blob:
identity:

PASS.

Python:
syntax:

PASS.

No:
DG-1R-05C:
world
was:
executed
before:
this:
freeze.

FROZEN PRIMARY DAMAGE BLOCKS

2,
6,
10.

FROZEN DISTRIBUTED DAMAGE BLOCKS

2
and:
10.

FROZEN WORLD FAMILY

20260926053000..20260926053007.

8 worlds.

DG-1R-05 CANONICAL STATUS

Still:

UNSPENT.

DG-1R-05C:

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


FINAL DG-1R-05C NON-EVIDENCE CLOSURE — OVERLAPPING NEIGHBOR RECONSTRUCTION

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE DISTRIBUTED-RECONSTRUCTION RESULT /
TWO-SIDED VALIDATION POSITIVE /
SYNDROME-BLIND THREE-BIT BOUNDARY DISCOVERED /
NON-CANONICAL /
NON-EVIDENCE.

FROZEN HARNESS

Git blob SHA:

e1171314c4448555b5893e80ce22387d70be511d.

Source SHA-256:

94f4825aab9bffbd67f6aaff03ac3e3fa7925e03c86eaeb67a25614614f7b049.

Source bytes:

13208.

CANONICAL OUTPUT FOR THIS NON-EVIDENCE PILOT

RUN 1 SHA-256:

33267aaf8dd074a79acb43bc061a283d445d94168f118ae2bb74e9b4e82ac342.

RUN 2 SHA-256:

33267aaf8dd074a79acb43bc061a283d445d94168f118ae2bb74e9b4e82ac342.

Byte-identical:

PASS.

MECHANICAL VALIDITY

No-damage controls:

PASS.

Lesion-cardinality assertions:

PASS.

mechanical_valid:

TRUE.

FROZEN SIGNALS

NEIGHBOR_RECONSTRUCTION_SIGNAL:

TRUE.

BLOCK_RECONSTRUCTION_SIGNAL:

TRUE.

DISTRIBUTED_TISSUE_SIGNAL:

TRUE.

TWO_SIDED_VALIDATION_VALUE:

TRUE.

TWO-DATA-BIT LOCAL DAMAGE

LOCAL84_GUARD:

median:
logical divergence area:

1.9791666666666665.

sustained:
exact logical recovery rate:

0.375.

h1:
logical divergence:

0.0625.

TISSUE74_XOR_BOTH:

median:
logical divergence area:

0.

physical divergence area:

0.

sustained:
exact logical recovery rate:

1.0.

h1:
logical divergence:

0.

h4:
logical divergence:

0.

false-repair fraction:

0.

Thus:

two:
locally:
damaged:
data bits

that:
exceed:
isolated:
Hamming:
correction capacity

are:

exactly:
reconstructed

from:
independent:
neighbor:
consistency:
relations.

The:
damaged:
organism

returns:
to:
the:
exact:
undamaged:
counterfactual:
trajectory

before:
persistent:
divergence
appears.

DISTRIBUTED TWO-BIT DAMAGE

Two:
separated:
logical:
blocks

are:
simultaneously:
damaged

with:

two:
data-bit:
lesions
per:
block.

TISSUE74_XOR_BOTH:

median:
logical divergence area:

0.

physical divergence area:

0.

sustained:
exact logical recovery rate:

1.0.

h1:
logical divergence:

0.

h4:
logical divergence:

0.

false-repair fraction:

0.

Thus:

distributed:
neighbor reconstruction

operates:
locally
and:
in:
parallel.

No:
global:
repair:
controller
is:
required.

ALL-FOUR-DATA-BIT LOCAL DAMAGE

TISSUE74_XOR_BOTH:

median:
logical divergence area:

0.

physical divergence area:

0.

sustained:
exact logical recovery rate:

1.0.

h1:
logical divergence:

0.

false-repair fraction:

0.

This is:
important.

The:
local:
Hamming:
codeword
alone

cannot:
recover:
four:
lost:
data bits.

But:

the:
neighbor:
relations
carry:
an:
independent:
description
of:
the:
logical:
block.

Both:
neighbors
agree
on:

all:
four:
data bits.

The:
block
can:
therefore:
reconstruct:
its:
entire:
logical:
content.

TWO-SIDED VALIDATION

Damage family:

DATA2_PLUS_LEFT_CHECK1.

Two:
local:
data bits
are:
damaged

plus:

one:
left:
neighbor:
cross-check:
bit.

TISSUE74_XOR_LEFT:

repairs:

24.

false-repair fraction:

1.0.

median:
logical divergence area:

2.125.

sustained:
exact logical recovery rate:

0.20833333333333334.

TISSUE74_XOR_BOTH:

repairs:

0.

abstentions:

24.

false-repair fraction:

0.

median:
logical divergence area:

1.9791666666666665.

sustained:
exact logical recovery rate:

0.375.

Thus:

one-sided:
reconstruction
can:
confidently:
misrepair

when:
its:
single:
recovery:
channel
is:
also:
damaged.

Two-sided:
independent:
agreement

recognizes:
the:
conflict

and:
refuses:
the:
unsafe:
repair.

This:
is:
a:
distributed:
confidence:
mechanism.

DETECT-ONLY CONTROL

TISSUE74_DETECT_ONLY:

TWO_DATA2:

median:
logical divergence area:

1.9791666666666665.

sustained:
exact logical recovery:

0.375.

DISTRIBUTED_TWO_DATA2:

median:
logical divergence area:

3.3020833333333335.

sustained:
exact logical recovery:

0.125.

Thus:

the:
positive:
tissue result

comes:
from:
active:
neighbor:
reconstruction,

not:
merely:
from:
the:
48-bit:
logical:
capacity
or:
cross-check:
representation.

THREE-DATA-BIT BOUNDARY

TISSUE74_XOR_BOTH:

THREE_DATA3:

median:
logical divergence area:

2.3854166666666665.

sustained:
exact logical recovery rate:

0.2916666666666667.

repairs:

0.

abstentions:

0.

Why?

The:
frozen:
three-bit:
lesion

flips:
Hamming:
physical:
positions:

3,
5,
6.

Their:
syndrome:
combination
is:

3 XOR 5 XOR 6
=
0.

Therefore:

the:
damaged:
local:
codeword

presents:

ZERO:
Hamming:
syndrome.

The:
frozen:
repair trigger

requires:

local syndrome
!=
0.

So:

the:
tissue
never:
asks:
its:
neighbors

even though:

the:
left
and:
right:
neighbor:
relations

contain:
enough:
information
to:
reconstruct:
the:
block.

This is:
not:
a:
failure
of:
distributed:
recovery:
information.

It is:
a:
failure
of:
LOCAL:
DAMAGE:
TRIGGERING.

CORE MECHANISTIC CONCLUSION

DG-1R-05C establishes:

OVERLAPPING:
LOCAL:
REDUNDANCY

can:
extend:
repair
far:
beyond:
the:
correction:
radius
of:
an:
isolated:
local:
code.

The:
architecture
now:
has:

1.
LOCAL:
integrity:
checks.

2.
NEIGHBOR:
reconstruction:
channels.

3.
TWO-SIDED:
repair:
validation.

4.
LOCAL:
abstention
when:
independent:
sources
disagree.

This:
resembles:

DISTRIBUTED:
SOFTWARE:
TISSUE

more:
than:

isolated:
error-correcting:
memory.

CAPACITY COST

DG-1R-05C uses:

48:
logical:
data bits

inside:
128:
physical:
bits.

DG-1R-05A/B used:

64:
logical:
data bits

inside:
128:
physical:
bits.

Thus:

the:
strong:
repair:
gain

costs:

25%:
of:
logical:
capacity

relative:
to:
the:
64-bit:
coded:
architecture.

This:
tradeoff
must:
remain:
explicit.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05D —
NEIGHBOR-INCONSISTENCY:
DAMAGE:
TRIGGER /
SYNDROME-BLIND:
REPAIR AUDIT.

Key change:

do NOT:
require:
local:
Hamming:
syndrome
to:
be:
nonzero.

For:
each:
interior:
block:

compute:

- current:
  decoded:
  local:
  data;
- left:
  neighbor-derived:
  candidate;
- right:
  neighbor-derived:
  candidate.

Trigger:
repair
when:

LEFT
==
RIGHT

AND:

CURRENT_LOCAL
!=
LEFT/RIGHT.

Thus:

two:
independent:
neighbors

can:
flag:
a:
locally:
silent:
corruption

even:
when:

local:
syndrome
=
0.

Primary target:

the:
THREE_DATA3:
syndrome-zero:
lesion.

Also test:

NO-DAMAGE:
false-trigger:
rate

and:

cross-check:
damage
to:
ensure:
the:
new:
trigger
does NOT:
turn:
neighbor:
noise
into:
confident:
repair.

PLAIN-SPEAK SUMMARY

This:
worked:
better
than:
the:
isolated:
repair system.

A:
damaged:
block
can:
now:
ask:
both:
neighbors:

"What:
should:
my:
four:
data bits
be?"

When:
both:
neighbors
independently:
give:
the:
same:
answer,

the:
block
can:
restore:
itself.

That:
repaired:

two:
lost:
data bits,

four:
lost:
data bits,

and:

two:
different:
damaged:
blocks
at:
the:
same:
time

back:
to:
the:
exact:
undamaged:
trajectory.

We also:
found:
why:
two:
neighbors
matter.

When:
one:
neighbor:
check
was:
damaged,

a:
one-sided:
repairer
made:
the:
wrong:
repair
every:
time.

The:
two-sided:
repairer
noticed:
the:
neighbors
disagreed

and:
refused:
to:
guess.

The:
remaining:
failure
is:
interesting.

One:
three-bit:
damage pattern
fooled:
the:
local:
Hamming:
check
into:
saying:

"Everything:
looks:
fine."

So:
the:
block
never:
asked:
its:
neighbors
for:
help.

But:
the:
neighbors
actually:
had:
the:
correct:
answer.

The:
next:
test
removes:
that:
blind spot.

Instead of:
waiting:
for:
the:
damaged:
block
to:
announce:
that:
it:
is:
damaged,

the:
neighbors
can:
say:

"Your:
state
does not:
match:
what:
both:
of:
us
independently:
say:
it:
should:
be."

That:
is:
a:
step
toward:
distributed:
self-diagnosis,

not:
just:
distributed:
repair.

DG-1R-05:
canonical frozen primary remains:

UNSPENT.

DG-1R-05C remains:

NON-CANONICAL /
NON-EVIDENCE.

canonical_scientific_execution = false.
stab18_r1_touched = false.
