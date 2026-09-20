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
