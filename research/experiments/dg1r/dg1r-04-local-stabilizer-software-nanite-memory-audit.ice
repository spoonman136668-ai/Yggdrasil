TITLE: DG-1R-04 — Local Stabilizer / Software-Nanite Memory Protection Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ACTIVE-STABILIZATION PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL HOMEOSTATIC MEMORY PROTECTION
BRANCH: dg1a-ar
PARENT: DG-1R-03

PURPOSE

DG-1R-03 established:

- slower evolution improves D1 / D4 / D8;
- passive slowing does NOT materially improve D16 / D32;
- splitting the same 128 cells into passive fast / medium / slow lanes
  also does NOT recover long memory.

Therefore:

RATE alone
is:
not enough.

DG-1R-04 tests:

ACTIVE:
LOCAL:
RETENTION CONTROL.

Question:

CAN:
A:
SMALL:
PROGRAMMED:
SOFTWARE-NANITE:
POPULATION

STABILIZE:
FRAGILE:
CELLULAR:
MEMORY TRACES

WITHOUT:

- adding:
  more:
  persistent:
  bits;
- receiving:
  task:
  labels;
- receiving:
  future:
  targets;
- becoming:
  a:
  hidden:
  conventional:
  history:
  register?

BOUNDARY

Synthetic software-only experiment.

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

TOTAL PERSISTENT STATE BUDGET

128:
binary:
cells
for:
every:
ReCA method.

Nanite methods:

112:
ordinary:
worker cells

plus:

16:
one-bit:
nanite:
controller cells.

Total:

128 bits.

No:
hidden:
controller state.

No:
timer:
state.

No:
external:
memory buffer.

ROLE METADATA

Nanite positions
and:
their:
fixed:
programs

are:
architecture metadata,
analogous to:
a:
fixed:
cell rule.

They are NOT:
dynamic:
memory.

NANITE POSITIONS

16:
fixed:
controller sites.

Indices:

7,
15,
23,
31,
...
127.

Thus:

the:
128-cell:
ring

is:
partitioned
into:

16:
8-cell:
local blocks.

Each block:

7:
worker cells

followed by:

1:
nanite cell.

INPUT MAPPING

8:
fixed:
mapped:
input positions.

The:
global:
128-cell:
index space

is:
partitioned
into:

8:
16-cell:
input compartments.

Inside:
each:
16-cell:
compartment,

choose:
one:
world-specific:
mapped:
WORKER:
position

uniformly
from:
the:
14:
positions

that:
are NOT:
potential:
nanite sites:

offsets:
7
or:
15.

The:
same:
8:
input positions

are used:
for:
all:
methods
inside:
one world.

INPUT RECURRENCE

Literature-style:

OVERWRITE.

At:
each:
external:
time step:

state[mapped]
=
u_t.

WORKER DYNAMICS

Ordinary:
worker cells

use:
the:
same:
world-specific:
MIXED5:
rule assignment
drawn from:

90,
150,
110,
22,
30.

Workers:

evolve:
once:
per:
external:
input

at:
microtick:
4.

Thus:

worker dynamics
match:
the:
SLOW128_MIXED1:
retention-friendly:
clock
from:
DG-1R-03.

There are:

4:
microticks
per:
external:
input.

All:
methods
record:
the:
full:
128-cell:
state
after:
each:
microtick.

Readout feature:

512 bits.

REFERENCE METHOD

SLOW128_MIXED1.

All:
128:
cells
behave:
as:
ordinary:
MIXED5:
workers.

One:
CA update
at:
microtick:
4.

Input mapping:

uses:
the:
same:
nanite-safe:
mapped positions

as:
nanite methods.

Purpose:

clean:
passive-slowing:
reference.

NANITE PROGRAM

Each:
nanite

owns:
the:
7:
worker cells
immediately:
before:
it
inside:
its:
8-cell:
block.

Nanite:
state

is:
one:
binary:
bit.

Nanites:

are:
NOT:
directly:
input-mapped.

Nanites:

do NOT:
receive:
task labels,
targets,
delay identities,
or:
readout gradients.

Their:
program
uses ONLY:

- their:
own:
one-bit:
state;
- the:
current:
7:
local:
worker bits;
- the:
worker:
candidate:
next-state
where:
the:
method
requires it.

NANITE UPDATE — HYSTERESIS

After:
worker evolution
at:
microtick 4,

count:

ones
among:
the:
7:
local:
workers.

H5:

if:
ones >=5:

nanite = 1.

if:
ones <=2:

nanite = 0.

otherwise:

nanite:
holds:
its:
previous:
bit.

H6:

if:
ones >=6:

nanite = 1.

if:
ones <=1:

nanite = 0.

otherwise:

nanite:
holds:
its:
previous:
bit.

Thus:

nanites:
change:
only
when:
a:
strong:
local:
consensus

overcomes:
their:
current:
one-bit:
inertia.

METHODS

1.
SLOW128_MIXED1

Passive:
128-worker:
reference.

2.
N16_H5

112:
MIXED5:
workers.

16:
H5:
nanites.

No:
explicit:
worker repair.

Nanites:
influence:
worker dynamics
only:
because:
their:
persistent:
bits

are:
local:
neighbors
inside:
the:
global:
ring.

3.
N16_H6

Same:

112 workers
+
16 nanites.

H6:
stronger:
hysteresis.

No:
explicit:
repair.

4.
N16_H6_DAMP

H6:
nanites.

Before:
the:
single:
worker:
evolution
at:
microtick 4:

for:
each:
8-cell:
block:

if:
at least:
5:
of:
the:
7:
current:
workers

match:
the:
nanite bit,

compute:
the:
ordinary:
candidate:
next state

for:
each:
worker.

If:
a:
worker
currently:
matches:
the:
nanite

and:
its:
candidate:
next state

would:
move:
away
from:
the:
nanite,

suppress:
that:
specific:
change.

Other:
candidate:
changes

remain:
unchanged.

Interpretation:

a:
coherent:
local:
trace

is:
actively:
protected
against:
erosion,

but:

the:
nanite
does NOT:
force:
currently:
different:
workers
to:
match it.

After:
worker evolution:

update:
nanite
using:
H6.

5.
N16_H6_REPAIR

H6:
nanites.

Workers:

first:
perform:
ordinary:
MIXED5:
evolution.

Then:

for:
each:
block,

after:
H6:
nanite:
update,

count:
workers
that:
disagree
with:
the:
nanite.

If:

disagreement
is:
4
or:
5:

write:

the:
block-center:
worker

index:

block_start + 3

to:

the:
nanite:
bit.

If:

disagreement <=3:

no repair.

If:

disagreement >=6:

no repair,

because:
the:
local:
state
has:
moved:
too far
for:
one-bit:
maintenance
to:
claim:
a:
stable:
trace.

Interpretation:

bounded:
one-cell:
local:
repair

only:
inside:
the:
ambiguous:
erosion:
regime.

No:
multi-cell:
clamping.

No:
task-aware:
repair.

INITIAL STATE

All:
128 bits:

0.

Same:
as:
prior:
ReCA pilots.

NANITE TELEMETRY

Per:
nanite method
and:
world:

report:

- nanite:
  bit-change:
  count;

- nanite:
  bit-change:
  rate
  per:
  external:
  step;

- DAMP:
  suppressed:
  worker:
  transitions;

- DAMP:
  suppression:
  rate
  per:
  worker:
  evolution;

- REPAIR:
  repair:
  writes;

- REPAIR:
  rate
  per:
  external:
  step;

- mean:
  nanite:
  one-bit:
  run length;

- median:
  nanite:
  one-bit:
  run length.

These:
metrics
are:
mechanistic:
telemetry.

They do NOT:
affect:
classification.

SEQUENCE

4096:
iid:
binary:
input steps.

Warmup:

64.

Train:

64..2111.

2048 rows.

Gap:

448.

Test:

2560..3583.

1024 rows.

TASKS

D1.
D4.
D8.
D16.
D32.
XOR3_11.
PARITY5.
MOTIF2_12.

Exact:
DG-1R-01..03:
definitions.

READOUT

Exact:
prior:
ReCA:
linear:
ridge:
readout.

Alpha:

1e-3.

Bias:

included,
unregularized.

Reservoir /
nanite programs:

never:
trained.

DYNAMIC METRICS

- binary feature entropy;
- numerical feature rank;
- Fisher separation:
  PARITY5;
  MOTIF2_12;
- perturbation Hamming:
  h1,
  h4,
  h8,
  h16.

PERTURBATION

After:
external:
step:
512:

clone:
the:
persistent:
128-bit:
state.

Flip:

worker:
cell:
112

in:
one:
clone.

Continue:

identical:
future:
input

under:
the:
method's:
frozen:
worker /
nanite:
program.

Measure:

normalized:
Hamming:
distance
after:

1,
4,
8,
16:
external:
steps.

RESOURCE ACCOUNTING

Persistent state:

128 bits
for:
all:
ReCA methods.

Readout feature:

512 bits.

SLOW128_MIXED1:

128:
worker:
cell updates
per:
external:
input.

Nanite methods:

112:
ordinary:
worker:
candidate updates

plus:

16:
fixed:
local:
controller:
evaluations

per:
external:
input.

DAMP:

may:
suppress:
candidate:
worker transitions.

REPAIR:

may:
perform:
at most:
16:
bounded:
one-cell:
repair writes

per:
external:
input.

No:
trainable:
reservoir:
parameters.

Readout:

513:
trainable:
scalars
per:
task.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926040000
through:
20260926040007.

No:
prior:
DG-1R:
seed reuse.

PRIMARY METRICS

For:
every:
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
- memory score;
- XOR3_11;
- PARITY5;
- MOTIF2_12;
- nonlinear score;
- state entropy;
- feature rank;
- h1 /
  h4 /
  h8 /
  h16:
  perturbation.

ABSOLUTE CLASSIFICATION

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
perturbation
in:
[0.01,0.75].

TEMPORAL_SUBSTRATE_CANDIDATE:

all:
three:
true.

NANITE LONG-MEMORY SIGNAL

TRUE
if:

at least:
one:
nanite:
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
SLOW128_MIXED1.

STRONG NANITE SIGNAL

TRUE
if:

at least:
one:
nanite:
method

has:

median:
D16
>=0.65

AND:

median:
D32
>=0.60

AND:

median:
nonlinear score

is:
no more than:
0.05
below:
SLOW128_MIXED1

AND:

median:
state entropy
>=0.20.

FULL NANITE RECOVERY

TRUE
if:

at least:
one:
nanite:
method

is:
TEMPORAL_SUBSTRATE_CANDIDATE

while:

SLOW128_MIXED1
is:
not.

OVERSTABILIZATION

Flag:
a:
nanite method

OVERSTABILIZED

if:

median:
state entropy
<0.20

OR:

median:
feature-rank fraction
<0.10.

Interpretation:

the:
maintenance:
program
has:
frozen:
too much:
of:
the:
reservoir's:
useful:
dynamic:
state.

IMPORTANT

Nanites:
are:
allowed:
to:
remember
one:
local:
bit

because:

that bit
is:
part:
of:
the:
same:
fixed:
128-bit:
persistent:
state budget.

They are NOT:
allowed:

- counters;
- hidden:
  timestamps;
- explicit:
  delay labels;
- copied:
  input-history arrays;
- task:
  information;
- held-out:
  information.

A:
positive:
result
therefore:
supports:

ROLE SPECIALIZATION /
LOCAL HOMEOSTASIS

not:

free:
external:
memory.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-04:
world,

do not alter:

- nanite count;
- nanite positions;
- mapping exclusions;
- worker clock;
- mixed-rule assignment;
- H5 threshold;
- H6 threshold;
- damping rule;
- repair rule;
- repair location;
- tasks;
- readout;
- perturbation protocol;
- classification gates;
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

NEXT

If:
FULL NANITE RECOVERY:

test:
developmental:
nanite:
birth /
death /
migration
under:
bounded:
resource pressure.

If:
STRONG NANITE SIGNAL
without:
full recovery:

test:
nanite:
density
and:
local:
protection:
radius

under:
fixed:
128-bit:
state.

If:
only:
D8 /
short:
memory
improves:

active:
stabilization
helps
but:
one-bit:
local:
controllers
are:
insufficient
for:
long:
memory.

If:
all:
nanite methods
are:
negative:

move:
ReCA:
away:
from:
raw:
delay-memory
and:
test:
whether:
cellular dynamics
are:
better:
used
for:

- nonlinear:
  preprocessing;
- anomaly:
  detection;
- local:
  repair;
- developmental:
  regulation;

while:
explicit:
compact:
state
handles:
long:
temporal:
memory.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We now know:
simply:
slowing:
the:
cells
does not:
keep:
a:
specific:
memory
alive
for:
long enough.

So:

we are:
putting:
16:
tiny:
maintenance:
cells
inside:
the:
same:
128-bit:
organism.

They:
do NOT:
know:
the:
answer.

They:
do NOT:
get:
extra:
memory.

They:
only:
watch:
seven:
nearby:
cells

and:
try:
to:
keep:
a:
coherent:
local:
pattern
from:
being:
accidentally:
mixed away.

One version:
just:
has:
local:
inertia.

One:
actively:
suppresses:
erosion.

One:
performs:
a:
single:
bounded:
repair
when:
a:
local:
pattern
looks:
partly:
damaged.

If:
D16 /
D32:
memory
comes back,

that:
would:
support:
your:
software-nanite:
idea:

some:
cells
compute,

while:
other:
cells
exist:
to:
protect:
the:
state
the:
computing:
cells
would:
otherwise:
destroy.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-04 SOFTWARE-NANITE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-04 PRIMARY WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_04_software_nanite_v1.py

Harness commit:

4fbc1defa505653ac638d0d21fdd5c8e37b6f025.

Git blob SHA:

6eeaf70c97174fd40483256db9c6e600989a6b47.

Source SHA-256:

debcaf7c79632740dbccd4ad8b0f6ebfcd034515cb144b9a21bc537f7a8f7eed.

Source bytes:

23776.

PRE-FREEZE SANITY

Python compile:

PASS.

Nanite-safe:
input mapping:

PASS.

A:
short:
non-primary:
10-step:
mechanical:
sanity

confirmed:

- no:
  input:
  mapping
  lands:
  on:
  nanite:
  sites;

- nanite:
  controller:
  state
  remains:
  inside:
  the:
  same:
  128-bit:
  organism;

- DAMP:
  can:
  suppress:
  worker:
  erosion
  without:
  hidden:
  state.

No:
primary:
DG-1R-04:
world
was:
executed
before:
this freeze.

FROZEN METHODS

SLOW128_MIXED1.

N16_H5.

N16_H6.

N16_H6_DAMP.

N16_H6_REPAIR.

All:
ReCA methods:

128:
persistent:
bits.

All:

512:
readout:
feature bits
per:
external:
input.

FROZEN WORLD FAMILY

20260926040000..20260926040007.

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


FINAL DG-1R-04 NON-EVIDENCE PILOT CLOSURE — SOFTWARE-NANITE MEMORY PROTECTION

DATE:
2026-09-20.

STATUS:
COMPLETE /
NEGATIVE RAW LONG-MEMORY RESULT /
POSITIVE STABILITY-REGULATION MECHANISTIC SIGNAL /
ONE OVERSTABILIZATION FAILURE /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

debcaf7c79632740dbccd4ad8b0f6ebfcd034515cb144b9a21bc537f7a8f7eed.

CANONICAL OUTPUT

RUN 1 SHA-256:

bc6c5be432f8a4d9b439df860ebe3aabfd69e81cfa084a9f8e2776aa0415461f.

RUN 2 SHA-256:

bc6c5be432f8a4d9b439df860ebe3aabfd69e81cfa084a9f8e2776aa0415461f.

Byte-identical:

PASS.

FROZEN SIGNALS

NANITE_LONG_MEMORY_SIGNAL:

FALSE.

STRONG_NANITE_SIGNAL:

FALSE.

FULL_NANITE_RECOVERY:

FALSE.

TEMPORAL_SUBSTRATE_CANDIDATES:

NONE.

OVERSTABILIZED_METHODS:

N16_H6_DAMP.

REFERENCE — SLOW128_MIXED1

D1:

1.0.

D4:

0.69189453125.

D8:

0.5517578125.

D16:

0.50439453125.

D32:

0.49365234375.

Memory score:

0.52001953125.

State entropy:

0.6964955425142572.

N16_H5

D1:

1.0.

D4:

0.68701171875.

D8:

0.53759765625.

D16:

0.5107421875.

D32:

0.4912109375.

Memory score:

0.5105794270833333.

Nonlinear score:

0.5405493253414746.

State entropy:

0.4143528104789671.

Median:
nanite:
bit-change count:

5232.

Median:
nanite:
run length:

3:
external steps.

Interpretation:

H5:
remains:
active
and:
dynamically balanced

but:
does NOT:
extend:
raw:
delay memory.

N16_H6

D16:

0.50537109375.

D32:

0.49951171875.

Median:
nanite:
bit-change count:

931.

Median:
nanite:
run length:

10.5:
steps.

Thus:

stronger:
hysteresis
creates:
much:
longer-lived:
controller state

without:
producing:
recoverable:
D16 /
D32:
input identity.

This is:
important:

PERSISTENT:
LOCAL STATE

is NOT:
automatically:

USEFUL:
TASK-RELEVANT:
MEMORY.

N16_H6_REPAIR

D1:

0.99169921875.

D4:

0.62158203125.

D8:

0.5322265625.

D16:

0.5048828125.

D32:

0.501953125.

Memory score:

0.51220703125.

Nonlinear score:

0.5474283611489688.

PARITY5:

0.5771484375.

Median:
repair:
state changes:

8713.5
per:
4096-step:
world.

Median:
repair:
changes
per:
external:
step:

2.1273193359375.

Median:
nanite:
bit changes:

466.

Median:
nanite:
run length:

9.5:
steps.

Interpretation:

bounded:
local:
repair

changes:
the:
feature geometry

and:
improves:
some:
nonlinear:
structure

but:
does NOT:
preserve:
arbitrary:
old:
input bits.

N16_H6_DAMP

OVERSTABILIZED.

State entropy:

0.05956502927131284.

Feature rank:

1
of:
512.

D1:

0.49267578125.

D16:

0.49853515625.

D32:

0.494140625.

Median:
nanite:
bit changes:

0.

Median:
nanite:
run length:

4096.

Median:
suppressed:
worker transitions:

25032.

Interpretation:

the:
controller:
successfully:
stabilized:
the:
state

so:
aggressively

that:

the:
reservoir
ceased:
to:
carry:
useful:
dynamic:
information.

This is:
a:
clean:
STABILITY /
PLASTICITY:
failure.

TECHNICAL INTERPRETATION

DG-1R-04 rejects:

the:
simple:
hypothesis

that:

local:
one-bit:
homeostatic:
controllers

can:
turn:
this:
ReCA architecture
into:
a:
general:
16-32:
step:
delay-memory:
substrate.

However:

the:
experiment
does NOT:
show:

software nanites
are:
useless.

It shows:

their:
natural:
effect
is:

STATE:
REGULATION,

not:

ARBITRARY:
HISTORY:
ENCODING.

Evidence:

1.
H6 creates:
long-lived:
local:
controller:
state.

2.
REPAIR performs:
thousands:
of:
bounded:
local:
corrections

while:
remaining:
dynamically:
alive.

3.
DAMP demonstrates:
that:
too much:
protection
can:
collapse:
the:
organism
into:
near-static:
state.

Therefore:

the:
next:
correct:
question
is NOT:

"can nanites remember old random bits?"

It is:

"can nanites prevent local damage from spreading
and restore an organism toward
the state it would have occupied
without the damage?"

This aligns:
directly
with:
Yggdrasil's:
repair /
homeostasis:
north-star.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05 —
LOCAL DAMAGE CONTAINMENT /
COUNTERFACTUAL RECOVERY AUDIT.

Use:

the:
same:
128-bit:
organism.

Develop:
the:
system
under:
a:
common:
input stream.

At:
a:
frozen:
damage time:

clone:
the:
organism.

Reference clone:

undamaged.

Damage clone:

flip:
a:
frozen:
set
of:
worker:
cells.

Continue:

both:
under:
identical:
future:
input.

Measure:

Hamming:
divergence
between:

damaged
and:
undamaged:
counterfactual trajectories

at:

1,
4,
8,
16,
32:
steps.

Also measure:

- damage:
  spread
  outside:
  the:
  original:
  lesion;

- recovered:
  lesion:
  cells;

- total:
  excess:
  divergence:
  area;

- controller:
  intervention:
  count;

- whether:
  repair:
  returns:
  the:
  organism:
  toward:
  its:
  own:
  undamaged:
  trajectory.

Primary comparison:

SLOW128_MIXED1

versus:

N16_H5,
N16_H6,
N16_H6_REPAIR.

Exclude:

N16_H6_DAMP
from:
primary:
repair:
candidate
classification

because:

DG-1R-04
already:
demonstrated:
severe:
overstabilization.

It may remain:
as:
an:
overstabilized:
negative:
control.

PLAIN-SPEAK SUMMARY

What happened to:
the:
nanite idea?

It did NOT:
solve:
long-term:
random-bit:
memory.

But:

it:
did:
something:
real.

The:
nanites:
changed:
how:
stable
the:
organism
was.

Mild:
nanites
could:
hold:
local:
state
for:
longer.

Repair:
nanites
could:
make:
thousands:
of:
small:
local:
corrections
without:
completely:
freezing:
the:
system.

The:
aggressive:
damping:
nanites
went:
too far:

they:
basically:
froze:
the:
organism.

That:
is:
actually:
useful:
information.

We now:
have:
direct:
evidence
of:
the:
balance
we:
need:

too little:
protection
=
memory /
structure:
washes away.

too much:
protection
=
the:
organism:
cannot:
change.

So:

the:
next:
test
uses:
the:
nanites
for:
what:
they:
appear:
naturally:
suited:
to:

REPAIR.

We will:
damage:
the:
software organism

and:
see:
whether:
nanites
help:
it:
return:
toward:
the:
trajectory
it:
would:
have:
followed
if:
it:
had:
never:
been:
damaged.

That:
is:
much:
closer
to:
Yggdrasil's:
self-healing:
goal
than:
forcing:
the:
nanites
to:
act:
like:
a:
history:
buffer.

canonical_scientific_execution = false.
stab18_r1_touched = false.
