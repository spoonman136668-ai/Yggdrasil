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


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-02 RECURRENT OVERWRITE FIDELITY HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-02 WORLD.

HARNESS

research/experiments/dg1r/harnesses/dg1r_02_recurrent_overwrite_v1.py

Harness commit:

9adb583bcb33d1b1bc430b8c350a6d5a6ddd0438.

Git blob SHA:

f82218188792185f1880386b4de10a5f8301b826.

Source SHA-256:

79d4da0f5585054debfdd873181d3e7463872c294a9dcf61e22e434c7c65ea1b.

Source bytes:

11697.

DEPENDENCY

DG-1R-01 frozen harness Git blob:

e053bf7f1088c5c8751d96afbd394dfa19f8a07c.

DG-1R-01 source SHA-256:

f1c97e345f83bc6a12efa6d9aa72a4a8309c300a4d3f044ebccfdf80e473f483.

LOCAL PRECHECK

P1 and P2 execution copies:
Git blob identity:

PASS.

DG-1R-02:
Python compile:

PASS.

No:
DG-1R-02:
experimental world
was:
executed
before:
this freeze.

FROZEN RECURRENCE

R:

8.

L_d:

16.

I:

4.

One:
fixed:
mapped position
inside:
each:
16-cell:
mapping compartment.

OVERWRITE:

state[mapped]
=
u_t.

XOR CONTROL:

if:
u_t == 1:

state[mapped]
XOR=
1.

if:
u_t == 0:

no:
input-state:
change.

All other:
rule,
feature,
task,
readout,
and:
evaluation:
semantics
remain:
paired.

FROZEN WORLD FAMILY

20260926020000..20260926020007.

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


FINAL DG-1R-02 NON-EVIDENCE PILOT CLOSURE — RECURRENT OVERWRITE / RANDOM-MAPPING FIDELITY

DATE:
2026-09-20.

STATUS:
COMPLETE /
NEGATIVE LONG-MEMORY RECOVERY /
POSITIVE IMMEDIATE-INPUT CAPTURE EFFECT /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

79d4da0f5585054debfdd873181d3e7463872c294a9dcf61e22e434c7c65ea1b.

CANONICAL OUTPUT

RUN 1 SHA-256:

e03b1d428550a7469812cc7ec3086e66c5e61202ee8290ef392bc42253652064.

RUN 2 SHA-256:

e03b1d428550a7469812cc7ec3086e66c5e61202ee8290ef392bc42253652064.

Byte-identical:

PASS.

OVERWRITE RECOVERY SIGNAL

FALSE.

STRONG RECURRENCE SIGNAL

FALSE.

TEMPORAL SUBSTRATE CANDIDATES

NONE.

PRIMARY RESULT

Literature-style:
input overwrite

materially improves:

IMMEDIATE:
INPUT CAPTURE

for:
several:
rule families.

It does NOT:

restore:
D16 /
D32:
long memory

under:

width:
128.

R:
8.

L_d:
16.

I:
4.

OW90

D1 median:

1.0.

Paired:
OVERWRITE - XOR:
D1 median:

+0.49462890625.

However:

D8:

0.50390625.

D16:

0.5029296875.

D32:

0.50732421875.

Memory score:

0.5091145833333333.

Thus:

the:
mapped:
current input
can:
become:
perfectly:
linearly visible
in:
some worlds

without:
creating:
long:
temporal memory.

OW182

D1 median:

0.9052734375.

P10:

0.83212890625.

Paired:
D1 improvement:

+0.4013671875.

This is:
a:
more:
world-robust:
immediate-input:
signal
than:
OW90.

But:

D16:

0.49462890625.

D32:

0.4833984375.

Memory score:

0.49609375.

OW_MIXED5

D1 median:

0.91943359375.

P10:

0.858984375.

Paired:
D1 improvement:

+0.1669921875.

D4:

0.5693359375.

D8:

0.484375.

D16:

0.50244140625.

D32:

0.50341796875.

Thus:

heterogeneous:
overwrite recurrence

extends:
the:
short-memory:
signal
slightly:
beyond:
one step,

but:
not:
to:
the:
long-memory:
targets.

OW22

D1:

0.57568359375.

D16:

0.50634765625.

D32:

0.49609375.

No:
long-memory:
recovery.

OW150

D1:

0.517578125.

D16:

0.50244140625.

D32:

0.49951171875.

No:
long-memory:
recovery.

RULE-90 NONLINEAR SIGNAL

OW90:

XOR3_11 median:

1.0.

But:

P10:
for:
D1
and:
the:
overall:
nonlinear family
shows:
substantial:
world dependence.

OW90 nonlinear score:

0.6740991260850427.

It still fails:
NONLINEAR_CAPABLE

because:

PARITY5:

0.48876953125.

MOTIF2_12:

0.5555442055471458.

Only:
one:
of:
the:
three:
nonlinear tasks

clears:
0.60.

XR90:

XOR3_11 median:

1.0.

P10:

0.8523437500000001.

Thus:

Rule 90's:
XOR feature

is:
not:
an:
overwrite-specific:
effect.

It is:
consistent
with:
Rule 90's:
additive /
XOR:
dynamics.

DYNAMIC BALANCE

OW90:

DYNAMICALLY_BALANCED:
PASS.

Entropy:

0.8509753637813233.

h16 perturbation:

0.015625.

OW150:

PASS.

OW182:

PASS.

OW22:

PASS.

OW_MIXED5:

FAILS:
the:
h16:
perturbation floor

with:
median:

0.0078125.

Thus:

overwrite:
can:
move:
several:
single-rule:
reservoirs
into:
the:
frozen:
dynamic-balance:
window,

but:
this:
still:
does not:
yield:
long memory.

RECURRENCE EFFECT

Overwrite versus:
paired XOR

produces:
large:
D1 gains
for:

Rule 90:
+0.49462890625.

Rule 182:
+0.4013671875.

MIXED5:
+0.1669921875.

Rule 22:
+0.05126953125.

Rule 150:
+0.0185546875.

But:

paired:
D16 /
D32:
deltas

remain:
near:
zero
and:
inconsistent.

Therefore:

OVERWRITE
corrects:
input observability

but:

does NOT:
solve:
the:
memory-decay:
mechanism.

TECHNICAL INTERPRETATION

DG-1R-02 answers:
an:
important:
methodological concern.

DG-1R-01's:
failure

was NOT:
simply:
caused
by:
using:
XOR
instead of:
the:
literature-style:
overwrite recurrence.

Overwrite:

does:
matter.

It:
greatly improves:
current-input:
capture.

But:

the:
128-cell:
single-state:
reservoir

still:
loses:
specific:
input identity

well before:
D16 /
D32.

The:
next:
research axis
therefore:
should NOT:
be:
another:
minor:
input-update:
change.

The:
evidence now points to:

TEMPORAL:
STRUCTURE.

Specifically:

- multiple:
  timescales;
- layered:
  reservoirs;
- slower:
  state evolution;
- recurrent:
  hierarchy.

This also aligns:
with:
Nichele / Molund's:
reported:
improvement
from:
a:
second:
layered:
CA reservoir.

NEXT JUSTIFIED EXPERIMENT

DG-1R-03 —
BOUNDED:
MULTI-TIMESCALE:
CELLULAR MEMORY AUDIT.

Keep:

total:
persistent:
cell budget:

128.

Compare:

1.
OW_MIXED5-I4:
single-timescale:
reference.

2.
SLOW-MIXED:
same:
128 cells

but:
slower:
internal:
evolution.

3.
PARALLEL-FAST/SLOW:

split:
the:
128 cells
between:
fast:
and:
slow:
reservoir lanes.

4.
PARALLEL-3-TIMESCALE:

fast /
medium /
slow:
lanes

under:
the:
same:
total:
cell budget.

5.
HETEROGENEOUS-TIMESCALE:

use:
different:
rule families
in:
fast /
slow:
lanes.

Primary question:

can:
slower:
or:
hierarchical:
cellular:
state

retain:
D8 /
D16 /
D32:
information

while:
preserving:
the:
useful:
nonlinear:
feature generation
seen:
in:
Rule 90
and:
the:
short-memory:
capture
seen:
in:
overwrite:
MIXED5 /
Rule 182?

PLAIN-SPEAK SUMMARY

What did we change?

The first:
ReCA test
flipped:
mapped cells
when:
the:
input was:
1

and:
did nothing
when:
the:
input was:
0.

The:
published:
recurrent:
ReCA design
instead:
writes:
the:
new:
input value
onto:
the:
old:
state.

So:
we tested:
that:
properly.

What happened?

It:
made:
the:
current:
input
much easier
to:
see.

For:
some:
rules,
the:
previous:
immediate:
bit
became:
very:
easy
to:
recover.

But:

the:
older:
history
still:
disappeared.

By:
16
or:
32:
steps,

the:
reservoirs
were:
basically:
guessing.

Did it work?

It fixed:
one:
part
of:
our:
implementation:

INPUT CAPTURE.

It did NOT:
fix:

LONG MEMORY.

What did we learn?

The:
problem
is now:
much less likely
to be:
a:
simple:
input-mapping:
mistake.

The:
cellular state
is:
evolving:
too:
quickly
or:
too:
uniformly

to:
hold:
specific:
older:
information.

What should we try next?

Give:
different:
parts
of:
the:
cell system

different:
speeds.

Let:
some:
cells
mix:
quickly

and:
some:
change:
slowly.

Keep:
the:
same:
total:
128-cell:
budget.

Then:
see:
whether:
the:
slow:
cells
can:
protect:
old:
information

while:
the:
fast:
cells
still:
create:
useful:
nonlinear:
features.

canonical_scientific_execution = false.
stab18_r1_touched = false.
