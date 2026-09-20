TITLE: DG-1R-05 — Local Damage Containment / Counterfactual Recovery Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE SELF-REPAIR PILOT
TRACK: DG-1R / SOFTWARE CELLS / LOCAL HOMEOSTASIS / DAMAGE RECOVERY
BRANCH: dg1a-ar
PARENT: DG-1R-04
PARENT_CLOSURE: cc980deb4a1ec87d3e405de52162e97632620314

PURPOSE

DG-1R-04 established:

- one-bit software nanites do NOT recover arbitrary D16 / D32 delay memory;
- H6 nanites can maintain substantially longer-lived local controller state;
- bounded REPAIR nanites perform many local corrections while preserving dynamic activity;
- aggressive DAMP nanites over-stabilize the organism.

Therefore:

the next question is NOT:

CAN:
NANITES:
ACT:
LIKE:
A:
HISTORY:
BUFFER?

It is:

CAN:
NANITES:
CONTAIN:
LOCAL:
DAMAGE

AND:

PULL:
A:
DAMAGED:
ORGANISM

BACK:
TOWARD:

THE:
COUNTERFACTUAL:
TRAJECTORY

IT:
WOULD:
HAVE:
FOLLOWED

IF:
THE:
DAMAGE:
HAD:
NEVER:
OCCURRED?

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

ORGANISM FAMILY

Exact frozen DG-1R-04 cellular mechanics.

Methods:

PRIMARY:
- SLOW128_MIXED1;
- N16_H5;
- N16_H6;
- N16_H6_REPAIR.

NEGATIVE / OVERSTABILIZED CONTROL:
- N16_H6_DAMP.

All methods:

128 persistent bits.

Same:
world-specific:
input stream.

Same:
world-specific:
MIXED5 worker rule assignment.

Same:
world-specific:
nanite-safe:
8-position:
input mapping.

Nanite methods:

112 worker bits
+
16 nanite controller bits.

No:
hidden:
state.

No:
task labels.

No:
targets.

No:
external:
repair memory.

PRE-DAMAGE DEVELOPMENT

Input:

u_t ~ Bernoulli(0.5).

Initial state:

all zero.

Each method evolves:

under:
its:
frozen:
DG-1R-04:
mechanics

for:

1024:
external:
input steps.

DAMAGE TIME

After:

processing:
input index:
1023

and:
completing:
that:
external:
step,

freeze:

the:
undamaged:
reference state.

Before:

processing:
input index:
1024,

create:

a:
damaged:
clone.

The:
reference
and:
damaged:
clone

then receive:

identical:
future:
inputs:

u_1024
through:
u_1055.

POST-DAMAGE HORIZON

32:
external:
steps.

Measure:

after:
horizons:

1,
4,
8,
16,
32.

LESION BLOCK SELECTION

The:
128-cell:
organism

contains:

16:
8-cell:
nanite blocks.

Each:
16-cell:
input compartment

contains:
two:
8-cell:
nanite blocks

but:

only:
one:
mapped:
input position.

Therefore:

for:
each:
16-cell:
input compartment,

exactly:
one:
8-cell:
nanite block

contains:
the:
mapped:
input site

and:
one:
sibling:
block
does not.

Define:

UNMAPPED SIBLING BLOCK

as:

the:
8-cell:
block
inside:
that:
16-cell:
compartment

that:
does NOT:
contain:
the:
mapped:
input:
position.

Select:

four:
lesion blocks

from:
input compartments:

0,
2,
4,
6.

Thus:

lesions:

- are:
  spatially:
  distributed;
- never:
  contain:
  an:
  input-mapped:
  worker;
- are:
  identical:
  across:
  methods
  inside:
  one world.

LESION SIZES

Within:
each:
selected:
unmapped:
8-cell:
block,

the:
seven:
worker positions

are:

offsets:
0..6.

SMALL3 lesion:

flip:
worker offsets:

2,
3,
4.

LARGE5 lesion:

flip:
worker offsets:

1,
2,
3,
4,
5.

Do NOT:
flip:
the:
nanite:
controller bit.

Thus:

per world:

4:
lesion locations

x:

2:
lesion sizes

=

8:
damage scenarios
per:
method.

DAMAGE OPERATION

At:
damage time:

for:
the:
damaged clone only:

state[lesion_workers]
XOR=
1.

Reference clone:

unchanged.

No:
other:
state
is:
modified.

COUNTERFACTUAL REFERENCE

For:
each:
method /
world /
damage scenario:

REFERENCE:

the:
undamaged:
state
continued:
under:
identical:
future:
input.

DAMAGED:

the:
lesioned:
state
continued:
under:
identical:
future:
input.

Therefore:

the:
reference trajectory

is:
the:
counterfactual:

WHAT:
THIS:
SAME:
ORGANISM

WOULD:
HAVE:
DONE

WITHOUT:
THE:
LESION.

PRIMARY METRICS

At:
horizons:
1,
4,
8,
16,
32:

WHOLE_STATE_DIVERGENCE

Hamming(
damaged,
reference
)
/
128.

LESION_DIVERGENCE

fraction:
of:
original:
lesion:
worker positions

where:

damaged
!=
reference.

LESION_RECOVERY

1
-
LESION_DIVERGENCE.

OUTSIDE_LESION_DIVERGENCE

Hamming:
difference
restricted:
to:
all:
persistent:
bits
outside:
the:
original:
lesion:

/
(
128
-
lesion_size
).

DAMAGE_SPREAD_COUNT

number:
of:
differing:
bits
outside:
the:
original:
lesion.

FULL_RECOVERY

TRUE
if:

damaged:
persistent:
128-bit:
state

equals:

reference:
persistent:
128-bit:
state.

EXCESS_DIVERGENCE_AREA

For:
each:
scenario:

sum:
WHOLE_STATE_DIVERGENCE

over:
all:
32:
post-damage:
external:
steps.

This is:

discrete:
divergence:
area-under-curve.

LOWER:
is:
better.

RECOVERY TIME

First:
post-damage:
external:
step

at:
which:

FULL_RECOVERY
becomes:
TRUE

and:

remains:
TRUE

through:
step:
32.

If:
never:

NOT_RECOVERED.

INTERVENTION TELEMETRY

For:
nanite methods:

start:
fresh:
post-damage:
telemetry

for:
both:

reference
and:
damaged:
clones.

Report:

DAMAGED minus REFERENCE

for:

- nanite bit changes;
- DAMP suppressed worker transitions;
- REPAIR attempts;
- REPAIR state changes.

This asks:

does:
damage

cause:
extra:
controller:
activity

relative:
to:
the:
organism's:
normal:
undamaged:
homeostasis?

NO-DAMAGE DETERMINISM CONTROL

For:
each:
method /
world:

create:

two:
identical:
undamaged:
clones

at:
the:
damage:
time.

Continue:

both:
for:
32:
steps

under:
identical:
future:
input.

Required:

maximum:
whole-state:
divergence

=
0.

If:
any:
method /
world
fails:

DG-1R-05
is:
MECHANICALLY INVALID.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260926050000
through:
20260926050007.

No:
prior:
DG-1R:
seed reuse.

SUMMARY LEVELS

Report:

per:

method /
lesion size

aggregated across:

8 worlds
x
4 lesion locations

=
32:
scenarios.

Also report:

combined:
64-scenario:
summary

per:
method.

For:
WHOLE_STATE_DIVERGENCE,
LESION_RECOVERY,
OUTSIDE_LESION_DIVERGENCE:

report:

median
and:
P90
where:
higher:
is:
worse

except:

LESION_RECOVERY:

report:
median
and:
P10.

For:
EXCESS_DIVERGENCE_AREA:

report:

median
and:
P90.

For:
FULL_RECOVERY:

report:

rate.

For:
RECOVERY TIME:

report:

median
among:
recovered:
scenarios

plus:

recovered:
scenario:
count.

FROZEN PRIMARY REFERENCE

SLOW128_MIXED1.

PRIMARY NANITE CANDIDATES

N16_H5.
N16_H6.
N16_H6_REPAIR.

N16_H6_DAMP:

negative:
overstabilized:
control only.

CONTAINMENT SIGNAL

A:
primary:
nanite method

has:

CONTAINMENT_SIGNAL

if:

for:
combined:
lesion scenarios:

1.
median:
EXCESS_DIVERGENCE_AREA

is:
at least:
25%:
lower

than:
SLOW128_MIXED1;

AND:

2.
median:
OUTSIDE_LESION_DIVERGENCE
at:
h16

is:
at least:
25%:
lower

than:
SLOW128_MIXED1;

AND:

3.
median:
OUTSIDE_LESION_DIVERGENCE
at:
h32

does NOT:
exceed:
SLOW128_MIXED1.

REPAIR SIGNAL

A:
primary:
nanite method

has:

REPAIR_SIGNAL

if:

for:
combined:
lesion scenarios:

1.
median:
LESION_RECOVERY
at:
h16

is:
at least:
0.10:
higher

than:
SLOW128_MIXED1;

OR:

median:
LESION_RECOVERY
at:
h32

is:
at least:
0.10:
higher;

AND:

2.
its:
median:
EXCESS_DIVERGENCE_AREA

does NOT:
exceed:
SLOW128_MIXED1.

STRONG COUNTERFACTUAL RECOVERY

A:
primary:
nanite method

has:

STRONG_COUNTERFACTUAL_RECOVERY

if:

1.
median:
WHOLE_STATE_DIVERGENCE
at:
h16
<=0.05;

2.
median:
WHOLE_STATE_DIVERGENCE
at:
h32
<=0.03;

3.
median:
LESION_RECOVERY
at:
h32
>=0.80;

4.
median:
OUTSIDE_LESION_DIVERGENCE
at:
h32
<=0.02;

5.
FULL_RECOVERY rate
>=0.25;

6.
median:
EXCESS_DIVERGENCE_AREA

is:
at least:
25% lower
than:
SLOW128_MIXED1.

HOMEOSTATIC REPAIR CANDIDATE

A:
primary:
nanite method

is:

HOMEOSTATIC_REPAIR_CANDIDATE

if:

CONTAINMENT_SIGNAL
is:
TRUE

AND:

REPAIR_SIGNAL
is:
TRUE.

FULL SELF-REPAIR SIGNAL

TRUE
if:

at least:
one:
primary:
nanite method

is:

HOMEOSTATIC_REPAIR_CANDIDATE

AND:

has:
STRONG_COUNTERFACTUAL_RECOVERY.

OVERSTABILIZATION CONTROL INTERPRETATION

N16_H6_DAMP

is:
not:
eligible
for:

HOMEOSTATIC_REPAIR_CANDIDATE.

It is:
retained
to:
measure:

whether:
severe:
stabilization

can:
artificially:
reduce:
damage spread

while:
destroying:
healthy:
dynamics.

Its:
result
must:
be:
reported

but:
cannot:
be:
selected
as:
the:
primary:
repair architecture.

IMPORTANT

This experiment:

does NOT:
ask:
whether:
the:
damaged:
organism

returns:
to:
some:
generic:
stable:
state.

It asks:

whether:
the:
damaged:
organism

returns:
toward:

ITS:
OWN:
UNDAMAGED:
COUNTERFACTUAL:
TRAJECTORY.

That distinction:

separates:

TRUE:
HOMEOSTATIC:
REPAIR

from:

mere:
FREEZING
or:
ATTRACTOR:
COLLAPSE.

NO POST-RUN TUNING

After:
the:
first:
DG-1R-05:
primary:
damage scenario,

do not alter:

- damage time;
- post-damage horizon;
- selected input compartments;
- unmapped sibling rule;
- SMALL3 lesion;
- LARGE5 lesion;
- damage operation;
- primary metrics;
- intervention telemetry;
- classifications;
- thresholds;
- world family;
- parent organism mechanics.

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
FULL_SELF_REPAIR_SIGNAL:

proceed to:

DG-1R-06 —
ADVERSARIAL /
REPEATED:
DAMAGE:
AND:
RECOVERY
under:
bounded:
nanite:
resource pressure.

If:
HOMEOSTATIC_REPAIR_CANDIDATE
without:
strong:
counterfactual recovery:

test:

- lesion:
  geometry;
- repair:
  radius;
- nanite:
  density;
- bounded:
  developmental:
  migration;

under:
the:
same:
128-bit:
state budget.

If:
CONTAINMENT_SIGNAL
only:

nanites:
can:
prevent:
damage spread

but:
cannot:
reconstruct:
the:
lost:
local:
trajectory.

Then:
investigate:

redundant:
developmental:
encoding
plus:
local:
repair.

If:
all:
primary:
nanite methods
are:
negative:

deprioritize:
nanites
as:
state-reconstruction:
agents

but:
retain:
their:
demonstrated:
stability-control:
role

for:
developmental:
regulation.

PLAIN-SPEAK PRE-REGISTERED QUESTION

We are:
not:
asking:
the:
nanites
to:
remember:
an:
old:
random:
bit
anymore.

We are:
asking:
them
to:
do:
something
much closer
to:
repair.

We grow:
two:
identical:
software organisms.

Then:
we damage:
one
by:
flipping:
a:
small:
group
of:
ordinary:
cells.

The:
other:
organism
is:
left:
untouched.

After that:

both:
see:
the:
same:
future:
inputs.

The:
untouched:
one
shows us:

where:
the:
damaged:
organism
would:
have:
gone

if:
the:
damage
had:
never:
happened.

Then:
we measure:

does:
the:
damaged:
organism
move:
back
toward:
that:
exact:
trajectory?

Do:
the:
nanites
stop:
the:
damage
from:
spreading?

Do:
they:
repair:
the:
cells
that:
were:
hit?

Do:
they:
actually:
restore:
the:
right:
state,

rather than:
simply:
freezing:
everything?

That:
is:
the:
first:
clean:
test
of:
whether:
the:
software-nanite:
idea
can:
serve:
Yggdrasil's:
self-healing:
goal.

canonical_scientific_execution = false.
stab18_r1_touched = false.
