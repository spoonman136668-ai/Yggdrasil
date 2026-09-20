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
