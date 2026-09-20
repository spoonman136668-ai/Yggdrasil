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
