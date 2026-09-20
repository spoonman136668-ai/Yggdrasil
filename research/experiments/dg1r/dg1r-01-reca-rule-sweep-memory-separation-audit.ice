TITLE: DG-1R-01 — Reservoir Cellular Automata Rule-Sweep Memory / Separation / Perturbation Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ReCA MECHANICAL PILOT
TRACK: DG-1R / SOFTWARE CELLS / TEMPORAL MEMORY SUBSTRATE
BRANCH: dg1a-ar
PARENT_SYNTHESIS: research/foundations/reca-software-cell-transformer-limit-synthesis.ice
MOTIVATING_RESULT: DG-1A-CLR3-H191-P12 negative conditional patch-routing result

PURPOSE

H191-P11 and P12 established that:

- developmental patch geometry is not safely globally mergeable;
- aggressive static patch hibernation distorts earlier capability state;
- later patch geometry does not automatically substitute for earlier birth-time state.

Therefore:

DG-1R moves to a different resource axis:

TEMPORAL STATE
instead of:
STATIC STRUCTURAL COMPRESSION.

P12 asks whether:

small:
fixed-rule:
software-cell reservoirs

can:
carry:
sequence memory
and:
nonlinear temporal features

with:

zero:
trained reservoir weights

and:

only:
small:
linear readouts.

BOUNDARY

Synthetic software-only experiment.

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

LITERATURE MOTIVATION

Reservoir Computing using Cellular Automata
(Yilmaz, 2014):

demonstrates:
CA space-time evolution
as:
a reservoir feature map.

Deep Reservoir Computing Using Cellular Automata
(Nichele / Molund, 2017):

shows:
cellular reservoirs
can:
perform:
temporal memory tasks
and:
stacked reservoirs
can:
improve:
memory behavior.

PRESENT EXPERIMENT

This experiment does NOT:

rely only on:
the classic:
5-bit memory task.

It tests:

multiple:
memory,
nonlinear,
and:
sequence-structure targets

plus:

state:
entropy,
feature rank,
and:
perturbation propagation.

RESERVOIR FAMILY

One-dimensional:
binary:
Elementary Cellular Automata.

Width:

128 cells.

Boundary:

circular / periodic.

Initial state:

all zero.

External binary input:

u_t ~ Bernoulli(0.5).

Input injection:

16:
fixed:
world-specific:
cell positions.

At:
each external time step:

1.
if:
u_t = 1,

XOR:
the:
16-cell:
injection mask
into:
the:
current state;

2.
apply:
the:
cellular rule
for:
4:
internal:
evolution steps;

3.
record:
the:
full:
128-cell state
after:
each:
internal step.

Readout feature dimension:

128 * 4
=
512.

Reservoir weights:

none.

RULES

ECA90.
ECA150.
ECA110.
ECA22.
ECA30.

MIXED5:

each:
cell
is assigned:
one:
frozen rule

from:

90,
150,
110,
22,
30

with:
approximately:
equal:
world-specific:
counts.

The:
per-cell:
rule assignment
is:
frozen
for:
the entire:
world.

BASELINES

RAW32

Feature:

the:
previous:
32:
input bits

u_(t-1)
through:
u_(t-32).

Dimension:

32.

No:
nonlinear:
feature map.

RANDOM512

Input:

the:
same:
RAW32:
history.

Fixed:
world-specific:
random:
binary:
projection

from:

32
to:
512:
features.

Projection:

weights:
-1
or:
+1.

Biases:

integer:
uniform:
[-4,4].

Feature:

1
if:
lag_vector @ weight
+
bias
>
0,

else:
0.

No:
trained:
feature weights.

Only:
the:
readout
is:
trained.

SEQUENCE

Per world:

4096:
iid:
binary:
input steps.

Warmup:

64.

Training indices:

64..2111
inclusive.

Training rows:

2048.

Gap:

448:
unused:
steps.

Test indices:

2560..3583
inclusive.

Test rows:

1024.

No:
train/test:
overlap.

TASKS

D1:
predict:
u_(t-1).

D4:
predict:
u_(t-4).

D8:
predict:
u_(t-8).

D16:
predict:
u_(t-16).

D32:
predict:
u_(t-32).

XOR3_11:

predict:

u_(t-3)
XOR
u_(t-11).

PARITY5:

predict:
XOR
of:
u_(t-1)
through:
u_(t-5).

MOTIF2_12:

look at:
u_(t-1)
through:
u_(t-12).

Label:
1
if:
the:
motif:
101

occurs:
at least:
twice
inside:
that:
12-bit:
history,

including:
overlapping:
occurrences.

Else:
0.

READOUT

One:
independent:
linear:
ridge:
readout
per:
task.

Readout alpha:

1e-3.

Include:
bias.

Classification threshold:

0.5.

Reservoir / feature map:

frozen.

No:
backpropagation
through:
the:
reservoir.

TASK METRICS

For:

D1,
D4,
D8,
D16,
D32,
XOR3_11,
PARITY5:

accuracy.

For:

MOTIF2_12:

balanced accuracy

because:
class balance
is:
not:
forced.

REPORT

Per method:

median
and:
P10:
across worlds
for:

all:
task metrics.

Also report:

memory score:

mean:
D8,
D16,
D32:
accuracy.

nonlinear score:

mean:
XOR3_11,
PARITY5,
MOTIF2_12:
metric.

DYNAMIC-STATE METRICS

STATE ENTROPY

For:
ReCA methods:

mean:
binary entropy
across:
the:
512:
space-time:
features
on:
test rows.

For:
baselines:

same:
feature-wise:
binary entropy
definition.

FEATURE RANK

On:
the first:
512:
test rows

or:
all test rows
if:
feature dimension:
smaller:

center:
the:
feature matrix.

Compute:
singular values.

Numerical rank threshold:

s_i
>
s_max * 1e-8.

Also report:

rank / feature_dimension.

LINEAR SEPARATION TELEMETRY

For:
PARITY5
and:
MOTIF2_12:

compute:
Fisher:
between-class:
centroid distance squared

divided by:

mean:
within-class:
squared distance
+
1e-12.

This is:
telemetry.

It is NOT:
used:
for:
task labels
or:
readout training.

PERTURBATION PROPAGATION

ReCA only.

At:
external step:
512:

clone:
the:
current:
reservoir state.

Flip:
one:
cell:
at:
index:
64
in:
the:
clone.

Continue:
both:
reservoirs
under:
identical:
future:
input.

Measure:
normalized:
Hamming distance
between:
the:
128-cell:
states

after:
external:
horizons:

1,
4,
8,
16.

Baselines:

report:
NOT_APPLICABLE.

RESOURCE METRICS

ReCA:

persistent:
reservoir state:

128 bits
=
16:
bit-packed bytes.

Per-step:
space-time:
readout feature:

512 bits
=
64:
bit-packed bytes.

Deterministic:
cell-update count
per:
external step:

128 * 4
=
512.

Trainable:
reservoir parameters:

0.

Trainable:
readout scalars
per task:

513:
including:
bias.

RAW32:

state / feature:

32 bits.

Trainable:
readout scalars:

33.

RANDOM512:

dynamic:
history state:

32 bits.

Readout features:

512 bits.

Fixed projection weights:

32 * 512:
binary signs

plus:
512:
small:
integer biases.

Trainable:
feature parameters:

0.

Trainable:
readout scalars:

513.

WALL-CLOCK TELEMETRY

Measure:
feature-generation:
wall-clock time

per:
method
per:
world.

Wall-clock:
is:
NON-CANONICAL
telemetry.

It MUST:
be written
to:
a:
separate:
runtime sidecar.

It MUST NOT:
be:
included
in:
canonical:
result bytes.

CANONICAL:
reproducibility
therefore:
remains:
byte-exact.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926010000
through:
20260926010007.

METHOD FAIRNESS

Within:
one world:

all methods
use:

- the:
  same:
  input sequence;
- the:
  same:
  train/test:
  indices;
- the:
  same:
  task labels;
- the:
  same:
  ReCA:
  injection positions
  for:
  all:
  ReCA rules.

Rule-specific:
dynamics
are:
the:
only:
difference
between:
ReCA methods.

RANDOM512:
uses:
a:
world-specific:
projection
independent
of:
ReCA:
rule identity.

FROZEN INTERPRETATION

MEMORY_CAPABLE

if:

median:
memory score
>=0.70

AND:

median:
D16
>=0.70.

NONLINEAR_CAPABLE

if:

median:
nonlinear score
>=0.60

AND:

at least:
two:
of:
XOR3_11,
PARITY5,
MOTIF2_12

have:
median:
metric
>=0.60.

DYNAMICALLY_BALANCED

ReCA only.

if:

median:
state entropy

between:

0.20
and:
0.95

AND:

median:
horizon-16:
perturbation Hamming

between:

0.01
and:
0.75.

TEMPORAL_SUBSTRATE_CANDIDATE

if:

a:
ReCA method

is:

MEMORY_CAPABLE

AND:

NONLINEAR_CAPABLE

AND:

DYNAMICALLY_BALANCED.

IMPORTANT

A:
failure:
to:
meet:
TEMPORAL_SUBSTRATE_CANDIDATE

does NOT:
disprove:
ReCA.

It bounds:

this:
specific:
width,
injection,
rule,
and:
timescale:
configuration.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-01:
world,

do not alter:

- width;
- injection count;
- internal steps;
- rules;
- mixed-rule definition;
- baselines;
- sequence length;
- train/test split;
- tasks;
- readout alpha;
- perturbation protocol;
- rank threshold;
- classification gates;
- world family.

REPRODUCIBILITY

Two:
complete:
8-world:
canonical sweeps.

Canonical result SHA-256
must:
match exactly.

Runtime sidecars:
need not:
match.

NEXT

If:
at least one:
ReCA method

qualifies as:
TEMPORAL_SUBSTRATE_CANDIDATE,

proceed to:

DG-1R-02 —
STACKED /
MULTI-TIMESCALE:
ReCA.

If:

memory is strong
but:
nonlinearity weak,

test:

stacked:
heterogeneous:
rules

and:
nonlinear:
readout constraints.

If:

nonlinearity is strong
but:
memory weak,

test:

slower:
update schedules,
larger:
width,
and:
multi-timescale:
patches.

If:

all:
single-rule:
reservoirs
are:
weak
but:
MIXED5:
is:
strong,

prioritize:

heterogeneous:
software-cell:
populations.

PLAIN-SPEAK PRE-REGISTERED QUESTION

Can:
a:
tiny:
128-cell:
software organism

remember:
useful:
parts
of:
a:
binary history

and:
turn:
that:
history
into:
features
that:
a:
simple:
linear:
readout
can:
use?

We are:
not:
training:
the:
cells.

We are:
only:
letting:
them:
evolve

and:
training:
the:
small:
reader
on top.

The:
interesting result
is:
not:
whether:
one:
famous:
rule
wins.

It is:

whether:
local:
cell dynamics

can:
give:
useful:
memory
and:
nonlinear:
sequence structure

for:
very:
little:
persistent:
state
and:
zero:
trained:
reservoir weights.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-01 ReCA RULE-SWEEP HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-01 WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_01_reca_rule_sweep_v1.py

Harness commit:

05179e938aee726e6a503b81e9a45672576e2eb6.

Git blob SHA:

e053bf7f1088c5c8751d96afbd394dfa19f8a07c.

Source SHA-256:

f1c97e345f83bc6a12efa6d9aa72a4a8309c300a4d3f044ebccfdf80e473f483.

Source bytes:

14518.

LOCAL PRECHECK

Git blob identity:

PASS.

Python compile:

PASS.

No:
DG-1R-01:
world
was:
executed
before:
this freeze.

FROZEN READOUT DETAIL

Ridge alpha:

1e-3.

Feature coefficients:

regularized.

Bias coefficient:

NOT:
regularized.

All:
eight:
task readouts

are:
solved
in:
one:
multi-target:
linear system

per:
method /
world.

FROZEN ECA DETAIL

Wolfram neighborhood index:

4*left
+
2*center
+
right.

Rule bit:

(rule >> index)
&
1.

Periodic:
boundaries.

Input:
XOR injection
occurs:
once
before:
the:
four:
internal:
cellular updates
at:
each:
external:
time step.

PERTURBATION SNAPSHOT

Reference state:

after:
external:
step:
512

and:
its:
fourth:
internal:
update.

Perturbed clone:

flip:
cell:
64.

Horizon 1:

uses:
input:
step:
513.

Both:
reference
and:
perturbed:
reservoirs
receive:
identical:
future:
input.

RUNTIME

Feature-generation:
wall-clock timing

is:
written:
only:
to:
the:
runtime sidecar.

It is:
excluded:
from:
canonical:
result bytes.

FROZEN WORLD FAMILY

20260926010000..20260926010007.

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
telemetry only
and:
need not:
match.

canonical_scientific_execution = false.
stab18_r1_touched = false.


FINAL DG-1R-01 NON-EVIDENCE PILOT CLOSURE — ReCA RULE-SWEEP MEMORY / SEPARATION / PERTURBATION

DATE:
2026-09-20.

STATUS:
COMPLETE /
NEGATIVE SINGLE-TIMESCALE TEMPORAL-SUBSTRATE RESULT /
USEFUL MECHANISTIC SIGNALS /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

f1c97e345f83bc6a12efa6d9aa72a4a8309c300a4d3f044ebccfdf80e473f483.

CANONICAL OUTPUT

RUN 1 SHA-256:

139739396503208e3a88d90663cb2a465e163f8d68ad59095332a3c6f5a42afe.

RUN 2 SHA-256:

139739396503208e3a88d90663cb2a465e163f8d68ad59095332a3c6f5a42afe.

Byte-identical:

PASS.

TEMPORAL SUBSTRATE CANDIDATES

0.

No:
ECA90,
ECA150,
ECA110,
ECA22,
ECA30,
or:
MIXED5

met:
all:
memory,
nonlinearity,
and:
dynamic-balance:
gates.

LONG-MEMORY RESULT

All:
ReCA methods

are:
near chance
by:
D16 /
D32.

Median D16:

ECA90:
0.501953125.

ECA150:
0.50439453125.

ECA110:
0.48876953125.

ECA22:
0.49853515625.

ECA30:
0.5029296875.

MIXED5:
0.505859375.

Median D32:

ECA90:
0.4990234375.

ECA150:
0.4970703125.

ECA110:
0.4990234375.

ECA22:
0.5009765625.

ECA30:
0.4931640625.

MIXED5:
0.482421875.

Thus:

the:
frozen:
128-cell /
16-site XOR injection /
4-internal-step:
single-timescale:
configuration

does NOT:
retain:
useful:
16-32-step:
linear memory.

MIXED5 SHORT-MEMORY SIGNAL

MIXED5:

D1 median:

0.744140625.

P10:

0.7056640625.

This is:
the:
strongest:
reliable:
short-memory:
signal
among:
the:
tested:
cellular reservoirs.

D4:

0.521484375.

D8:

0.49853515625.

Thus:

heterogeneous:
rule assignment

improves:
immediate:
input retention,

but:
that:
memory
decays:
rapidly.

RULE 90 NONLINEAR SIGNAL

ECA90:

XOR3_11 median:

0.7587890625.

However:

P10:

0.48056640625.

Thus:

Rule 90
shows:
a:
strong:
median:
nonlinear:
XOR feature

but:
the:
effect
is:
not:
robust:
across:
worlds.

Its:
overall:
nonlinear score:

0.5886826039658208.

This misses:
the:
0.60:
frozen:
nonlinear-capable gate.

Its:
PARITY5
and:
MOTIF2_12

remain:
near:
chance.

DYNAMIC REGIMES

ECA22:

state entropy median:

0.9424848711089135.

Horizon-16:
perturbation Hamming:

0.3515625.

Classification:

DYNAMICALLY_BALANCED:
PASS.

But:

memory:
FAIL.

Nonlinearity:
FAIL.

MIXED5:

state entropy median:

0.7518172060639444.

Horizon-16 perturbation:

0.1328125.

Classification:

DYNAMICALLY_BALANCED:
PASS.

But:

long memory:
FAIL.

Nonlinearity:
FAIL.

ECA110:

perturbation persists:

h1:
0.03125.

h4:
0.07421875.

h8:
0.14453125.

h16:
0.234375.

But:

state entropy:

0.9893807715718957

exceeds:
the:
frozen:
0.95:
dynamic-balance:
upper bound.

ECA30:

h16:
0.31640625.

State entropy:

0.9993079297966428.

Thus:

its:
perturbations
spread,

but:
the:
state
is:
too:
near:
maximal:
binary entropy
under:
the:
frozen:
balance definition.

ECA90:

h16:

0.

Thus:

the:
single-cell:
perturbation
dies:
by:
horizon 16

in:
this:
periodic:
width-128 /
4-step:
configuration.

ECA150:

h16:

0.0078125,

below:
the:
frozen:
0.01:
balance floor.

FEATURE RANK

High:
feature rank
alone
does NOT:
produce:
usable:
temporal memory.

Median:
rank / dimension:

ECA110:
511 / 512.

ECA22:
511 / 512.

ECA30:
511 / 512.

Yet:
their:
D16 /
D32:
readouts
remain:
near:
chance.

Therefore:

high-dimensional:
state diversity

is:
not:
sufficient.

The:
feature map
must:
preserve:
task-relevant:
temporal information.

BASELINE CONTEXT

RAW32:

D1,
D4,
D8,
D16,
D32:

all:
1.0 median.

This is:
expected.

RAW32 explicitly:
stores:
the:
32-bit:
history.

Its:
nonlinear:
tasks
remain:
weak
with:
a:
linear readout.

RANDOM512:

memory score:

0.9990234375.

XOR3_11:

0.63671875.

MOTIF2_12:

0.6139696079324364.

PARITY5:

0.5029296875.

This:
fixed:
static:
nonlinear:
feature map

preserves:
explicit:
32-step history
and:
adds:
some:
nonlinear separability.

It is:
not:
a:
dynamic:
reservoir.

Its:
role
is:
to:
show:
that:
the:
readout /
sample size
are:
capable
of:
solving:
the:
memory tasks
when:
the:
relevant:
history
is:
actually present.

RESOURCE TELEMETRY

ReCA methods:

persistent:
dynamic state:

128 bits
=
16:
bit-packed bytes.

Readout:
space-time feature:

512 bits
=
64:
bit-packed bytes.

Reservoir:
trainable parameters:

0.

Cell updates:
per:
external step:

512.

Readout scalars:
per:
task:

513.

Observed:
feature-generation:
wall-clock
on:
the:
sandbox
was:
approximately:

0.33
to:
0.39 seconds
median
per:
4096-step:
ReCA world/method

across:
the:
two:
runtime sidecars.

This:
wall-clock data
is:
NON-CANONICAL
telemetry only.

TECHNICAL INTERPRETATION

DG-1R-01 does NOT show:

"ReCA cannot work."

It shows:

the:
specific:
single-timescale:
configuration

WIDTH:
128.

INPUT INJECTION:
16 XOR sites.

INTERNAL EVOLUTION:
4:
cellular updates
per:
input bit.

READOUT:
current:
4-step:
space-time block.

does NOT:
preserve:
long-range:
input identity
well enough
for:
D16 /
D32.

The:
mechanistic signals
split:

MIXED5:
best:
short memory
+
balanced dynamics.

ECA90:
isolated:
nonlinear XOR signal.

ECA22 /
ECA110 /
ECA30:
persistent:
perturbation propagation.

No:
single:
rule/configuration
combines:
all:
three.

NEXT ARCHITECTURAL HYPOTHESIS

Do NOT:
simply:
increase:
width
or:
select:
one:
famous:
rule.

The:
failure mode
points to:

MULTI-TIMESCALE:
CELLULAR MEMORY.

Use:

parallel:
software-cell:
reservoir lanes

that:
evolve
at:
different:
external clocks.

Example:

FAST:
update:
every:
input.

MEDIUM:
update:
every:
2:
inputs.

SLOW:
update:
every:
4:
inputs.

Keep:

total:
persistent:
cell count
bounded.

Allow:

different:
rule classes
per:
lane.

The:
slow lanes
should:
protect:
older:
input information

while:
fast:
lanes
supply:
nonlinear:
mixing.

NEXT JUSTIFIED EXPERIMENT

DG-1R-02 —
MULTI-TIMESCALE /
HETEROGENEOUS:
CELLULAR RESERVOIR AUDIT.

Primary comparisons:

1.
SINGLE128-MIXED5:
the:
DG-1R-01:
mixed-rule:
reference.

2.
PARALLEL-3:
bounded:
total:
128:
cells

split:
across:
fast /
medium /
slow:
lanes.

3.
STACKED-3:
fast:
lane
feeds:
medium,
medium:
feeds:
slow

under:
the:
same:
total:
cell budget.

4.
CLOCKED-HETEROGENEOUS:
lane-specific:
rule families.

Primary target:

recover:

D8 /
D16 /
D32:
memory

without:
destroying:
nonlinear:
separability
or:
dynamic:
stability.

PLAIN-SPEAK SUMMARY

What did we try?

We gave:
tiny:
128-cell:
software organisms

a:
stream:
of:
bits

and:
asked:
their:
evolving:
cell patterns
to:
remember:
the past

well enough
that:
a:
simple:
linear:
reader
could:
recover it.

What happened?

The:
single-speed:
reservoirs
forgot:
too quickly.

The:
mixed-rule:
organism
could:
remember:
the:
immediately previous:
bit
fairly well,

but:
by:
16
or:
32:
steps
the:
information
was:
effectively gone.

Rule 90
showed:
an:
interesting:
nonlinear:
XOR effect,

but:
it was:
not:
stable
across:
worlds.

Did ReCA fail?

No.

This:
specific:
single-speed:
design
failed:
the:
long-memory:
goal.

What did we learn?

Different:
cellular dynamics
are:
good at:
different:
things.

Some:
preserve:
short memory.

Some:
spread:
perturbations.

Some:
create:
nonlinear:
features.

The:
next:
design
should:
combine:
different:
timescales

instead of:
forcing:
one:
cell population
to:
do:
everything
at:
one:
speed.

What should we try next?

Build:
a:
small:
multi-speed:
cellular memory.

Some:
cells
react:
quickly.

Some:
change:
more slowly.

The:
goal
is:
for:
the:
slow:
cells
to:
protect:
older:
information

while:
the:
fast:
cells
do:
the:
nonlinear:
mixing.

This:
directly tests:
whether:
TIME
can:
replace:
some:
permanent:
stored:
history.

canonical_scientific_execution = false.
stab18_r1_touched = false.
