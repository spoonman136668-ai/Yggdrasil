TITLE: DG-1R-03 — Bounded Multi-Timescale Cellular Memory Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ReCA MULTI-TIMESCALE PILOT
TRACK: DG-1R / SOFTWARE CELLS / TEMPORAL MEMORY SUBSTRATE
BRANCH: dg1a-ar
PARENT: DG-1R-02

PURPOSE

DG-1R-01 showed:
single-timescale cellular reservoirs
did not retain useful D16 / D32 memory.

DG-1R-02 showed:
literature-style overwrite recurrence
greatly improves immediate input capture
but still does not restore long memory.

The remaining leading hypothesis is:

THE CELLULAR STATE
IS EVOLVING
TOO MUCH
PER UNIT
OF REMEMBERED TIME.

DG-1R-03 asks:

CAN:
THE SAME:
128-CELL:
PERSISTENT:
STATE BUDGET

RETAIN:
OLDER:
INPUT INFORMATION

IF:

DIFFERENT:
SUBPOPULATIONS

EVOLVE:
AT:
DIFFERENT:
INTERNAL:
CLOCK RATES?

BOUNDARY

Synthetic software-only pilot.

No:
living tissue.
No:
wetware.
No:
production modification.
No:
canonical H191 execution.
No:
STAB-18-R1 execution.

FIXED TOTAL STATE BUDGET

Every ReCA method uses:

128:
persistent:
binary:
cells.

No method:
receives:
more:
persistent:
cell state.

External input:

u_t ~ Bernoulli(0.5).

Input recurrence:

literature-style:
OVERWRITE.

At:
each:
external:
step:

all:
mapped positions

are:
set:
directly
to:
u_t.

MAPPING

8:
fixed:
mapped positions.

The:
128-cell:
global index space

is:
partitioned
into:
8:
contiguous:
16-cell:
mapping compartments.

At:
world initialization:

choose:
one:
fixed:
mapped position
uniformly
inside:
each:
16-cell:
compartment.

The:
same:
8 mapped positions
are:
used:
for:
all:
ReCA methods
inside:
that world.

GLOBAL MICROTICKS

Each:
external:
input step

contains:

4:
microticks.

At:
each:
microtick:

some:
cellular lanes
evolve
one:
CA update

while:
slower:
lanes
hold:
their:
state.

After:
each:
microtick:

record:
the:
entire:
128-cell:
composite state.

Thus:

every:
ReCA method
produces:

4 * 128
=
512:
binary:
readout features
per:
external:
time step.

Slower lanes:

do NOT:
gain:
more:
feature dimension.

Held:
states
are:
simply:
repeated:
during:
microticks
where:
that lane
does not:
evolve.

CLOCKS

FAST4:

update:
microticks:
1,
2,
3,
4.

MEDIUM2:

update:
microticks:
2,
4.

SLOW1:

update:
microtick:
4
only.

Therefore:

per:
external:
input

FAST4:
4:
CA transitions.

MEDIUM2:
2:
CA transitions.

SLOW1:
1:
CA transition.

METHODS

1.
FAST128_MIXED4

128:
cells.

One:
ring.

All:
cells:
mixed-rule:
population
from:

90,
150,
110,
22,
30.

Clock:

FAST4.

Purpose:

single-timescale:
reference
matching:
the:
DG-1R-02:
overwrite:
mixed-rule:
architecture.

2.
SLOW128_MIXED1

128:
cells.

One:
ring.

Same:
world-specific:
mixed-rule:
assignment
as:
FAST128_MIXED4.

Clock:

SLOW1.

Purpose:

isolate:
whether:
simply:
reducing:
state evolution
preserves:
longer:
memory.

3.
DUAL64_64_MIXED41

Lane A:

64:
cells,
MIXED5,
FAST4.

Lane B:

64:
cells,
MIXED5,
SLOW1.

Each lane:

periodic:
within:
itself.

Total:

128:
cells.

Purpose:

test:
simultaneous:
fast transformation
plus:
slow retention.

4.
TRI64_32_32_MIXED421

FAST4:
64 cells.

MEDIUM2:
32 cells.

SLOW1:
32 cells.

All lanes:

MIXED5.

Total:

128 cells.

Purpose:

fast-heavy:
three-timescale:
control.

5.
TRI32_32_64_MIXED421

FAST4:
32 cells.

MEDIUM2:
32 cells.

SLOW1:
64 cells.

All lanes:

MIXED5.

Total:

128 cells.

Purpose:

slow-heavy:
three-timescale:
control.

6.
SPEC32_32_64_90M182

FAST4:
32 cells:
Rule 90.

MEDIUM2:
32 cells:
MIXED5.

SLOW1:
64 cells:
Rule 182.

Total:

128 cells.

Reason:

DG-1R-01 / 02 mechanically suggested:

Rule 90:
useful:
nonlinear:
XOR structure.

Rule 182:
robust:
immediate:
overwrite input capture.

MIXED5:
useful:
short-memory:
heterogeneous:
behavior.

This method tests:
ROLE SPECIALIZATION

without:
increasing:
persistent:
cell count.

LANE BOUNDARIES

DUAL64_64:

[0,64)
[64,128).

TRI methods:

for:
64/32/32:

[0,64)
[64,96)
[96,128).

for:
32/32/64:

[0,32)
[32,64)
[64,128).

Each lane:

uses:
periodic:
boundary
inside:
its:
own:
lane.

No:
cross-lane:
cellular:
neighbor:
edges.

The readout:

can:
combine:
all:
lane states.

MIXED RULE ASSIGNMENT

At:
world initialization:

create:
one:
world-specific:
128-cell:
MIXED5:
rule assignment

using:
approximately:
equal:
counts
of:

90,
150,
110,
22,
30.

FAST128
and:
SLOW128
use:
this:
same:
full assignment.

Partitioned:
MIXED5:
methods
use:
the:
corresponding:
slices
of:
the:
same:
assignment.

This avoids:
method-specific:
random rule populations.

BASELINES

RAW32.

RANDOM512.

Exact:
DG-1R-01:
definitions.

SEQUENCE

Per world:

4096:
iid:
binary:
input steps.

Warmup:

64.

Train:

64..2111
inclusive.

2048 rows.

Gap:

448:
unused:
steps.

Test:

2560..3583
inclusive.

1024 rows.

TASKS

Exact:
DG-1R-01 /
DG-1R-02:
task family.

D1.
D4.
D8.
D16.
D32.
XOR3_11.
PARITY5.
MOTIF2_12.

READOUT

Linear:
ridge.

Alpha:

1e-3.

Bias:

included,
unregularized.

Threshold:

0.5.

MOTIF2_12:

balanced accuracy.

All other tasks:

accuracy.

DYNAMIC METRICS

Exact:
DG-1R-01:
definitions.

- binary feature entropy;
- numerical feature rank;
- Fisher separation:
  PARITY5;
  MOTIF2_12.

PERTURBATION

After:
external step:
512:

clone:
the:
persistent:
128-cell:
state.

Flip:
global:
cell:
112

in:
one:
clone.

Reason:

cell 112
lies:
in:
the:
slow lane

for:
all:
partitioned:
multi-timescale:
methods.

For:
single-ring:
methods

it remains:
a:
valid:
fixed:
perturbation location.

Continue:

identical:
future:
input

and:
the:
method's:
frozen:
clock schedule.

Measure:
persistent-state:
normalized Hamming
after:
external:
horizons:

1,
4,
8,
16.

RESOURCE ACCOUNTING

Persistent state:

128 bits
for:
every:
ReCA method.

Readout feature:

512 bits
for:
every:
ReCA method.

Nominal:
cell updates
per:
external:
input:

FAST128_MIXED4:

512.

SLOW128_MIXED1:

128.

DUAL64_64_MIXED41:

64*4
+
64*1
=
320.

TRI64_32_32_MIXED421:

64*4
+
32*2
+
32*1
=
352.

TRI32_32_64_MIXED421:

32*4
+
32*2
+
64*1
=
256.

SPEC32_32_64_90M182:

256:
cell updates.

Mapped overwrite writes:

8:
per:
external:
input
for:
all:
ReCA methods.

Reservoir trainable parameters:

0.

Readout scalars:

513:
per task.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926030000
through:
20260926030007.

No:
DG-1R-01 /
DG-1R-02:
seed reuse.

PRIMARY METRICS

For:
each:
method:

median
and:
P10
across:
worlds:

- D1;
- D4;
- D8;
- D16;
- D32;
- XOR3_11;
- PARITY5;
- MOTIF2_12;
- memory score:
  mean:
  D8,
  D16,
  D32;
- nonlinear score:
  mean:
  XOR3_11,
  PARITY5,
  MOTIF2_12;
- entropy;
- feature rank;
- perturbation:
  h1,
  h4,
  h8,
  h16.

FROZEN ABSOLUTE CLASSIFICATION

MEMORY_CAPABLE:

median:
memory score
>=0.70

AND:

median:
D16
>=0.70.

NONLINEAR_CAPABLE:

median:
nonlinear score
>=0.60

AND:

at least:
two:
nonlinear tasks
have:
median:
metric
>=0.60.

DYNAMICALLY_BALANCED:

median:
state entropy
in:
[0.20,0.95]

AND:

median:
h16:
perturbation Hamming
in:
[0.01,0.75].

TEMPORAL_SUBSTRATE_CANDIDATE:

all:
three:
true.

FROZEN RELATIVE CLASSIFICATION

Reference:

FAST128_MIXED4.

For:
each:
non-reference:
ReCA method

report:

paired:
method - FAST128_MIXED4

for:

D1,
D4,
D8,
D16,
D32,
memory score,
nonlinear score.

SLOWING_SIGNAL

TRUE
if:

SLOW128_MIXED1

improves:

median:
D16
by:
>=0.10

OR:

median:
D32
by:
>=0.10

relative:
to:
FAST128_MIXED4.

MULTITIMESCALE_SIGNAL

TRUE
if:

at least:
one:
DUAL /
TRI /
SPEC:
method

improves:

median:
D16
by:
>=0.10

OR:

median:
D32
by:
>=0.10

relative:
to:
FAST128_MIXED4

AND:

its:
median:
nonlinear score

is:
no more than:
0.05
below:
FAST128_MIXED4.

STRONG_MULTITIMESCALE_RECOVERY

TRUE
if:

at least:
one:
DUAL /
TRI /
SPEC:
method

is:
MEMORY_CAPABLE

while:

FAST128_MIXED4
is:
not.

SPECIALIZATION_SIGNAL

TRUE
if:

SPEC32_32_64_90M182

exceeds:

TRI32_32_64_MIXED421

by:
>=0.05
on:

median:
memory score

OR:

median:
nonlinear score

without:
degrading:
the:
other:
score
by:
more than:
0.05.

IMPORTANT

If:
SLOW128 improves
but:
partitioned methods
do not:

the:
main mechanism
is:
slower:
global:
evolution,
not:
division of labor.

If:
partitioned methods
improve
beyond:
SLOW128:

timescale:
coexistence
adds:
value.

If:
SPEC improves
beyond:
mixed-rule:
partitioning:

role-specific:
rule specialization
adds:
value.

If:
all remain:
near:
chance
at:
D16 /
D32:

the:
memory problem
requires:

a:
stronger:
retention:
mechanism

than:
passive:
clock separation.

That result
would:
directly motivate:

DG-1R-04:
local:
stabilizer /
"software nanite":
memory protection.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-03:
world,

do not alter:

- total cell budget;
- lane sizes;
- lane boundaries;
- clock schedules;
- mapping positions;
- overwrite recurrence;
- rule assignments;
- specialized rules;
- feature extraction;
- tasks;
- readout;
- perturbation protocol;
- thresholds;
- world family.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical:
SHA-256
must:
match exactly.

Runtime:
sidecar:
non-canonical.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We think:
the:
cells
may be:
changing:
too much:
too quickly
to:
remember.

This test:
does NOT:
give:
the system
more cells.

It gives:
different:
parts
of:
the same:
128-cell:
organism
different:
speeds.

Some:
cells
change:
four times
per:
input.

Some:
twice.

Some:
once.

If:
the:
slow:
cells
hold:
older:
information

while:
the:
fast:
cells
still:
mix:
new:
information,

then:

D16 /
D32:
memory
should:
improve

without:
adding:
permanent:
state.

If:
that:
still:
does not work,

the next:
clean:
hypothesis
is:
active:
local:
stabilization

rather than:
passive:
slowing.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-03 BOUNDED MULTI-TIMESCALE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-03 PRIMARY WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_03_multitimescale_v1.py

Harness commit:

b9b13fe30c75800e83574f9d930d71da48df49e6.

Git blob SHA:

7b5d6995450195f10d7ae2c474cf6936093dcf96.

Source SHA-256:

f75e7089f1ff3ac8bd55d9126c2cb7950f08feb775a1ce8e5571269eee4fefb9.

Source bytes:

17130.

PRE-FREEZE SANITY

Python compile:

PASS.

Feature surface:

all ReCA methods:
512 bits:
per external input.

Frozen cell-update counts:

FAST128_MIXED4:
512.

SLOW128_MIXED1:
128.

DUAL64_64_MIXED41:
320.

TRI64_32_32_MIXED421:
352.

TRI32_32_64_MIXED421:
256.

SPEC32_32_64_90M182:
256.

No:
primary:
DG-1R-03:
world
was:
executed
before:
this freeze.

FROZEN WORLD FAMILY

20260926030000..20260926030007.

8 worlds.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical output SHA-256
must:
match exactly.

Runtime sidecars:
are:
non-canonical.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-03 NON-EVIDENCE PILOT CLOSURE — BOUNDED MULTI-TIMESCALE CELLULAR MEMORY

DATE:
2026-09-20.

STATUS:
COMPLETE /
NEGATIVE LONG-MEMORY RECOVERY /
POSITIVE SHORT-TO-MEDIUM RETENTION EFFECT /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

f75e7089f1ff3ac8bd55d9126c2cb7950f08feb775a1ce8e5571269eee4fefb9.

CANONICAL OUTPUT

RUN 1 SHA-256:

7d9c0f5265f3b963fcb61c133002b1c156167e1e6100a95210fd8b5cdc7f5391.

RUN 2 SHA-256:

7d9c0f5265f3b963fcb61c133002b1c156167e1e6100a95210fd8b5cdc7f5391.

Byte-identical:

PASS.

PRIMARY CLASSIFICATION

SLOWING_SIGNAL:

FALSE
under:
the:
frozen:
>=0.10:
D16/D32:
gain gate.

MULTITIMESCALE_SIGNAL:

FALSE.

STRONG_MULTITIMESCALE_RECOVERY:

FALSE.

SPECIALIZATION_SIGNAL:

FALSE.

TEMPORAL_SUBSTRATE_CANDIDATES:

NONE.

FAST128_MIXED4 REFERENCE

Median:

D1:
0.83447265625.

D4:
0.55517578125.

D8:
0.4951171875.

D16:
0.4951171875.

D32:
0.49951171875.

Memory score:

0.5017903645833333.

SLOW128_MIXED1

Median:

D1:
0.98779296875.

D4:
0.69189453125.

D8:
0.56298828125.

D16:
0.50146484375.

D32:
0.50927734375.

Memory score:

0.52783203125.

Relative to:
FAST128:

D1:
+0.12109375.

D4:
+0.08935546875.

D8:
+0.06396484375.

D16:
-0.0029296875:
paired median.

D32:
+0.00732421875:
paired median.

Thus:

slowing:
the:
entire:
cellular state

materially:
improves:
recent:
retention

but:

does NOT:
recover:
long:
D16 /
D32:
identity.

PASSIVE MULTI-TIMESCALE LANES

DUAL64_64_MIXED41:

D8:
0.521484375.

D16:
0.5009765625.

D32:
0.50439453125.

TRI64_32_32_MIXED421:

D8:
0.51611328125.

D16:
0.50048828125.

D32:
0.49755859375.

TRI32_32_64_MIXED421:

D8:
0.52783203125.

D16:
0.50439453125.

D32:
0.5029296875.

None:

produce:
a:
material:
D16 /
D32:
recovery.

ROLE-SPECIALIZED METHOD

SPEC32_32_64_90M182:

D1:
1.0.

D4:
0.69873046875.

D8:
0.52294921875.

D16:
0.50927734375.

D32:
0.49072265625.

Nonlinear score:

0.547616281500878.

Its:

MOTIF2_12:
0.6163198762591717.

This is:
an:
interesting:
nonlinear:
task-specific:
signal,

but:

the:
method
does NOT:
recover:
long memory.

RESOURCE RESULT

The:
slow-heavy:
TRI32_32_64

uses:

256:
cell updates
per:
external:
input

versus:

512:
for:
FAST128.

SLOW128:

uses:
128:
updates.

Despite:
large:
compute reduction,

D16 /
D32:
remain:
near:
chance.

Therefore:

the:
failure
is NOT:
simply:
"too many:
cell updates"
in:
a:
linear:
sense.

Fewer:
updates
delay:
information loss,

but:
passive:
clock separation
does not:
create:
a:
stable:
long-term:
trace.

TECHNICAL INTERPRETATION

DG-1R-03 refines:
the:
timescale hypothesis.

The:
system
was:
indeed:
evolving:
too aggressively
for:
recent:
memory.

Evidence:

slowing:
improves:
D1,
D4,
and:
D8.

But:

simply:
running:
cells:
more slowly

does NOT:
protect:
specific:
older:
information
through:
D16 /
D32.

This implies:

passive:
timescale separation

is:
insufficient.

The:
remaining:
leading mechanism
is:

ACTIVE:
LOCAL:
STABILIZATION.

The:
system
needs:
a:
mechanism
that:
detects:
when:
local:
state evolution
is:
too destructive

and:
selectively:
suppresses /
damps:
that:
evolution,

rather than:
merely:
slowing:
every:
update
on:
a:
fixed:
clock.

NEXT JUSTIFIED EXPERIMENT

DG-1R-04 —
PROGRAMMED:
SOFTWARE-NANITE:
LOCAL STABILIZATION AUDIT.

Fixed:
total:
persistent:
state:

128:
bits.

Candidate architecture:

112:
ordinary:
worker cells.

16:
programmed:
stabilizer /
"nanite":
controller cells.

Each:
nanite
controls:
one:
local:
7-worker:
sector.

At:
a:
worker:
micro-update:

1.
compute:
the:
sector's:
proposed:
CA update;

2.
measure:
the:
local:
fraction:
of:
worker bits
that:
would:
change;

3.
if:
that:
local:
change
exceeds:
a:
frozen:
threshold,

the:
nanite:
vetoes:
that:
sector's:
CA transition

for:
that:
microtick;

4.
the:
post-input:
worker state
is:
preserved
instead.

The:
nanite
does NOT:

store:
the:
old:
input bit
in:
a:
hidden:
register.

It only:

locally:
regulates:
whether:
a:
destructive:
state transition
is:
allowed.

This directly tests:

ACTIVE:
STABILITY CONTROL

versus:

PASSIVE:
SLOWING.

PLAIN-SPEAK SUMMARY

What happened?

Slowing:
the:
cells down
helped.

They remembered:
recent:
information
better.

But:
it only:
pushed:
the:
forgetting point
back:
a:
little.

By:
16
or:
32:
inputs ago,

the:
old:
bit
was:
still:
basically:
gone.

So:

we were:
partly right.

The cells:
were:
changing:
too quickly.

But:
simply:
making:
them:
slower
is:
not enough.

What does that mean?

The:
system
probably:
needs:
something
that:
actively says:

"this:
local:
change
is:
too destructive;
do not:
let it:
happen."

That is:
exactly:
where:
the:
software-nanite:
idea
fits.

The:
next:
experiment
will:
give:
a:
small:
fraction:
of:
the:
same:
128-cell:
budget

a:
local:
stabilizer:
job.

They will:
not:
be:
extra:
memory.

They will:
act:
like:
tiny:
local:
shock absorbers
that:
can:
veto:
overly:
destructive:
cellular:
changes.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-03 NON-EVIDENCE PILOT CLOSURE — BOUNDED MULTI-TIMESCALE CELLULAR MEMORY

DATE:
2026-09-20.

STATUS:
COMPLETE /
NEGATIVE D16-D32 RECOVERY /
POSITIVE SHORT-MEMORY SLOWING SIGNAL BELOW FROZEN THRESHOLD /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

f75e7089f1ff3ac8bd55d9126c2cb7950f08feb775a1ce8e5571269eee4fefb9.

CANONICAL OUTPUT

RUN 1 SHA-256:

7d9c0f5265f3b963fcb61c133002b1c156167e1e6100a95210fd8b5cdc7f5391.

RUN 2 SHA-256:

7d9c0f5265f3b963fcb61c133002b1c156167e1e6100a95210fd8b5cdc7f5391.

Byte-identical:

PASS.

FROZEN SIGNALS

SLOWING_SIGNAL:

FALSE.

MULTITIMESCALE_SIGNAL:

FALSE.

STRONG_MULTITIMESCALE_RECOVERY:

FALSE.

SPECIALIZATION_SIGNAL:

FALSE.

TEMPORAL_SUBSTRATE_CANDIDATES:

NONE.

FAST128_MIXED4 REFERENCE

D1:

0.83447265625.

D4:

0.55517578125.

D8:

0.4951171875.

D16:

0.4951171875.

D32:

0.49951171875.

Memory score:

0.5017903645833333.

SLOW128_MIXED1

D1:

0.98779296875.

D4:

0.69189453125.

D8:

0.56298828125.

D16:

0.50146484375.

D32:

0.50927734375.

Memory score:

0.52783203125.

PAIRED SLOWING EFFECT

Relative to:
FAST128_MIXED4.

D1:

+0.12109375.

D4:

+0.08935546875.

D8:

+0.06396484375.

D16:

-0.0029296875.

D32:

+0.00732421875.

Memory score:

+0.02620442708333337.

Interpretation:

slower:
whole-reservoir:
evolution

substantially improves:

immediate
and:
short:
memory

but:

does NOT:
meaningfully:
extend:
the:
memory horizon
to:
D16 /
D32.

MULTI-TIMESCALE PARTITIONS

DUAL64_64_MIXED41:

D8:

0.521484375.

D16:

0.5009765625.

D32:

0.50439453125.

TRI64_32_32_MIXED421:

D8:

0.51611328125.

D16:

0.50048828125.

D32:

0.49755859375.

TRI32_32_64_MIXED421:

D8:

0.52783203125.

D16:

0.50439453125.

D32:

0.5029296875.

No:
partitioned:
clock architecture

produced:
the:
frozen:
>=0.10:
D16 /
D32:
gain.

ROLE SPECIALIZATION

SPEC32_32_64_90M182:

D1:

1.0.

D4:

0.69873046875.

D8:

0.52294921875.

D16:

0.50927734375.

D32:

0.49072265625.

Nonlinear score:

0.547616281500878.

MOTIF2_12:

0.6163198762591717.

This:
specialized:
architecture

creates:
a:
useful:
motif:
signal

and:
perfect:
median:
D1

but:

does NOT:
restore:
long memory.

SPECIALIZATION_SIGNAL:

FALSE
under:
the:
frozen:
joint:
criteria.

RESOURCE RESULT

The:
strongest:
passive:
slowing:
method

SLOW128_MIXED1

uses:

128:
cell updates
per:
external:
input

versus:

512
for:
FAST128_MIXED4.

Thus:

it:
improves:
D1 /
D4 /
D8

while:
using:
75% fewer:
cell updates.

This is:
a:
real:
efficiency:
signal.

However:

long:
memory
remains:
absent.

TECHNICAL INTERPRETATION

DG-1R-03 sharpens:
the:
memory-loss:
mechanism.

The:
reservoir
does:
benefit
from:
less:
evolution.

Therefore:

"too much evolution too fast"

was:
partly:
correct.

But:

simply:
slowing:
the:
entire:
state

or:
splitting:
the:
same:
128 cells
into:
passive:
fast /
medium /
slow:
lanes

is:
not:
enough
to:
preserve:
specific:
information
for:
16-32:
external steps.

The:
problem
is therefore:

NOT ONLY:
RATE.

It is also:

RETENTION:
CONTROL.

The:
system
needs:
a:
mechanism
that:
recognizes:
locally useful:
state

and:
actively:
protects,
refreshes,
or:
temporarily:
freezes:
that:
state

instead of:
letting:
every:
trace
decay
under:
the:
same:
passive:
clock policy.

NEXT JUSTIFIED EXPERIMENT

DG-1R-04 —
LOCAL STABILIZER /
"SOFTWARE NANITE":
MEMORY PROTECTION AUDIT.

Core question:

can:
a:
small:
fixed:
fraction
of:
the:
same:
128-cell:
budget

act as:
local:
maintenance /
stabilizer:
controllers

and:
extend:
D16 /
D32:
memory

without:
turning:
the:
system
into:
a:
conventional:
explicit:
history register?

Fairness requirement:

the:
nanite design
must NOT:
receive:
free:
task labels,
future:
targets,
or:
unbounded:
hidden:
memory.

The:
same:
128-bit:
persistent:
cell budget

must:
remain:
the:
primary:
state budget.

The:
nanites
may:
only:
alter:
local:
state-evolution behavior
through:
frozen:
programmed:
rules.

PLAIN-SPEAK SUMMARY

What did we try?

We kept:
the:
same:
128 cells

but:
made:
some:
cell groups
run:
fast
and:
others:
slow.

What happened?

Slowing:
the:
cells
really did:
help:
short-term:
memory.

The:
slow:
128-cell:
reservoir

remembered:
D4
and:
D8

better
than:
the:
fast:
one

while:
doing:
far:
less:
cellular:
work.

But:

D16
and:
D32
were:
still:
basically:
guessing.

What did we learn?

Yes:

the:
system
was:
evolving:
too:
fast.

But:

just:
telling:
some:
cells
to:
move:
more slowly

is:
not:
enough.

Something:
has to:
actively:
protect:
important:
state
from:
being:
mixed away.

That is:
exactly:
where:
the:
software-nanite:
idea
fits.

The:
next:
experiment
will:
test:
whether:
a:
small:
local:
maintenance:
population

can:
detect:
and:
stabilize:
fragile:
memory traces

without:
simply:
adding:
a:
hidden:
conventional:
memory buffer.

canonical_scientific_execution = false.
stab18_r1_touched = false.
