TITLE: DG-1R-06 — Redundant Local Encoding / Counterfactual Reconstruction Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE LOCAL ERROR-CORRECTION PILOT
TRACK: DG-1R / SOFTWARE CELLS / DISTRIBUTED REDUNDANCY / SELF-REPAIR
BRANCH: dg1a-ar
PARENT: DG-1R-05
PARENT_CLOSURE: 6df189674589c82727b68ccc5cae740968654278

PURPOSE

DG-1R-05 established:

- H6 nanites can strongly contain finite lesions;
- N16_H6_REPAIR reduced median cumulative trajectory divergence by ~42.7%;
- N16_H6_REPAIR reduced median h32 outside-lesion divergence by ~74.6%;
- but:
  one-bit local controllers did NOT reconstruct the destroyed lesion state.

Therefore:

the missing mechanism is hypothesized to be:

REDUNDANT /
RECONSTRUCTABLE:
LOCAL INFORMATION.

DG-1R-06 asks:

CAN:
LOCAL:
REDUNDANCY

CONSUMING:
REAL:
BITS
FROM:
THE:
SAME:
128-BIT:
ORGANISM

ALLOW:
A:
PURELY:
LOCAL:
DECODER

TO:
RECONSTRUCT:
DAMAGED:
STATE

AND:
RETURN:
EXACTLY
TO:
THE:
UNDAMAGED:
COUNTERFACTUAL:
TRAJECTORY?

MOTIVATION

Recent GNCA analysis reports:
recovery-associated:
increases:
in:
redundant:
coordination.

Classical:
fault-tolerant:
cellular-automata:
work

also:
uses:
redundancy
plus:
local:
correction
to:
protect:
distributed:
state.

These:
external:
results
are:
motivation only.

DG-1R-06
must:
supply:
its:
own:
mechanical:
evidence.

BOUNDARY

Synthetic software only.

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

FIXED PHYSICAL STATE BUDGET

Every method:

128:
persistent:
binary:
bits.

No:
shadow:
copy.

No:
external:
history.

No:
counterfactual:
reference
available:
to:
the:
organism.

No:
task:
label.

No:
future:
target.

LOGICAL DYNAMIC STATE

64:
logical:
worker:
bits.

They form:

one:
periodic:
64-bit:
worker ring.

Worker rule assignment:

world-specific:
MIXED5

from:

90,
150,
110,
22,
30

with:
approximately:
equal:
counts.

Worker clock:

one:
CA:
update
per:
external:
input.

INPUT

u_t ~ Bernoulli(0.5).

Input recurrence:

OVERWRITE.

64:
logical:
worker:
positions

are:
partitioned
into:

8:
contiguous:
8-worker:
input compartments.

At:
world initialization:

choose:
one:
mapped:
logical:
worker
inside:
each:
8-worker:
compartment.

Total:

8:
mapped:
logical:
workers.

Same:

input stream,
mapping,
and:
logical:
worker rules

for:
all:
methods
inside:
one:
world.

METHOD 1 — UNCODED64_PAD64

64:
logical:
worker bits

stored:
directly
in:
physical:
positions:
0..63.

Physical:
positions:
64..127

are:
fixed:
zero:
padding.

Thus:

physical:
state:
budget:

128 bits.

Logical:
dynamic:
capacity:

64 bits.

Per:
external:
step:

1.
overwrite:
mapped:
logical:
workers
with:
u_t;

2.
evolve:
the:
64-bit:
MIXED5:
worker ring
one:
CA step;

3.
write:
the:
64:
worker bits
to:
physical:
positions:
0..63;

4.
reset:
padding:
64..127
to:
zero.

Purpose:

same:
logical:
capacity
and:
same:
worker:
dynamics

as:
the:
coded:
method

but:
without:
redundant:
repair:
information.

METHOD 2 — SECDED64_LOCAL

16:
independent:
8-bit:
local:
code blocks.

Each:
block

stores:

4:
logical:
worker:
data bits

using:

extended:
Hamming:
SECDED:

[8,4,4].

Across:

16 blocks:

64:
logical:
worker bits

consume:

128:
physical:
bits.

Thus:

50%:
of:
physical:
state

is:
explicit:
local:
redundancy.

This:
redundancy
is:
NOT:
free.

BLOCK LAYOUT

Within:
each:
8-bit:
physical:
block,

using:
1-based:
Hamming:
positions:

1:
P1.

2:
P2.

3:
D0.

4:
P4.

5:
D1.

6:
D2.

7:
D3.

8:
P8:
overall:
even:
parity.

ENCODING

For:
data:

D0,
D1,
D2,
D3.

P1
=
D0
XOR
D1
XOR
D3.

P2
=
D0
XOR
D2
XOR
D3.

P4
=
D1
XOR
D2
XOR
D3.

P8
=
P1
XOR
P2
XOR
D0
XOR
P4
XOR
D1
XOR
D2
XOR
D3.

Thus:

all:
four:
SECDED:
parity checks
are:
even.

LOCAL DECODER

Before:
every:
external:
input,

each:
8-bit:
block
is:
decoded
independently.

Syndrome:

S1:
XOR:
positions:
1,
3,
5,
7.

S2:
XOR:
positions:
2,
3,
6,
7.

S4:
XOR:
positions:
4,
5,
6,
7.

syndrome
=
S1
+
2*S2
+
4*S4.

Overall parity:

XOR:
positions:
1..8.

Cases:

A.
syndrome = 0
AND:
overall = 0.

NO ERROR.

B.
syndrome != 0
AND:
overall = 1.

SINGLE:
error
in:
positions:
1..7.

Flip:
physical:
position:
syndrome.

C.
syndrome = 0
AND:
overall = 1.

SINGLE:
error
in:
position:
8.

Flip:
position:
8.

D.
syndrome != 0
AND:
overall = 0.

DOUBLE:
error
detected.

DO NOT:
correct.

The:
decoder:
has:
no:
external:
information.

TRIPLE-ERROR LIMIT

A:
three-bit:
error

may:
masquerade
as:
a:
single:
error

under:
SECDED.

DG-1R-06
does NOT:
hide:
this:
limit.

It:
measures:
it
explicitly.

NORMAL SECDED64 STEP

At:
the:
start:
of:
each:
external:
step:

1.
run:
local:
SECDED:
decode /
correction
on:
all:
16:
blocks;

2.
extract:
64:
logical:
data bits;

3.
overwrite:
mapped:
logical:
workers
with:
u_t;

4.
evolve:
the:
64-bit:
MIXED5:
worker ring
one:
CA step;

5.
re-encode:
all:
16:
local:
code blocks.

Thus:

redundancy
is:
refreshed
from:
the:
new:
healthy:
logical:
state
after:
every:
worker:
evolution.

PRE-DAMAGE DEVELOPMENT

Per world:

1056:
iid:
binary:
input steps.

Use:

0..1023

as:
common:
pre-damage:
development.

Damage:

after:
step:
1023

and:
before:
the:
decoder /
input
for:
step:
1024.

Post-damage:

32:
future:
input steps:

1024..1055.

REFERENCE /
DAMAGED PAIR

For:
each:
method
and:
damage scenario:

REFERENCE:

undamaged:
clone.

DAMAGED:

same:
state
plus:
frozen:
physical:
bit flips.

Both:

receive:
identical:
future:
input.

Reference:
trajectory
is:
measurement only.

The:
damaged:
organism
never:
sees:
it.

LESION BLOCK SELECTION

The:
64:
logical:
workers

contain:

16:
4-worker:
code blocks.

Each:
8-worker:
input compartment

contains:

2:
code blocks

but:
only:
one:
mapped:
logical:
input:
position.

Define:

UNMAPPED:
SIBLING:
CODE BLOCK

as:
the:
4-worker:
block
inside:
that:
8-worker:
input:
compartment

which:
does NOT:
contain:
the:
mapped:
input:
worker.

This:
guarantees:

future:
input overwrite
does NOT:
trivially:
erase:
the:
damaged:
logical:
worker.

FROZEN DAMAGE FAMILIES

A.
SPREAD4.

Use:
input compartments:

0,
2,
4,
6.

In:
the:
unmapped:
sibling:
code block
of:
each:

flip:

logical:
data offset:
1

inside:
that:
4-worker:
block.

Total:

4:
damaged:
logical:
worker bits.

Distribution:

one:
error
per:
SECDED:
codeword.

Expected:
code capacity:

correctable.

B.
SPREAD8.

Use:
all:
8:
input:
compartments.

In:
each:
unmapped:
sibling:
code block:

flip:

logical:
data offset:
1.

Total:

8:
damaged:
logical:
worker bits.

Distribution:

one:
error
per:
codeword.

Expected:
code capacity:

correctable
independently
in:
all:
8:
blocks.

C.
LOCAL2.

Use:
input compartment:
0.

Inside:
its:
unmapped:
sibling:
code block:

flip:
logical:
data offsets:

1,
2.

Total:

2:
errors
inside:
one:
codeword.

Expected:

SECDED:
detects:
but:
cannot:
correct.

D.
LOCAL3.

Use:
input compartment:
0.

Inside:
its:
unmapped:
sibling:
code block:

flip:
logical:
data offsets:

0,
1,
2.

Total:

3:
errors
inside:
one:
codeword.

Expected:

outside:
guaranteed:
SECDED:
correction:
radius.

May:
miscorrect.

IMPORTANT FAIRNESS DETAIL

The:
same:
logical:
worker:
bits

are:
damaged
for:

UNCODED64_PAD64
and:
SECDED64_LOCAL.

For:
SECDED:

the:
corresponding:
physical:
data:
positions
are:
flipped.

Parity:
bits
are:
not:
directly:
damaged
in:
this:
experiment.

Therefore:

the:
test
asks:

does:
redundancy
allow:
reconstruction
of:
the:
same:
destroyed:
logical:
information?

COUNTERFACTUAL METRICS

Immediately:
after:
the:
first:
post-damage:
local:
decode

but:
before:
input:
1024:

POST_DECODE_LOGICAL_DIVERGENCE.

Hamming:
logical:
data
between:
DAMAGED
and:
REFERENCE

/
64.

POST_DECODE_PHYSICAL_DIVERGENCE.

Hamming:
physical:
state
/
128.

Then:

after:
post-damage:
external:
horizons:

1,
4,
8,
16,
32:

LOGICAL_DIVERGENCE.

PHYSICAL_DIVERGENCE.

FULL_LOGICAL_RECOVERY.

FULL_PHYSICAL_RECOVERY.

EXCESS_LOGICAL_DIVERGENCE_AREA

sum:
logical:
divergence
over:
32:
future:
steps.

EXCESS_PHYSICAL_DIVERGENCE_AREA.

RECOVERY TIME

first:
post-damage:
step

where:
logical:
state
matches:
reference

and:
remains:
matched
through:
step:
32.

DECODER TELEMETRY

For:
SECDED64_LOCAL:

report:

- blocks:
  with:
  no:
  syndrome;

- single:
  corrections;

- overall-parity:
  corrections;

- detected:
  double:
  errors;

- decoder:
  correction:
  actions;

- correction actions
  that:
  reduce:
  logical:
  counterfactual:
  divergence;

- correction actions
  that:
  increase:
  logical:
  counterfactual:
  divergence.

The:
last:
two:
are:
evaluation:
telemetry only.

They are:
NOT:
available:
to:
the:
decoder.

NO-DAMAGE CONTROL

Two:
identical:
undamaged:
clones

must:
remain:
exactly:
identical

for:
all:
32:
future:
steps.

Maximum:
logical:
and:
physical:
divergence:

0.

Otherwise:

DG-1R-06:

MECHANICALLY INVALID.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926060000
through:
20260926060007.

No:
prior:
DG-1R:
seed reuse.

SUMMARY

Per:
method
x:
damage family

aggregate:

8:
worlds.

Report:

median,
P10,
P90

as:
appropriate

for:

- post-decode:
  logical divergence;

- post-decode:
  physical divergence;

- logical divergence:
  h1,
  h4,
  h8,
  h16,
  h32;

- physical divergence:
  h1,
  h4,
  h8,
  h16,
  h32;

- full logical recovery rate;

- full physical recovery rate;

- logical divergence area;

- physical divergence area;

- recovery time.

SPARSE RECONSTRUCTION SIGNAL

TRUE
if:

SECDED64_LOCAL

for:
both:

SPREAD4
and:
SPREAD8

has:

1.
median:
POST_DECODE_LOGICAL_DIVERGENCE
=
0;

2.
full:
logical:
recovery rate
at:
h1
>=0.95;

3.
full:
logical:
recovery rate
at:
h32
>=0.95;

4.
median:
logical:
divergence area
<=10%:
of:
UNCODED64_PAD64
for:
the:
same:
damage family.

LOCAL CODE-DISTANCE LIMIT

CONFIRMED
if:

SPARSE_RECONSTRUCTION_SIGNAL
is:
TRUE

AND:

SECDED64_LOCAL

does NOT:
achieve:

>=0.95:
h1:
full:
logical:
recovery

for:
LOCAL2
or:
LOCAL3.

Interpretation:

redundancy:
works,

but:
repair:
radius
is:
bounded
by:
local:
code:
distance.

REDUNDANCY RECONSTRUCTION SIGNAL

TRUE
if:

SPARSE_RECONSTRUCTION_SIGNAL
is:
TRUE.

This is:
the:
primary:
DG-1R-06:
positive:
mechanistic:
signal.

IMPORTANT

A:
positive:
SPREAD4 /
SPREAD8:
result

does NOT:
prove:
general:
self-repair.

It demonstrates:

destroyed:
logical:
state
can:
be:
reconstructed
locally

when:

the:
organism
has:
paid:
for:
enough:
redundant:
information

and:

the:
damage:
geometry
lies:
inside:
the:
local:
code's:
correction:
radius.

A:
negative:
LOCAL2 /
LOCAL3:
result

is:
not:
a:
failure
of:
redundancy.

It:
measures:
the:
capacity:
boundary.

RESOURCE ACCOUNTING

UNCODED64_PAD64:

128:
physical bits.

64:
logical:
dynamic:
bits.

64:
padding:
bits.

Information-density:
telemetry:

0.50:
logical bits
per:
physical bit.

SECDED64_LOCAL:

128:
physical bits.

64:
logical:
dynamic:
bits.

64:
redundancy:
bits.

Same:

0.50:
logical bits
per:
physical bit.

Thus:

both:
methods

have:
the:
same:
logical:
capacity

and:
the:
same:
physical:
state:
budget.

Difference:

the:
second:
64 bits

are:

INERT
versus:

STRUCTURED:
REDUNDANCY.

This is:
the:
core:
paired:
mechanistic:
comparison.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-06:
primary:
damage scenario,

do not alter:

- 64-bit:
  logical:
  ring;

- 128-bit:
  physical:
  budget;

- code:
  equations;

- decoder:
  cases;

- input:
  mapping;

- damage:
  families;

- damage:
  positions;

- worker:
  clock;

- worker:
  rules;

- metrics;

- thresholds;

- world family.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical:
sweeps.

Canonical:
SHA-256
must:
match exactly.

Runtime:
sidecar:
non-canonical.

NEXT

If:
REDUNDANCY_RECONSTRUCTION_SIGNAL:

combine:

DG-1R-05:
H6:
damage:
containment

with:

DG-1R-06:
reconstructable:
redundancy

in:
a:
new:
fixed-budget:
architecture.

Goal:

contain:
damage:
large enough
to:
prevent:
spread

while:

distributed:
redundancy
reconstructs:
the:
lost:
state.

If:
LOCAL CODE-DISTANCE LIMIT
is:
confirmed:

the:
next:
question
becomes:

how:
to:
make:
redundancy
OVERLAP:
across:
neighboring:
maintenance:
territories

so:

a:
multi-bit:
local:
lesion

can:
be:
reconstructed
from:
information
outside:
the:
damaged:
territory.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The:
last:
experiment
showed:

the:
nanites
can:
stop:
damage
from:
spreading,

but:
they:
do not:
know:
what:
information
was:
destroyed.

This:
experiment
gives:
the:
organism

a:
small:
error-correcting:
structure

inside:
the:
same:
128 bits.

We are:
not:
adding:
memory.

We are:
taking:
bits
that:
already:
exist

and:
using:
half
of:
them
as:
redundant:
local:
information.

Then:

if:
a:
worker:
bit
is:
destroyed,

a:
local:
decoder
may:
be:
able:
to:
figure out
what:
it:
used:
to:
be.

The:
critical:
test
is:
damage
spread
across:
different:
local:
blocks.

If:
one:
bit
is:
lost
in:
many:
different:
blocks,

each:
block
should:
have:
enough:
local:
redundancy
to:
repair:
itself.

If:
several:
bits
inside:
one:
small:
block
are:
destroyed,

the:
code
should:
eventually:
hit:
its:
limit.

That:
would:
tell:
us
something:
very:
useful:

self-healing
needs:
both:

NANITES:
to:
contain:
damage

and:

REDUNDANCY:
to:
know:
what:
to:
rebuild.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-06 REDUNDANT LOCAL RECONSTRUCTION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-06 PRIMARY DAMAGE SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_06_redundant_local_reconstruction_v1.py

Harness commit:

d64f06713c9de823152355c12bed12ed710da4f7.

Git blob SHA:

c979c2650d1fd05cc0ee05b7c6cdf109c7b402f0.

Source SHA-256:

d60a5bc665f69ba708858e4a16a49256b13ecf77c6ff3afac8b36ceaa5c897b0.

Source bytes:

18629.

PRE-FREEZE SANITY

Exact:
local /
remote:
Git blob identity:

PASS.

Python compile:

PASS.

Direct:
SECDED:
single-data-bit:
correction:

PASS.

Direct:
same-block:
two-data-bit:
detection:

PASS.

Non-primary:
out-of-family:
trajectory:
sanity:

PASS.

No-damage:
logical divergence:

0.

No-damage:
physical divergence:

0.

Damage:
logical positions
exclude:
mapped:
input:
positions:

PASS.

No:
primary:
DG-1R-06:
world
or:
damage scenario
was:
executed
before:
this freeze.

FROZEN METHODS

UNCODED64_PAD64.

SECDED64_LOCAL.

Both:

128:
physical:
persistent bits.

Both:

64:
logical:
dynamic:
worker bits.

UNCODED:

64:
padding bits.

SECDED:

64:
structured:
redundancy bits.

FROZEN WORLD FAMILY

20260926060000..20260926060007.

8 worlds.

FROZEN DAMAGE FAMILIES

SPREAD4.

SPREAD8.

LOCAL2.

LOCAL3.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical:
sweeps.

Canonical output SHA-256
must:
match exactly.

Runtime sidecars:
are:
non-canonical.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-06 NON-EVIDENCE PILOT CLOSURE — REDUNDANT LOCAL ENCODING / COUNTERFACTUAL RECONSTRUCTION

DATE:
2026-09-20.

STATUS:
COMPLETE /
POSITIVE REDUNDANCY-RECONSTRUCTION SIGNAL /
LOCAL CODE-DISTANCE LIMIT CONFIRMED /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

d60a5bc665f69ba708858e4a16a49256b13ecf77c6ff3afac8b36ceaa5c897b0.

CANONICAL OUTPUT

RUN 1 SHA-256:

6ac7d0d13a798460ff9545bb129fca2a86440dacab0e2f73d16652e77732ab3e.

RUN 2 SHA-256:

6ac7d0d13a798460ff9545bb129fca2a86440dacab0e2f73d16652e77732ab3e.

Byte-identical:

PASS.

MECHANICAL VALIDITY

TRUE.

No-damage:

logical divergence:

0.

physical divergence:

0.

SPARSE_RECONSTRUCTION_SIGNAL

TRUE.

REDUNDANCY_RECONSTRUCTION_SIGNAL

TRUE.

LOCAL_CODE_DISTANCE_LIMIT_CONFIRMED

TRUE.

SPREAD4 — EXACT LOCAL RECONSTRUCTION

Damage:

4:
logical:
worker:
bits.

Geometry:

one:
damaged:
data bit
inside:
each:
of:
four:
different:
SECDED:
code blocks.

UNCODED64_PAD64:

post-decode:
logical divergence:

0.0625.

Median:
32-step:
logical divergence area:

7.5625.

SECDED64_LOCAL:

post-decode:
logical divergence:

0.

h1:
full logical recovery rate:

1.0.

h32:
full logical recovery rate:

1.0.

Median:
32-step:
logical divergence area:

0.

Reduction versus:
uncoded:

100%.

Median:
single corrections:

4.

Median:
decoder actions
toward:
the:
counterfactual:
reference:

4.

Median:
decoder actions
away:

0.

Thus:

all:
four:
destroyed:
logical:
bits

are:
reconstructed:

BEFORE:
THE:
NEXT:
EXTERNAL:
INPUT.

The:
damaged:
organism

then:
follows:

the:
exact:
undamaged:
logical:
trajectory.

SPREAD8 — SCALING ACROSS LOCAL TERRITORIES

Damage:

8:
logical:
worker:
bits.

Geometry:

one:
damaged:
data bit

inside:
each:
of:
eight:
different:
SECDED:
code blocks.

UNCODED64_PAD64:

post-decode:
logical divergence:

0.125.

Median:
logical divergence area:

10.7734375.

SECDED64_LOCAL:

post-decode:
logical divergence:

0.

h1:
full logical recovery rate:

1.0.

h32:
full logical recovery rate:

1.0.

Median:
logical divergence area:

0.

Reduction:

100%.

Median:
single corrections:

8.

Median:
decoder actions
toward:
reference:

8.

Median:
decoder actions
away:

0.

Interpretation:

damage:
amount
can:
increase

without:
breaking:
repair

when:

the:
errors
remain:

DISTRIBUTED
inside:
independently:
correctable:
local:
territories.

LOCAL2 — DETECTION WITHOUT RECONSTRUCTION

Damage:

2:
logical:
data bits

inside:
one:
SECDED:
codeword.

SECDED:

median:
detected:
double errors:

1.

Post-decode:
logical divergence:

0.03125.

h1:
full logical recovery rate:

0.

Median:
logical divergence area:

2.0546875.

Uncoded:

same:

2.0546875.

Thus:

the:
decoder
correctly:
detects:

THIS:
BLOCK:
IS:
DAMAGED

but:

does NOT:
contain:
enough:
redundant:
information

to:
reconstruct:
both:
destroyed:
data:
bits.

At:
h32:

full logical:
match rate:

0.25.

This:
late:
reconvergence

is:
natural:
dynamical:
coalescence
in:
some:
worlds,

not:
SECDED:
reconstruction,

because:

post-decode:
and:
trajectory-area:
metrics

show:
no:
coded:
advantage.

LOCAL3 — OUTSIDE THE CODE RADIUS

Damage:

3:
logical:
data bits

inside:
one:
codeword.

SECDED:

post-decode:
logical divergence:

0.046875.

h1:
full logical recovery:

0.

h32:
full logical recovery:

0.

Median:
logical divergence area:

2.1875.

Uncoded:

2.1875.

No:
reconstruction:
advantage.

The:
frozen:
triple-error:
pattern

falls:
outside:
the:
extended-Hamming:
correction:
radius.

TECHNICAL INTERPRETATION

DG-1R-05
and:
DG-1R-06

now:
separate:
the:
self-healing:
problem
into:
two:
mechanisms.

DG-1R-05:

H6:
local:
controller:
state

provides:

DAMAGE:
CONTAINMENT.

It:
reduces:
spread

but:
cannot:
infer:
destroyed:
information.

DG-1R-06:

structured:
redundancy

provides:

LOST-STATE:
RECONSTRUCTION

when:
damage
is:
inside:
the:
local:
code:
radius.

Therefore:

a:
credible:
Yggdrasil:
repair:
architecture

likely:
needs:

1.
CONTAINMENT.

Prevent:
corruption
from:
propagating.

2.
REDUNDANCY.

Preserve:
independent:
information
about:
the:
healthy:
state.

3.
LOCAL DECODING.

Use:
that:
redundancy
to:
reconstruct:
damaged:
state.

4.
OVERLAPPING:
REPAIR:
DOMAINS.

Avoid:
having:
one:
large:
local:
lesion
destroy:
all:
redundancy
needed
to:
repair:
that:
same:
territory.

RESOURCE RESULT

The:
paired:
comparison
is:
strict.

Both:

UNCODED64_PAD64

and:

SECDED64_LOCAL

have:

128:
physical:
persistent:
bits.

Both:

have:

64:
logical:
dynamic:
worker:
bits.

The:
difference
is:

UNCODED:

64:
otherwise:
unused:
physical:
bits.

SECDED:

the:
same:
64:
physical:
bits
carry:
structured:
redundancy.

Therefore:

the:
SPREAD4 /
SPREAD8:
repair:
gain

is:
not:
caused
by:

more:
persistent:
state

or:

more:
logical:
capacity.

It:
is:
caused
by:

HOW:
THE:
EXISTING:
STATE:
IS:
ORGANIZED.

ARCHITECTURAL INFLECTION

The:
current:
best:
repair:
picture
is:

H6:
CONTROLLER /
FIREBREAK

plus:

DISTRIBUTED:
REDUNDANT:
STATE

plus:

LOCAL:
DECODER.

But:

simple:
non-overlapping:
SECDED:
territories

fail:

when:
multiple:
important:
bits

inside:
the:
same:
territory

are:
destroyed.

NEXT JUSTIFIED EXPERIMENT

DG-1R-07 —
OVERLAPPING REDUNDANCY /
CONTAINMENT FUSION AUDIT.

Goal:

retain:

the:
same:
128-bit:
physical:
budget

while:

combining:

- H6-style:
  damage:
  containment;

- redundant:
  state:
  encoding;

- overlapping:
  parity /
  reconstruction:
  neighborhoods.

Primary question:

can:
redundancy
stored:
OUTSIDE:
a:
damaged:
local:
territory

reconstruct:

LOCAL2 /
LOCAL3:

concentrated:
lesions

that:
defeated:
the:
non-overlapping:
SECDED:
code?

The:
next:
design
should:
not:
simply:
increase:
code:
size.

It:
should:

SPREAD:
REPAIR:
INFORMATION

across:
neighboring:
territories

so:

a:
lesion
cannot:
destroy:

both:

the:
state

and:

all:
information
needed
to:
reconstruct:
that:
state.

PLAIN-SPEAK SUMMARY

This:
worked.

Not:
for:
every:
kind:
of:
damage,

but:
for:
exactly:
the:
reason
we:
wanted:
to:
test.

We:
kept:
the:
organism
at:

128:
total:
bits.

Both:
systems
had:

64:
real:
working:
bits.

The:
control:
wasted:
the:
other:
64.

The:
new:
organism
used:
those:
same:
64:
bits

to:
store:
local:
error-correcting:
information.

Then:
we:
destroyed:
bits.

When:
the:
damage
was:
spread out:

one:
lost:
bit
in:
each:
local:
territory,

the:
organism
reconstructed:

ALL:
OF:
THEM

before:
the:
next:
input
arrived.

Four:
lost:
bits:

100%:
recovery.

Eight:
lost:
bits:

100%:
recovery.

After:
repair,

the:
organism
followed:

the:
exact:
same:
future:
trajectory

as:
the:
copy
that:
was:
never:
damaged.

That:
is:
the:
first:
clean:
counterfactual:
regeneration
signal
in:
this:
line.

But:

when:
two:
or:
three:
important:
bits

inside:
one:
small:
repair:
territory

were:
destroyed,

the:
local:
code
ran:
out:
of:
information.

That:
gives:
us:
the:
next:
problem.

The:
repair:
information
cannot:
live:
only:
inside:
the:
same:
small:
region
it:
is:
supposed:
to:
repair.

We:
need:
overlapping:
redundancy:

some:
information
about:
this:
region
stored:
over:
there,

and:
vice:
versa.

So:
the:
current:
self-healing:
recipe
is:

nanites:
STOP:
THE:
DAMAGE.

redundancy:
REMEMBERS:
WHAT:
WAS:
THERE.

local:
decoders:
REBUILD:
IT.

The:
next:
step
is:
making:
that:
redundancy
survive:
larger:
local:
injuries.

canonical_scientific_execution = false.
stab18_r1_touched = false.
