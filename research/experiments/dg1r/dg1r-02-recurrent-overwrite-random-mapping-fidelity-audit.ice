TITLE: DG-1R-02 — Recurrent Overwrite / Random-Mapping Fidelity Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ReCA RECURRENCE PILOT
TRACK: DG-1R / SOFTWARE CELLS / TEMPORAL MEMORY SUBSTRATE
BRANCH: dg1a-ar
PARENT: DG-1R-01
LITERATURE BASIS:
- Yilmaz 2014, Reservoir Computing using Cellular Automata
- Nichele & Molund 2017, Deep Reservoir Computing Using Cellular Automata

PURPOSE

DG-1R-01 found:
no temporal-substrate candidate
under:
single-stream XOR injection.

However:

the literature-faithful recurrent ReCA architecture
does NOT simply XOR a one-bit signal into a persistent state.

Nichele / Molund describe:

- fixed random mappings;
- concatenated mapped reservoirs;
- previous final CA state carried forward;
- the next mapped input OVERWRITES
  its mapped positions
  in that previous state;
- then:
  I CA iterations;
- concatenate:
  all I evolved states
  as:
  the time-step reservoir feature.

They explicitly note:

overwrite ensures:
a zero-valued input
also changes:
the next reservoir state.

They also report:
XOR recurrence
can:
reach attractors.

DG-1R-02 therefore asks:

WAS:
DG-1R-01's:
LONG-MEMORY FAILURE

CAUSED:
IN PART

BY:
THE:
XOR INPUT-UPDATE MECHANISM

RATHER THAN:
BY:
THE:
CELLULAR RULES THEMSELVES?

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

FIXED STATE BUDGET

Total CA width:

128 cells.

Periodic boundary.

Initial state:

all zero.

Input:

scalar binary:
u_t ~ Bernoulli(0.5).

RANDOM MAPPINGS

R = 8.

Diffuse length:

L_d = 16.

The:
128-cell:
state
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

Thus:

8:
fixed:
mapped positions
per:
world.

The same:
8 positions

are used by:
all:
rule / recurrence:
methods
inside:
that world.

CA ITERATIONS

I = 4.

At:
each:
external:
time step:

generate:
four:
successive:
CA states.

Feature:

concatenate:
all:
four:
128-cell:
states.

Feature dimension:

512.

RECURRENCE POLICIES

OVERWRITE

At:
time t:

start from:
the:
last CA state
from:
time t-1.

At:
all:
8 mapped positions:

write:
u_t
directly.

Thus:

u_t = 0:

sets:
the:
mapped:
cell
to:
0.

u_t = 1:

sets:
the:
mapped:
cell
to:
1.

Then:

apply:
the:
CA rule
for:
4 iterations.

XOR CONTROL

Identical:
state,
mapped positions,
rule,
iterations,
and:
feature extraction.

Difference:

if:
u_t = 1:

XOR:
1
into:
the:
8 mapped positions.

if:
u_t = 0:

do:
nothing.

This directly isolates:

overwrite
versus:
XOR recurrence.

RULES

ECA90.
ECA150.
ECA182.
ECA22.

These include:
the:
rules
reported:
among:
strong:
ReCA memory performers
in:
the:
prior literature.

MIXED5

Also test:
a:
heterogeneous:
per-cell:
frozen:
rule assignment
using:

90,
150,
110,
22,
30

with:
approximately:
equal:
counts.

Test:
both:

OVERWRITE_MIXED5
and:
XOR_MIXED5.

METHODS

OW90.
XR90.

OW150.
XR150.

OW182.
XR182.

OW22.
XR22.

OW_MIXED5.
XR_MIXED5.

BASELINES

RAW32.

RANDOM512.

Use:
the:
exact:
DG-1R-01:
baseline definitions.

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

448.

Test:

2560..3583
inclusive.

1024 rows.

TASKS

Exact:
DG-1R-01:
task set.

D1.
D4.
D8.
D16.
D32.
XOR3_11.
PARITY5.
MOTIF2_12.

READOUT

Exact:
DG-1R-01:
linear:
ridge:
readout.

Alpha:

1e-3.

Bias:

included
and:
unregularized.

Threshold:

0.5.

MOTIF2_12:

balanced accuracy.

All others:

accuracy.

DYNAMIC METRICS

Exact:
DG-1R-01:

- binary feature entropy;
- numerical feature rank;
- Fisher separation
  for:
  PARITY5
  and:
  MOTIF2_12;
- perturbation Hamming:
  h1,
  h4,
  h8,
  h16.

PERTURBATION

After:
external step:
512:

clone:
the:
last:
CA state.

Flip:
cell:
64
in:
one clone.

Continue:
both:
states

with:
identical:
future:
input
and:
the:
same:
recurrence policy.

For:
OVERWRITE:

mapped:
positions
are:
overwritten
before:
each:
future:
four-step:
evolution.

For:
XOR:

mapped:
positions
use:
the:
XOR control rule.

RESOURCE METRICS

Persistent:
CA state:

128 bits.

Readout feature:

512 bits.

CA updates:

512:
cell updates
per:
external:
step.

Mapped-position writes:

8:
per:
external:
step
for:
OVERWRITE.

XOR mapped operations:

0 or:
8
depending:
on:
u_t.

Trainable:
reservoir parameters:

0.

Readout scalars:

513:
per task.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926020000
through:
20260926020007.

No:
DG-1R-01:
seed reuse.

FROZEN CLASSIFICATION

Use:
the:
exact:
DG-1R-01:
gates.

MEMORY_CAPABLE:

median:
memory score
>=0.70

AND:

D16 median
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
entropy
in:
[0.20,0.95]

AND:

median:
h16 perturbation
in:
[0.01,0.75].

TEMPORAL_SUBSTRATE_CANDIDATE:

all:
three:
true.

RECURRENCE EFFECT

For:
each:
rule family

report:

OVERWRITE
minus:
XOR

for:

- D1;
- D8;
- D16;
- D32;
- memory score;
- nonlinear score;
- entropy;
- h16 perturbation.

OVERWRITE_RECOVERY_SIGNAL

if:

at least:
one:
OVERWRITE:
method

is:
MEMORY_CAPABLE

AND:

its:
paired:
XOR:
method
is:
not.

STRONG_RECURRENCE_SIGNAL

if:

at least:
one:
OVERWRITE:
method

is:
TEMPORAL_SUBSTRATE_CANDIDATE

AND:

its:
paired:
XOR:
method
is:
not.

IMPORTANT

A:
negative:
DG-1R-02
means:

the:
single-state /
I=4 /
R=8:
literature-style:
overwrite recurrence

still:
does not:
meet:
our:
general:
memory /
nonlinear:
criteria.

It does NOT:
invalidate:

- larger:
R;
- larger:
I;
- multi-timescale:
reservoirs;
- layered:
reservoirs;
- alternative:
input dimensions;
- ReCA:
more broadly.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-02:
world,

do not alter:

- width;
- R;
- L_d;
- I;
- mapped positions;
- recurrence definitions;
- rules;
- baselines;
- tasks;
- sequence split;
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
OVERWRITE_RECOVERY_SIGNAL:

perform:
DG-1R-03:
R / I:
memory-compute:
scaling
using:
the:
best:
overwrite rule family.

If:
no:
overwrite recovery
but:
short-memory:
or:
nonlinear:
signals improve:

proceed:
to:
multi-timescale /
layered:
ReCA.

If:
overwrite
is:
uniformly:
no better:

deprioritize:
this:
recurrent mapping
for:
Yggdrasil
and:
move:
to:
multi-timescale:
cellular memory.

PLAIN-SPEAK PRE-REGISTERED QUESTION

The first:
cellular reservoir
may have:
forgotten too quickly

because:
we were:
flipping:
input cells

instead of:
writing:
the:
new:
input value
onto:
the:
old:
state.

This test:
changes:
only:
that:
recurrent:
input mechanism

while:
keeping:
the:
cell budget,
four-step:
evolution,
tasks,
and:
readout
fixed.

If:
memory:
comes back,

we learned:
the:
problem
was:
our:
recurrence design,

not:
the:
basic:
cellular-reservoir:
idea.

canonical_scientific_execution = false.
stab18_r1_touched = false.
