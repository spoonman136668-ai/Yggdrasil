TITLE: DG-1R-04 — Programmed Software-Nanite Local Stabilization Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ACTIVE-STABILIZATION PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL REGULATION / MEMORY STABILITY
BRANCH: dg1a-ar
PARENT: DG-1R-03

PURPOSE

DG-1R-03 established:

- passive slowing improves D1 / D4 / D8;
- passive slowing does NOT recover D16 / D32;
- fixed multi-timescale lanes do NOT recover D16 / D32.

Therefore:

the next hypothesis is:

OLDER INFORMATION
NEEDS:
ACTIVE:
LOCAL:
STABILIZATION

rather than:
only:
a slower:
global:
clock.

DG-1R-04 tests the user's proposed:

"programmed software nanites"

as:

small:
local:
controller cells

whose:
only:
job
is:
to:
suppress:
overly destructive:
cellular transitions.

BOUNDARY

Synthetic software-only experiment.

"Nanite" means:

a:
programmed:
software:
stabilizer cell.

No:
physical nanotechnology.
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

FAIR STATE BUDGET

Every ReCA method uses:

128:
persistent:
binary:
state bits.

NANITE METHODS

112:
worker:
CA cells.

16:
stabilizer:
controller cells.

Total:

128.

The nanite methods therefore:

DO NOT:
receive:
additional:
persistent:
memory.

WORKER TOPOLOGY

Worker cells:

indices:
0..111.

One:
periodic:
112-cell:
worker ring.

Controller cells:

logical:
indices:
112..127.

The:
16:
controller cells

do NOT:
participate
in:
the:
worker:
nearest-neighbor:
CA rule.

Instead:

each:
controller
owns:
one:
contiguous:
7-worker:
sector.

Sector j:

workers:

7*j
through:
7*j+6.

Thus:

16 * 7
=
112:
worker cells.

INPUT MAPPING

8:
fixed:
mapped:
worker positions.

The:
112-worker:
input space

is:
partitioned
into:
8:
contiguous:
14-worker:
mapping compartments.

At:
world initialization:

choose:
one:
fixed:
mapped worker position
uniformly
inside:
each:
14-worker:
compartment.

The:
same:
8:
global worker positions

are:
used:
for:
ALL:
ReCA methods,
including:
the:
128-worker:
controls.

Thus:

input:
location
is:
paired
across:
methods.

INPUT RECURRENCE

Literature-style:

OVERWRITE.

At:
each:
external:
input:

state[mapped]
=
u_t.

For:
nanite methods:

this:
overwrite
applies:
to:
worker cells
before:
stabilizer decisions.

GLOBAL MICROTICKS

4:
microticks
per:
external:
input.

Readout:

record:
the:
full:
128-bit:
persistent state

after:
each:
microtick.

Feature dimension:

512 bits.

For:
nanite methods:

the:
readout state
is:

112:
worker bits
+
16:
controller bits.

For:
ordinary controls:

128:
worker bits.

WORKER RULE

Unless:
otherwise specified:

MIXED5:
fixed:
world-specific:
per-worker:
rules

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

No:
worker:
rule
is:
trained.

PROGRAMMED STABILIZER RULE

At:
a:
worker:
update microtick:

1.
start from:
the:
current:
POST-INPUT:
worker state;

2.
compute:
the:
ordinary:
MIXED5:
proposed:
next:
112-worker:
state;

3.
for:
each:
7-worker:
sector:

calculate:

flip_fraction
=
number:
of:
worker bits
that:
would:
change
/
7;

4.
compare:
flip_fraction
to:
the:
frozen:
nanite threshold;

5.
if:
flip_fraction
>
threshold:

controller bit
=
1;

VETO:
the:
proposed:
transition
for:
that:
7-worker:
sector;

the:
sector:
retains:
its:
current:
post-input:
state;

6.
else:

controller bit
=
0;

COMMIT:
the:
proposed:
sector state.

IMPORTANT

The:
nanite
does NOT:

- store:
  u_t
  in:
  a:
  hidden:
  register;
- store:
  the:
  previous:
  worker sector
  somewhere else;
- maintain:
  an:
  external:
  countdown timer;
- access:
  task labels;
- access:
  readout targets;
- access:
  future:
  input.

The:
veto
uses only:

CURRENT:
local worker state

and:

CURRENT:
proposed:
local:
CA transition.

If:
a:
transition
is:
vetoed,

the:
already-written:
current:
input
is:
NOT:
rolled back.

Thus:

nanites:
stabilize:
post-input:
state,

not:
erase:
new:
input.

CONTROLLER PERSISTENCE

Controller bits:

are:
part:
of:
the:
128-bit:
persistent state.

At:
a:
microtick
where:
a:
worker update
occurs:

each:
controller
is:
set:
to:
the:
current:
veto decision.

At:
a:
microtick
where:
workers:
do not:
update:

controller bits
hold:
their:
previous:
state.

No:
additional:
controller memory
exists.

METHODS

1.
FAST128_MIXED4

128:
ordinary:
worker cells.

No:
controllers.

Worker clock:

FAST4:
microticks:
1,
2,
3,
4.

Purpose:

fast:
all-worker:
reference.

2.
SLOW128_MIXED1

128:
ordinary:
worker cells.

No:
controllers.

Worker clock:

SLOW1:
microtick:
4.

Purpose:

best:
passive:
slowing:
reference
from:
DG-1R-03.

3.
INERT112_16_FAST4

112:
MIXED5:
worker cells.

16:
controller-state:
bits
fixed:
to:
0.

Workers:

FAST4.

No:
stabilization.

Purpose:

capacity /
topology:
control
for:
the:
112+16:
architecture.

4.
NANITE112_16_FAST4_T50

112:
MIXED5:
workers.

16:
active:
stabilizers.

Workers:

FAST4.

Veto threshold:

0.50.

Because:
sector size
=
7,

a:
veto occurs
when:

at least:
4:
of:
7:
workers

would:
change.

5.
NANITE112_16_FAST4_T35

112:
MIXED5:
workers.

16:
active:
stabilizers.

Workers:

FAST4.

Veto threshold:

0.35.

Because:
sector size
=
7,

a:
veto occurs
when:

at least:
3:
of:
7:
workers

would:
change.

Purpose:

more:
aggressive:
stabilization
control.

6.
NANITE112_16_SLOW1_T50

112:
MIXED5:
workers.

16:
active:
stabilizers.

Worker clock:

SLOW1.

Threshold:

0.50.

Purpose:

test:
active:
stabilization

combined:
with:
the:
passive:
slowing
that:
helped:
D4 /
D8
in:
DG-1R-03.

BASELINES

RAW32.

RANDOM512.

Exact:
DG-1R-01:
definitions.

SEQUENCE

4096:
iid:
binary:
input steps
per:
world.

Warmup:

64.

Train:

64..2111.

2048:
rows.

Gap:

448.

Test:

2560..3583.

1024:
rows.

TASKS

Exact:
DG-1R:
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

included:
and:
unregularized.

Threshold:

0.5.

MOTIF2_12:

balanced accuracy.

All:
others:

accuracy.

DYNAMIC METRICS

Exact:
DG-1R-03:
definitions:

- binary:
  feature entropy;
- numerical:
  feature rank;
- Fisher:
  PARITY5:
  separation;
- Fisher:
  MOTIF2_12:
  separation.

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
bit:
98

in:
one:
clone.

For:
nanite methods:

worker:
98
lies:
inside:
a:
stabilized:
worker sector.

Continue:

identical:
future input

under:
the:
method's:
frozen:
worker clock
and:
nanite rule.

Measure:

normalized:
Hamming distance

over:
all:
128:
persistent bits

at:
external horizons:

1,
4,
8,
16.

STABILIZER TELEMETRY

For:
active:
nanite methods:

report:

- veto decisions;
- total:
  sector decisions;
- veto fraction;
- realized:
  worker-change fraction;
- mean:
  proposed:
  worker-change fraction.

For:
INERT112_16:

veto fraction:

0.

For:
128-worker:
controls:

stabilizer telemetry:

NOT_APPLICABLE.

RESOURCE ACCOUNTING

All:
ReCA methods:

persistent:
state:

128 bits.

Readout:

512 bits.

FAST128:

512:
CA cell updates
per:
external:
input.

SLOW128:

128:
CA cell updates.

INERT112_16_FAST4:

448:
worker CA updates.

NANITE112_16_FAST4:

448:
worker:
proposed:
CA updates

plus:

64:
local:
sector:
stabilizer decisions
per:
external:
input.

NANITE112_16_SLOW1:

112:
worker:
proposed:
CA updates

plus:

16:
local:
stabilizer decisions.

Trainable:
reservoir parameters:

0.

Trainable:
readout scalars:

513:
per task.

WORLD FAMILY

8:
disjoint:
worlds.

Seeds:

20260926040000
through:
20260926040007.

No:
DG-1R-01 /
02 /
03:
seed reuse.

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
h16 perturbation
in:
[0.01,0.75].

TEMPORAL_SUBSTRATE_CANDIDATE:

all:
three.

FROZEN ACTIVE-STABILIZATION TEST

Primary active-control reference:

INERT112_16_FAST4.

For:
each:
FAST4:
nanite method

report:

paired:
nanite
minus:
INERT112_16_FAST4

for:

D1,
D4,
D8,
D16,
D32,
memory score,
nonlinear score.

ACTIVE_STABILIZATION_SIGNAL

TRUE
if:

at least:
one:
FAST4:
nanite method

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

versus:
INERT112_16_FAST4

AND:

its:
median:
nonlinear score

is:
no more than:
0.05
below:
INERT112_16_FAST4.

PASSIVE_COMPARISON_SIGNAL

TRUE
if:

at least:
one:
nanite method

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

versus:
SLOW128_MIXED1

AND:

its:
median:
nonlinear score

is:
no more than:
0.05
below:
SLOW128_MIXED1.

NANITE_MEMORY_RECOVERY

TRUE
if:

at least:
one:
nanite method

is:
MEMORY_CAPABLE

while:

INERT112_16_FAST4
and:
SLOW128_MIXED1

are:
not.

OVERSTABILIZATION TELEMETRY

Flag:
OVERSTABILIZED

for:
a:
nanite method
if:

median:
veto fraction
>=0.75

AND:

median:
state entropy
<0.20

OR:

median:
feature-rank fraction
<0.15.

This flag:

does NOT:
change:
the:
primary:
memory classification.

IMPORTANT

If:
nanites improve:
D16 /
D32
versus:
INERT112_16

then:

active:
local:
transition regulation
adds:
something:
passive:
capacity reduction
does not.

If:
nanites improve:
over:
SLOW128

then:

active stabilization
adds:
something:
passive slowing
does not.

If:
T35:
freezes:
too much
while:
T50:
helps:

the:
stability /
plasticity:
tradeoff
is:
directly visible.

If:
both:
nanite thresholds
fail:

local:
instantaneous:
transition veto
is:
insufficient.

That would motivate:

a:
second:
nanite family

with:
bounded:
refresh /
anchor:
state

or:
local:
repair
rather than:
only:
veto.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-04:
primary world,

do not alter:

- 128-bit:
  total state budget;
- 112 / 16:
  worker-controller split;
- worker sectors;
- input mapping;
- overwrite recurrence;
- worker rules;
- controller rule;
- thresholds;
- clocks;
- readout;
- tasks;
- perturbation protocol;
- metrics;
- gates;
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

Runtime sidecar:

non-canonical.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The last:
experiment
showed:

slowing:
the:
cells
helps:

but:
they:
still:
forget.

This experiment
gives:
16:
of:
the:
same:
128:
software cells

a:
different:
job.

They become:

tiny:
local:
stabilizers.

Before:
a:
worker neighborhood
is:
allowed:
to:
change,

its:
nanite
asks:

"would:
this:
update
change:
too much
of:
my:
local:
area?"

If:
yes:

the:
nanite
blocks:
that:
one:
local:
transition.

If:
no:

the:
change
goes:
through.

The:
nanite
does NOT:
keep:
a:
secret:
copy
of:
the:
memory.

It only:
acts:
like:
a:
local:
shock absorber.

The:
question
is:

can:
active:
local:
protection

preserve:
D16 /
D32:
memory

better:
than:
simply:
making:
all:
cells
slower?

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-04 SOFTWARE-NANITE STABILIZATION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-04 PRIMARY WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_04_nanite_stabilization_v1.py

Harness commit:

94f86d02a05847b56bad5508c8fc870810810d83.

Git blob SHA:

2c5542ac27e0871ff1b96b9d085a0e9bb1f40d49.

Source SHA-256:

d9c176a232ee90e2a138a47f153a0d2f99b28cdf618e680dc38be9b6c9299905.

Source bytes:

15774.

DEPENDENCY

DG-1R-03 harness Git blob:

7b5d6995450195f10d7ae2c474cf6936093dcf96.

DG-1R-03 source SHA-256:

f75e7089f1ff3ac8bd55d9126c2cb7950f08feb775a1ce8e5571269eee4fefb9.

PRE-FREEZE SANITY

Python compile:

PASS.

All:
nanite /
inert:
feature surfaces:

512:
bits:
per:
external:
input.

Non-primary:
short-stream:
sanity:

INERT112_16_FAST4:
veto fraction:
0.

NANITE112_16_FAST4_T50:
veto fraction:
approximately:
0.428.

NANITE112_16_FAST4_T35:
veto fraction:
approximately:
0.497.

NANITE112_16_SLOW1_T50:
veto fraction:
approximately:
0.413.

These:
sanity:
values
are:
NON-EVIDENCE.

No:
primary:
DG-1R-04:
world
was:
executed
before:
this freeze.

FROZEN WORLD FAMILY

20260926040000..20260926040007.

8 worlds.

FROZEN TOTAL STATE

All:
ReCA methods:

128:
persistent:
bits.

Nanite methods:

112:
worker bits
+
16:
controller bits.

No:
hidden:
input register.

No:
hidden:
timer.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical output SHA-256
must:
match exactly.

Runtime sidecars:

non-canonical.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-04 NON-EVIDENCE PILOT CLOSURE — SOFTWARE-NANITE LOCAL STABILIZATION

DATE:
2026-09-20.

STATUS:
COMPLETE /
NEGATIVE THRESHOLD-VETO NANITE RESULT /
MECHANISTIC OVER-STABILIZATION SIGNAL /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

d9c176a232ee90e2a138a47f153a0d2f99b28cdf618e680dc38be9b6c9299905.

CANONICAL OUTPUT

RUN 1 SHA-256:

34cab21965bc7c61f4499b0b6059982695ed49d94815f03cfe7537e7e0257a30.

RUN 2 SHA-256:

34cab21965bc7c61f4499b0b6059982695ed49d94815f03cfe7537e7e0257a30.

Byte-identical:

PASS.

PRIMARY CLASSIFICATION

ACTIVE_STABILIZATION_SIGNAL:

FALSE.

PASSIVE_COMPARISON_SIGNAL:

FALSE.

NANITE_MEMORY_RECOVERY:

FALSE.

TEMPORAL_SUBSTRATE_CANDIDATES:

NONE.

INERT112_16_FAST4 CONTROL

Median:

D8:
0.50146484375.

D16:
0.49462890625.

D32:
0.498046875.

Memory score:

0.4957682291666667.

Feature rank:

269 / 512.

Feature-rank fraction:

0.525390625.

State entropy:

0.5926879752853804.

Realized worker-change fraction:

0.3930424281529018.

NANITE112_16_FAST4_T50

Median:

veto fraction:

0.6675834655761719.

Proposed worker-change fraction:

0.45544569832938053.

Realized worker-change fraction:

0.02727508544921875.

Thus:

the:
nanites
reduced:
realized:
worker-state change

by:
approximately:
an:
order of magnitude.

However:

D8:
0.49462890625.

D16:
0.5068359375.

D32:
0.4931640625.

Memory score:

0.5003255208333334.

Paired:
versus:
INERT112_16:

D16:
+0.0185546875.

D32:
-0.0048828125.

These:
miss:
the:
frozen:
>=0.10:
active-stabilization gate.

Feature rank:

7 / 512.

Feature-rank fraction:

0.013671875.

State entropy:

0.10852350921262315.

The:
reservoir
became:
extremely:
low-dimensional.

NANITE112_16_FAST4_T35

Median:

veto fraction:

0.5049991607666016.

Proposed worker-change fraction:

0.2657996586390904.

Realized worker-change fraction:

0.009014947073800223.

Feature rank:

2.5 / 512.

Feature-rank fraction:

0.0048828125.

State entropy:

0.084579629018642.

D16:
0.49658203125.

D32:
0.49853515625.

No:
long-memory:
gain.

NANITE112_16_SLOW1_T50

Median:

veto fraction:

0.585845947265625.

Realized worker-change fraction:

0.041445050920758925.

Feature rank:

16 / 512.

State entropy:

0.11822014982000272.

D16:
0.49169921875.

D32:
0.4912109375.

Combining:

passive:
slowing

with:
the:
same:
threshold-veto:
stabilization

does NOT:
recover:
long memory.

FROZEN OVERSTABILIZED FLAG

The:
pre-registered:
OVERSTABILIZED:
flag

did NOT:
fire

because:

its:
veto-fraction:
condition
required:

>=0.75.

Observed:
median:
veto fractions

were:
below:
0.75.

However:

the:
observed:
feature-rank
and:
entropy:
collapse

show:
a:
clear:
practical:
over-stabilization:
mechanism.

This:
does NOT:
retroactively:
change:
the:
frozen:
flag.

TECHNICAL INTERPRETATION

DG-1R-04 establishes:

ACTIVE:
LOCAL:
STABILIZATION

can:
strongly:
suppress:
state change.

Therefore:

the:
software-nanite:
controller
has:
real:
causal:
authority
over:
reservoir dynamics.

But:

the:
current:
threshold rule

protects:
TOO MUCH:
STATE

and:
does not:
know:
which:
state changes
are:
useful
versus:
destructive.

The:
resulting:
system

becomes:
stable

but:
not:
informative.

This is:
the:
stability /
plasticity:
tradeoff
we:
expected
as:
the:
main:
risk.

The:
important:
negative finding
is:

MAXIMIZING:
STABILITY

does NOT:

MAXIMIZE:
MEMORY.

A:
useful:
memory substrate

must:
preserve:
specific:
information

while:
still:
allowing:
enough:
state evolution
to:
encode:
new:
inputs.

NEXT HYPOTHESIS

Do NOT:
abandon:
active:
stabilizers.

Instead:

BOUND:
their:
intervention.

Two:
mechanisms
are:
now:
justified:

1.
REFRACTORY NANITES

After:
a:
nanite
vetoes:
one:
transition,

it:
must:
allow:
the:
next:
eligible:
transition

before:
it:
may:
veto:
again.

This:
uses:
the:
controller's:
existing:
one-bit:
state

as:
a:
refractory:
flag.

No:
additional:
persistent:
memory.

2.
GLOBAL INTERVENTION BUDGET

At:
each:
worker:
microtick:

rank:
sectors
by:
proposed:
flip fraction.

Allow:
only:
the:
K:
most:
volatile:
sectors

to:
veto.

Examples:

K=1:
6.25%:
maximum:
sector intervention.

K=2:
12.5%.

This:
prevents:
the:
whole:
reservoir
from:
freezing.

NEXT JUSTIFIED EXPERIMENT

DG-1R-05 —
BOUNDED-INTERVENTION:
SOFTWARE-NANITE:
STABILITY /
PLASTICITY:
AUDIT.

Compare:

- INERT112_16_FAST4;
- REFRACTORY_T50;
- REFRACTORY_T35;
- BUDGET_K1;
- BUDGET_K2;
- SLOW128_MIXED1.

Primary question:

can:
nanites
protect:
a:
small:
fraction:
of:
the:
most:
destructive:
local:
changes

without:
collapsing:
feature rank
and:
entropy?

PLAIN-SPEAK SUMMARY

The:
nanites
definitely:
worked
as:
brakes.

They:
worked:
too well.

They:
stopped:
so much:
cellular:
change
that:
the:
reservoir
lost:
almost:
all:
of:
its:
interesting:
internal:
patterns.

It became:

stable,

but:
mostly:
dead.

That:
did not:
help:
16-step
or:
32-step:
memory.

So:

the:
idea
is:
not:
"stabilization:
doesn't work."

The:
lesson
is:

the:
nanites
cannot:
be:
allowed
to:
slam:
the:
brakes
every:
time:
a:
neighborhood
changes:
a lot.

They:
need:
rules
that:
force:
them
to:
let:
the:
system
move
again.

The:
next:
version
will:
put:
a:
hard:
budget
on:
how:
much:
stabilization
they:
can:
apply.

That:
tests:
whether:
we:
can:
find:
a:
middle ground
between:

forgetting:
too fast

and:

freezing:
too hard.

canonical_scientific_execution = false.
stab18_r1_touched = false.
