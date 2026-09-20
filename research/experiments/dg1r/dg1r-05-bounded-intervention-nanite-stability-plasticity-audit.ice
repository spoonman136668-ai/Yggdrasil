TITLE: DG-1R-05 — Bounded-Intervention Software-Nanite Stability / Plasticity Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE ACTIVE-STABILIZATION PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL REGULATION / STABILITY-PLASTICITY
BRANCH: dg1a-ar
PARENT: DG-1R-04

PURPOSE

DG-1R-04 established:

- programmed local stabilizers have strong causal control over reservoir dynamics;
- unrestricted threshold veto suppresses worker-state change by roughly an order of magnitude;
- that suppression collapses feature rank and entropy;
- D16 / D32 memory does not improve.

Therefore:

the failure is NOT:

"nanites cannot stabilize."

They can.

The failure is:

THEY:
STABILIZE:
TOO BROADLY.

DG-1R-05 asks:

CAN:
ACTIVE:
LOCAL:
STABILIZATION

HELP:
MEMORY

IF:

NANITE:
INTERVENTION
IS:
STRICTLY:
BOUNDED

SO:
THE:
RESERVOIR
MUST:
REMAIN:
PLASTIC?

BOUNDARY

Synthetic software-only experiment.

"Nanite" means:

programmed:
software:
stabilizer controller.

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

FIXED TOTAL STATE

All ReCA methods:

128:
persistent:
binary:
bits.

Nanite / inert methods:

112:
worker:
CA cells.

16:
controller:
cells.

No:
hidden:
input register.

No:
external:
timer.

No:
extra:
persistent:
state.

WORKER TOPOLOGY

Exact:
DG-1R-04:

112:
periodic:
worker ring.

16:
contiguous:
7-worker:
sectors.

Controller j:

owns:
workers:

7*j
through:
7*j+6.

INPUT

Exact:
DG-1R-04:

8:
fixed:
mapped:
worker positions.

One:
position:
inside:
each:
14-worker:
input compartment.

All:
ReCA methods
inside:
one world

share:
the:
same:
8:
input positions.

Input recurrence:

OVERWRITE.

WORKER RULE

MIXED5:

90,
150,
110,
22,
30

fixed:
per:
worker
for:
the:
world.

Worker update clock
for:
nanite methods:

FAST4:
microticks:
1,
2,
3,
4.

READOUT

After:
each:
of:
4:
microticks

record:

112:
worker bits

+
16:
controller bits.

Feature dimension:

512.

CONTROL METHODS

1.
INERT112_16_FAST4

112:
workers.

16:
controller bits:
fixed:
0.

No:
stabilization.

Primary:
capacity /
topology:
control.

2.
SLOW128_MIXED1

128:
ordinary:
workers.

No:
controllers.

Passive:
slowing:
reference.

BOUNDED NANITE FAMILY A — REFRACTORY

3.
REFRACTORY112_16_FAST4_T50

Local:
flip threshold:

0.50.

Controller state:

0:
eligible:
to:
veto.

1:
refractory:
must:
allow:
the:
next:
eligible:
worker transition.

At:
each:
worker:
microtick:

for:
each:
sector:

calculate:
proposed:
flip fraction.

If:
controller == 1:

FORCE:
commit:
the:
proposed:
worker transition

regardless:
of:
flip fraction.

Then:

controller
=
0.

Else:

if:
flip_fraction
>
0.50:

VETO:
that:
sector.

Controller:

=
1.

Else:

COMMIT:
transition.

Controller:

=
0.

Thus:

a:
sector
cannot:
veto:
two:
consecutive:
eligible:
worker updates.

No:
extra:
timer.

The:
existing:
one-bit:
controller state
is:
the:
refractory flag.

4.
REFRACTORY112_16_FAST4_T35

Exact:
same:
mechanism

with:
threshold:

0.35.

Purpose:

test:
whether:
aggressive:
detection
becomes:
usable
when:
forced:
release
prevents:
persistent:
freezing.

BOUNDED NANITE FAMILY B — GLOBAL VETO BUDGET

5.
BUDGET112_16_FAST4_K1

At:
each:
worker:
microtick:

compute:
proposed:
flip count
for:
all:
16:
sectors.

Among:
sectors
with:
at least:
one:
proposed:
worker flip:

rank:
by:
flip fraction:
descending.

Tie:

lower:
sector index
first.

Veto:

ONLY:
the:
single:
most:
volatile:
eligible:
sector.

K=1.

Maximum:
sector-veto:
fraction:

1 / 16
=
6.25%
per:
worker:
microtick.

Controller bit:

1
for:
the:
vetoed:
sector.

0:
for:
all:
others.

No:
controller:
refractory state
is:
used
for:
budget methods.

6.
BUDGET112_16_FAST4_K2

Exact:
same:

K=2.

Maximum:
sector-veto:
fraction:

12.5%
per:
worker:
microtick.

PURPOSE OF THE TWO FAMILIES

REFRACTORY:

limits:
temporal:
persistence
of:
one:
local:
brake.

BUDGET:

limits:
spatial:
extent
of:
stabilization
at:
one:
time.

Both:

force:
continued:
state evolution.

Neither:

stores:
the:
input
or:
target:
memory
directly.

BASELINES

RAW32.

RANDOM512.

Exact:
DG-1R:
definitions.

SEQUENCE

4096:
iid:
binary:
steps.

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

READOUT

Linear:
ridge.

Alpha:

1e-3.

Bias:

included:
unregularized.

Threshold:

0.5.

MOTIF2_12:

balanced accuracy.

Other tasks:

accuracy.

PERTURBATION

Exact:
DG-1R-04:

after:
external step:
512:

clone:
persistent state.

Flip:
worker bit:
98.

Continue:
identical:
future:
input
under:
the:
method's:
frozen:
controller rule.

Measure:
normalized:
Hamming distance

at:
external horizons:

1,
4,
8,
16.

STABILIZER TELEMETRY

For:
every:
112+16:
method:

report:

- veto fraction;
- proposed worker-change fraction;
- realized worker-change fraction.

For:
REFRACTORY:

also report:

- forced-release fraction:
  fraction:
  of:
  sector decisions
  where:
  controller=1
  caused:
  mandatory:
  commit.

For:
BUDGET:

also report:

- mean:
  vetoes:
  per:
  active:
  microtick;
- maximum:
  vetoes:
  per:
  active:
  microtick.

RESOURCE ACCOUNTING

Persistent:

128 bits
all ReCA methods.

Readout:

512 bits.

INERT / REFRACTORY / BUDGET:

448:
worker:
proposed:
CA cell updates
per:
external:
input.

REFRACTORY:

64:
sector:
controller:
decisions
per:
external:
input.

BUDGET:

64:
sector:
volatility:
scores
+
4:
top-K:
arbitrations
per:
external:
input.

Reservoir:
trainable parameters:

0.

Readout:

513:
trainable scalars
per:
task.

WORLD FAMILY

8:
disjoint:
worlds.

Seeds:

20260926050000
through:
20260926050007.

No:
DG-1R-01 /
02 /
03 /
04:
seed reuse.

ABSOLUTE CLASSIFICATION

Exact:
prior:
DG-1R gates.

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
with:
median:
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
three.

PRIMARY ACTIVE-STABILIZATION TEST

Primary reference:

INERT112_16_FAST4.

For:
each:
bounded nanite method

report:

paired:
method - INERT

for:

D1,
D4,
D8,
D16,
D32,
memory score,
nonlinear score.

BOUNDED_STABILIZATION_SIGNAL

TRUE
if:

at least:
one:
bounded:
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
INERT

AND:

its:
median:
nonlinear score

is:
no more than:
0.05
below:
INERT.

PLASTICITY_RECOVERY

TRUE
for:
a:
bounded:
nanite method
if:

median:
state entropy
>=0.20

AND:

median:
feature-rank fraction
>=0.15.

Reason:

DG-1R-04:
threshold-veto:
methods
collapsed:

entropy
to:
approximately:
0.08-0.12

and:
rank fraction
to:
approximately:
0.005-0.031.

PASSIVE_COMPARISON_SIGNAL

TRUE
if:

at least:
one:
bounded:
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

median:
nonlinear score
is:
no more than:
0.05
below:
SLOW128.

NANITE_MEMORY_RECOVERY

TRUE
if:

at least:
one:
bounded:
nanite method

is:
MEMORY_CAPABLE

while:

INERT112_16_FAST4

and:

SLOW128_MIXED1

are:
not.

INTERPRETATION

If:

PLASTICITY_RECOVERY
passes

but:
BOUNDED_STABILIZATION_SIGNAL
fails:

bounded:
braking
fixes:
the:
DG-1R-04:
freezing problem

but:

volatility:
alone
does not:
identify:
memory-relevant:
state.

Then:

the:
next:
nanite family
should:
use:

TRACE-TARGETED:
ANCHOR /
REFRESH /
REPAIR

rather than:
generic:
volatility:
suppression.

If:

BOUNDED_STABILIZATION_SIGNAL
passes:

active:
local:
regulation
adds:
long-memory:
value
without:
global:
freezing.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05:
primary world,

do not alter:

- 112 / 16 split;
- worker sectors;
- input mapping;
- worker rules;
- clocks;
- refractory logic;
- thresholds;
- K budgets;
- tie rule;
- readout;
- tasks;
- perturbation;
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

The:
first:
nanites
were:
too:
powerful.

They:
kept:
slamming:
the:
brakes

until:
the:
cell system
barely:
changed.

This test
forces:
them
to:
back off.

One:
version
says:

"after:
you:
block:
one:
change,
you:
must:
allow:
the:
next:
one."

The:
other
says:

"only:
one
or:
two:
neighborhoods
in:
the:
whole:
system
may:
be:
protected
at:
a:
time."

If:
memory:
improves
while:
the:
reservoir
stays:
active,

then:
we:
have:
evidence
that:
controlled:
software-nanite:
stabilization
can:
help.

If:
the:
reservoir
stays:
healthy
but:
D16 /
D32
still:
do not:
improve,

then:
the:
nanites
need:
to:
protect:
the:
right:
information,

not:
just:
the:
most:
volatile:
information.

canonical_scientific_execution = false.
stab18_r1_touched = false.
