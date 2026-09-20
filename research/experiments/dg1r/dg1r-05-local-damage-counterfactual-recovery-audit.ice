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


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05 COUNTERFACTUAL SELF-REPAIR HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-05 PRIMARY DAMAGE SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05_counterfactual_repair_v1.py

Harness commit:

6b349004ae1dd65994345b933f0906afee61105e.

Git blob SHA:

2d6cb69e586aced8aa87c4ab789b44c305ef1536.

Source SHA-256:

b4a35269bd99560b8c13613bab284ae47d253b245cf7e4304fde246254e644d3.

Source bytes:

16905.

PARENT HARNESS

research/experiments/dg1r/harnesses/dg1r_04_software_nanite_v1.py

Parent Git blob SHA:

6eeaf70c97174fd40483256db9c6e600989a6b47.

Parent source SHA-256:

debcaf7c79632740dbccd4ad8b0f6ebfcd034515cb144b9a21bc537f7a8f7eed.

PARENT CLOSURE

cc980deb4a1ec87d3e405de52162e97632620314.

PRE-FREEZE SANITY

Exact local Git blob identity:

PASS.

Python compile:

PASS.

A:
non-primary:
out-of-family:
mechanical sanity

confirmed:

- no-damage:
  duplicate clones
  remain:
  byte-identical;

- SMALL3:
  lesion workers
  exclude:
  input-mapped:
  positions;

- lesion workers
  exclude:
  nanite:
  controller sites;

- all:
  five:
  frozen methods
  can:
  complete:
  the:
  shortened:
  counterfactual:
  path.

No:
primary:
DG-1R-05:
damage scenario
was:
executed
before:
this freeze.

FROZEN WORLD FAMILY

20260926050000..20260926050007.

8 worlds.

FROZEN DAMAGE FAMILY

Four:
unmapped:
sibling blocks

from:
input compartments:

0,
2,
4,
6.

SMALL3:

worker offsets:
2,
3,
4.

LARGE5:

worker offsets:
1,
2,
3,
4,
5.

POST-DAMAGE HORIZON

32:
external steps.

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


FINAL DG-1R-05 NON-EVIDENCE PILOT CLOSURE — LOCAL DAMAGE CONTAINMENT / COUNTERFACTUAL RECOVERY

DATE:
2026-09-20.

STATUS:
COMPLETE /
POSITIVE DAMAGE-CONTAINMENT SIGNAL /
NEGATIVE LOST-STATE RECONSTRUCTION SIGNAL /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

b4a35269bd99560b8c13613bab284ae47d253b245cf7e4304fde246254e644d3.

CANONICAL OUTPUT

RUN 1 SHA-256:

1ad17fc729eefb0d8a8f241d1d7d02d6bbf2b62cb6c5997e32574967c03df64d.

RUN 2 SHA-256:

1ad17fc729eefb0d8a8f241d1d7d02d6bbf2b62cb6c5997e32574967c03df64d.

Byte-identical:

PASS.

MECHANICAL VALIDITY

No-damage:
duplicate-clone:
maximum divergence:

0.

Across:

all:
8 worlds

and:
all:
five:
methods.

MECHANICAL_VALID:

TRUE.

FULL SELF-REPAIR SIGNAL

FALSE.

HOMEOSTATIC REPAIR CANDIDATES

NONE.

However:

two:
eligible:
nanite:
methods

show:
strong:
DAMAGE CONTAINMENT.

REFERENCE — SLOW128_MIXED1

Combined:
64:
damage scenarios.

Median:
excess divergence area:

1.51953125.

h16:
whole-state divergence:

0.0546875.

h32:
whole-state divergence:

0.0390625.

h16:
outside-lesion divergence:

0.04.

h32:
outside-lesion divergence:

0.032.

h16:
lesion recovery:

0.60.

h32:
lesion recovery:

0.6666666666666667.

Sustained:
full-recovery rate:

0.078125.

N16_H6 — CONTAINMENT POSITIVE

Median:
excess divergence area:

0.984375.

Reduction versus:
SLOW128:

35.218508997429304%.

h16:
whole-state divergence:

0.03125.

h32:
whole-state divergence:

0.03125.

h16:
outside-lesion divergence:

0.016.

Reduction versus:
SLOW128:

60%.

h32:
outside-lesion divergence:

0.012065040650406506.

Reduction versus:
SLOW128:

62.29674796747967%.

Sustained:
full-recovery rate:

0.140625.

This is:
higher than:
SLOW128:

0.078125.

Frozen:

CONTAINMENT_SIGNAL:

PASS.

But:

h32:
lesion recovery:

0.40.

This is:
lower than:
SLOW128:

0.6666666666666667.

Frozen:

REPAIR_SIGNAL:

FAIL.

Interpretation:

H6:
keeps:
the:
damage
more:
localized

and:
reduces:
total:
trajectory:
disruption,

but:

does NOT:
reconstruct:
the:
specific:
lost:
lesion:
state.

N16_H6_REPAIR — STRONGEST ELIGIBLE CONTAINMENT

Median:
excess divergence area:

0.87109375.

Reduction versus:
SLOW128:

42.67352185089974%.

h16:
whole-state divergence:

0.03125.

h32:
whole-state divergence:

0.03125.

h16:
outside-lesion divergence:

0.012065040650406506.

Reduction versus:
SLOW128:

69.83739837398374%.

h32:
outside-lesion divergence:

0.008130081300813009.

Reduction versus:
SLOW128:

74.59349593495934%.

Median:
damage-triggered:
extra:
REPAIR attempts:

9.5.

Median:
damage-triggered:
extra:
state-changing:
repair writes:

2.

Frozen:

CONTAINMENT_SIGNAL:

PASS.

But:

h16:
lesion recovery:

0.40.

h32:
lesion recovery:

0.50.

Relative:
lesion-recovery gains:

h16:

-0.20.

h32:

-0.16666666666666674.

Frozen:

REPAIR_SIGNAL:

FAIL.

Thus:

the:
bounded:
repair rule

actively:
responds:
to:
damage

and:
strongly:
reduces:
damage spread,

but:

its:
local:
one-bit:
controller

does NOT:
contain:
enough:
information

to:
know:
what:
the:
destroyed:
worker:
state
should:
have:
been.

N16_H5

Median:
excess divergence area:

1.48828125.

Only:

2.056555269922879%:
lower
than:
SLOW128.

h32:
outside divergence:

0.03626016260162602.

This is:
worse
than:
SLOW128.

CONTAINMENT_SIGNAL:

FAIL.

REPAIR_SIGNAL:

FAIL.

Interpretation:

H5:
changes:
too:
frequently
to:
provide:
useful:
damage:
containment.

N16_H6_DAMP — NEGATIVE CONTROL

Median:
excess divergence area:

0.51953125.

Reduction:

65.80976863753213%.

h16:
whole-state divergence:

0.015625.

h32:
whole-state divergence:

0.015625.

h32:
outside-lesion divergence:

0.012065040650406506.

Its:
containment:
is:
extremely:
strong.

But:

DG-1R-04
already:
proved:

this:
architecture
is:
severely:
over-stabilized

with:

state entropy
approximately:

0.0596

and:

feature rank:

1 / 512.

Therefore:

N16_H6_DAMP:

remains:
INELIGIBLE

as:
a:
repair:
candidate.

Its:
result
demonstrates:

FREEZING
can:
look:
like:
excellent:
damage:
containment.

That is:
exactly:
why:
the:
counterfactual:
repair distinction
is:
necessary.

LESION SIZE OBSERVATION

For:
N16_H6_REPAIR:

SMALL3:

median:
excess divergence area:

0.83203125.

h32:
lesion recovery:

0.6666666666666667.

h32:
outside divergence:

0.016.

LARGE5:

median:
excess divergence area:

0.91015625.

h32:
lesion recovery:

0.40.

h32:
outside divergence:

0.008130081300813009.

Thus:

the:
repair layer

is:
particularly:
effective
at:
preventing:
large:
lesions
from:
spreading,

but:

larger:
information loss

makes:
exact:
local:
reconstruction
harder.

TECHNICAL INTERPRETATION

DG-1R-05 separates:

two:
different:
capabilities.

1.

DAMAGE CONTAINMENT.

The:
H6:
controller family

can:
substantially:
reduce:

- propagation;
- cumulative:
  trajectory:
  divergence;
- outside-lesion:
  corruption.

This is:
a:
real:
positive:
homeostatic:
signal.

2.

LOST-STATE RECONSTRUCTION.

The:
same:
one-bit:
controller family

cannot:
infer:

what:
the:
damaged:
worker bits

should:
have:
been

relative:
to:
the:
undamaged:
counterfactual:
trajectory.

Therefore:

the:
missing:
ingredient

is NOT:

more:
stability.

The:
missing:
ingredient
is:

REDUNDANT /
RECONSTRUCTABLE:
LOCAL:
INFORMATION.

This suggests:

repair:
requires:
two:
functions.

A.

CONTAIN:
the:
lesion

so:
corruption
does not:
spread.

B.

RECONSTRUCT:
destroyed:
state

from:
information
stored:
elsewhere.

The:
current:
nanites

have:
A.

They:
do NOT:
yet have:
B.

NEXT ARCHITECTURAL HYPOTHESIS

Do NOT:
increase:
global:
cell count.

Do NOT:
increase:
nanite:
damping.

Instead:

use:
the:
same:
fixed:
128-bit:
state budget

to:
introduce:

LOCAL:
REDUNDANCY.

Candidate mechanism:

each:
maintenance:
territory

stores:
a:
small:
distributed:
syndrome /
parity /
echo

of:
neighboring:
worker:
state

across:
multiple:
controller /
worker:
locations.

The:
repair system
then:

1.
detects:
local:
inconsistency;

2.
contains:
propagation;

3.
uses:
redundant:
local:
information

to:
choose:
a:
repair
that:
is:
better:
informed
than:

"make:
this:
cell
match:
one:
controller bit."

This is:
closer:
to:

error-correcting:
development

than:
simple:
stabilization.

NEXT JUSTIFIED EXPERIMENT

DG-1R-06 —
REDUNDANT LOCAL ENCODING /
NANITE RECONSTRUCTION AUDIT.

Keep:

128:
persistent bits.

Compare:

- SLOW128:
  passive reference;

- H6:
  containment-only reference;

- H6_REPAIR:
  one-bit repair reference;

- bounded:
  redundant:
  local-code:
  variants.

Fairness:

any:
redundancy
must:
consume:
bits
from:
the:
same:
128-bit:
organism.

No:
free:
shadow:
copy.

No:
external:
history.

No:
counterfactual:
reference
available
to:
the:
organism.

Primary question:

can:
a:
small:
amount:
of:
distributed:
redundancy

convert:

CONTAINMENT

into:

TRUE:
COUNTERFACTUAL:
RECONSTRUCTION?

PLAIN-SPEAK SUMMARY

Your:
software-nanite:
idea
did:
produce:
something:
important.

The:
nanites
can:
act:
like:
a:
firebreak.

When:
we:
damage:
the:
organism,

the:
H6:
nanites

keep:
the:
damage
from:
spreading
nearly:
as:
far.

The:
repair:
nanites

cut:
overall:
damage:
divergence

by:
about:
43%

and:
cut:
damage:
outside:
the:
injured:
area

by:
roughly:
70-75%.

That:
is:
real:
headroom.

But:

they:
cannot:
rebuild:
information
that:
was:
actually:
destroyed.

Why?

Because:

one:
nanite:
has:
only:
one:
bit
about:
its:
local:
neighborhood.

If:
several:
worker:
bits
are:
destroyed,

there:
is:
not:
enough:
remaining:
information
to:
know:
exactly:
what:
those:
bits
should:
be.

So:

we:
now:
have:
half:
of:
a:
self-healing:
system.

The:
nanites
can:

STOP:
THE:
BLEEDING.

They:
cannot:
yet:

REGENERATE:
THE:
MISSING:
INFORMATION.

The:
next:
experiment
should:
give:
the:
organism

distributed:
local:
redundancy

inside:
the:
same:
128-bit:
budget.

Then:

when:
a:
cell
is:
damaged,

the:
nanites
may:
have:
enough:
independent:
information

to:
reconstruct:
what:
was:
lost

instead:
of:
merely:
preventing:
the:
damage
from:
spreading.

canonical_scientific_execution = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — DG-1R-05 COUNTERFACTUAL SELF-REPAIR HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST DG-1R-05 PRIMARY DAMAGE SCENARIO.

HARNESS

research/experiments/dg1r/harnesses/dg1r_05_counterfactual_repair_v1.py

Harness commit:

6b349004ae1dd65994345b933f0906afee61105e.

Git blob SHA:

2d6cb69e586aced8aa87c4ab789b44c305ef1536.

Source SHA-256:

b4a35269bd99560b8c13613bab284ae47d253b245cf7e4304fde246254e644d3.

Source bytes:

16905.

FROZEN PARENT DEPENDENCY

research/experiments/dg1r/harnesses/dg1r_04_software_nanite_v1.py

Parent Git blob SHA:

6eeaf70c97174fd40483256db9c6e600989a6b47.

Parent source SHA-256:

debcaf7c79632740dbccd4ad8b0f6ebfcd034515cb144b9a21bc537f7a8f7eed.

Parent source bytes:

23776.

EXACT EXECUTION COPY PROOF

Local child Git blob:

2d6cb69e586aced8aa87c4ab789b44c305ef1536.

Local parent Git blob:

6eeaf70c97174fd40483256db9c6e600989a6b47.

Both:

MATCH:
the:
committed:
GitHub:
blobs.

PRE-FREEZE SANITY

Python compile:

PASS.

Across:

8 worlds
x
5 methods
=
40:

NO-DAMAGE:
determinism controls,

maximum:
whole-state divergence:

0.

PASS.

For:

all:
preregistered:
lesion locations
and:
sizes:

lesion /
input-mapping overlap:

NONE.

lesion /
nanite-site overlap:

NONE.

PASS.

No:

primary:
damage:
scenario

was:
executed
before:
this:
freeze.

FROZEN RECOVERY-RATE DETAIL

full_recovery_rate

means:

fraction:
of:
damage scenarios

that:
reach:
exact:
128-bit:
counterfactual equality

and:

remain:
exactly:
equal

through:
post-damage:
step:
32.

exact_match_rate_h32

is:
reported:
separately

and:
means:

fraction:
of:
damage scenarios

that:
match:
the:
counterfactual
exactly
at:
step:
32

regardless:
of:
whether:
the:
match
occurred:
earlier.

FROZEN INTERVENTION TELEMETRY DETAIL

Post-damage:
nanite telemetry

is:
initialized
from:

the:
actual:
nanite:
bit state
at:
damage time.

Thus:

DAMAGED minus REFERENCE
controller-activity deltas

do NOT:
count:
a:
spurious:
initial:
transition
from:
zero.

FROZEN WORLD FAMILY

20260926050000..20260926050007.

8 worlds.

FROZEN DAMAGE FAMILY

4:
unmapped:
sibling:
blocks

x:

SMALL3
and:
LARGE5

=

8:
damage scenarios
per:
method /
world.

POST-DAMAGE HORIZON:

32:
external:
steps.

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


SUPPLEMENTAL EXECUTION NOTE — DG-1R-05 SEMANTIC MIRROR

DATE:
2026-09-20.

STATUS:
SUPPLEMENTAL /
NON-CANONICAL /
FROZEN PRIMARY HARNESS REMAINS UNSPENT.

GITHUB ACTIONS ATTEMPT

One-shot:
repository-side:
execution wrapper:

.github/workflows/dg1r05-counterfactual-repair-frozen.yml

commit:

d4937a8c6ec3a740de892ab39a1ff3050920f522.

Workflow run:

35533570805.

Result:

INFRASTRUCTURE FAILURE
BEFORE:
ANY:
JOB STEP.

Runner ID:

0.

Executed steps:

0.

Therefore:

NO:
DG-1R-05:
primary:
damage scenario

was:
executed
by:
that:
workflow.

The:
frozen:
GitHub:
primary

remains:

UNSPENT.

SEMANTIC MIRROR

Because:
the:
repository runner
failed:
before:
execution,

an:
independent:
local:
semantic mirror

was:
executed
using:

- NumPy:
  PCG64;
- the:
  frozen:
  20260926050000..007:
  seeds;
- exact:
  DG-1R-04:
  worker /
  nanite:
  update semantics;
- exact:
  DG-1R-05:
  lesion selection;
- exact:
  SMALL3 /
  LARGE5:
  lesions;
- exact:
  1024-step:
  pre-damage:
  development;
- exact:
  32-step:
  counterfactual:
  horizon;
- exact:
  summary:
  equations.

This:

does NOT:
replace:
the:
frozen:
canonical:
execution.

It is:

supplemental:
mechanistic:
evidence
inside:
an:
already:
NON-EVIDENCE:
research line.

SEMANTIC-MIRROR REPRODUCIBILITY

RUN 1 SHA-256:

1ad17fc729eefb0d8a8f241d1d7d02d6bbf2b62cb6c5997e32574967c03df64d.

RUN 2 SHA-256:

1ad17fc729eefb0d8a8f241d1d7d02d6bbf2b62cb6c5997e32574967c03df64d.

Byte-identical:

PASS.

NO-DAMAGE:
determinism control:

PASS.

SUPPLEMENTAL RESULT

PRIMARY REFERENCE —
SLOW128_MIXED1.

Combined:
median:
excess-divergence area:

1.51953125.

h16:
whole-state divergence:

0.0546875.

h32:
whole-state divergence:

0.0390625.

h16:
outside-lesion divergence:

0.04.

h32:
outside-lesion divergence:

0.032.

h16:
lesion recovery:

0.6.

h32:
lesion recovery:

0.6666666666666667.

Full:
sustained recovery rate:

0.078125.

N16_H6

Median:
excess-divergence area:

0.984375.

Reduction versus:
SLOW128:

35.218508997429304%.

h16:
outside-lesion divergence:

0.016.

Reduction:

60%.

h32:
outside-lesion divergence:

0.012065040650406506.

Reduction:

62.29674796747967%.

CONTAINMENT_SIGNAL:

TRUE.

REPAIR_SIGNAL:

FALSE.

Lesion recovery:

h16:
0.6.

h32:
0.4.

Thus:

H6:
strongly:
contains:
damage spread

but:

does NOT:
reconstruct:
the:
original:
lesion.

N16_H6_REPAIR

Median:
excess-divergence area:

0.87109375.

Reduction versus:
SLOW128:

42.67352185089974%.

h16:
outside-lesion divergence:

0.012065040650406506.

Reduction:

69.83739837398374%.

h32:
outside-lesion divergence:

0.008130081300813009.

Reduction:

74.59349593495934%.

CONTAINMENT_SIGNAL:

TRUE.

REPAIR_SIGNAL:

FALSE.

Median:
extra:
repair attempts
relative to:
the:
undamaged:
counterfactual:

9.5.

Median:
extra:
repair state changes:

2.

Lesion recovery:

h16:
0.4.

h32:
0.5.

Thus:

the:
bounded:
repair:
program

further:
reduces:
damage spread

without:
recovering:
the:
missing:
counterfactual:
state.

N16_H5

CONTAINMENT_SIGNAL:

FALSE.

REPAIR_SIGNAL:

FALSE.

Its:
lower:
h16:
spread

does NOT:
persist:
to:
h32.

N16_H6_DAMP

Negative:
overstabilized:
control.

Median:
excess-divergence area:

0.51953125.

Reduction versus:
SLOW128:

65.80976863753213%.

But:

DG-1R-04
already:
showed:

state entropy:

0.05956502927131284.

Feature rank:

1 /
512.

Therefore:

its:
apparent:
containment

is:
not:
eligible:
self-repair.

It:
contains:
damage

largely:
by:
making:
the:
organism:
too:
static.

SUPPLEMENTAL CLASSIFICATION

HOMEOSTATIC_REPAIR_CANDIDATES:

NONE.

FULL_SELF_REPAIR_SIGNAL:

FALSE.

But:

CONTAINMENT_SIGNAL:

TRUE

for:

N16_H6

and:

N16_H6_REPAIR.

MECHANISTIC INTERPRETATION

This:
separates:

two:
functions
that:
had:
previously:
been:
conflated.

1.

DAMAGE CONTAINMENT.

Nanites:
can:
reduce:
how far:
a:
local:
lesion
perturbs:
the:
rest:
of:
the:
organism.

SUPPORTED:
mechanically.

2.

STATE RECONSTRUCTION.

Nanites:
must:
know:
what:
the:
damaged:
cells
should:
have:
been

in:
order:
to:
restore:
the:
counterfactual:
trajectory.

One:
hysteretic:
bit
per:
local:
block

does NOT:
carry:
enough:
redundant:
information
for:
that.

NOT SUPPORTED.

Therefore:

the:
next:
research axis

is:

REDUNDANT:
DEVELOPMENTAL:
ENCODING
+
LOCAL:
NANITE:
REPAIR.

The:
repair:
agent
already:
has:
a:
containment:
role.

What:
it:
lacks
is:

LOCAL:
RECOVERY:
INFORMATION.

PLAIN-SPEAK SUPPLEMENT

The:
nanites
did:
something:
useful.

When:
we damaged:
the:
organism,

the:
H6:
nanites
made:
the:
damage
spread:
much less.

The:
repair:
version
contained:
it:
even:
better.

But:

they:
could not:
put:
the:
damaged:
cells
back:
to:
the:
right:
values.

Why?

Because:
the:
nanite
only:
has:
one:
local:
bit.

It can:
tell:

"this area
should stay
stable."

It cannot:
fully tell:

"these:
three
or:
five:
specific:
cells
used to:
look:
exactly:
like:
THIS."

That:
requires:
redundant:
information.

So:
the:
next:
idea
is:

keep:
the:
nanites'
damage-containment:
ability,

but:
give:
the:
organism
a:
distributed:
error-correcting:
developmental:
representation

inside:
the:
same:
fixed:
state budget.

Then:

the:
nanites
would not:
guess:
what:
to:
repair.

The:
surrounding:
redundant:
structure
would:
tell:
them.

canonical_scientific_execution = false.
canonical_dg1r05_frozen_execution_spent = false.
stab18_r1_touched = false.


FINAL DG-1R-05 NON-EVIDENCE PILOT CLOSURE — LOCAL DAMAGE CONTAINMENT / COUNTERFACTUAL RECOVERY

DATE:
2026-09-20.

STATUS:
COMPLETE /
POSITIVE DAMAGE-CONTAINMENT SIGNAL /
NEGATIVE CORRECT-STATE RECONSTRUCTION /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

b4a35269bd99560b8c13613bab284ae47d253b245cf7e4304fde246254e644d3.

CANONICAL OUTPUT

RUN 1 SHA-256:

1ad17fc729eefb0d8a8f241d1d7d02d6bbf2b62cb6c5997e32574967c03df64.

RUN 2 SHA-256:

1ad17fc729eefb0d8a8f241d1d7d02d6bbf2b62cb6c5997e32574967c03df64.

Byte-identical:

PASS.

MECHANICAL VALIDITY

NO-DAMAGE:
counterfactual controls:

PASS.

mechanical_valid:

TRUE.

HOMEOSTATIC_REPAIR_CANDIDATES:

NONE.

FULL_SELF_REPAIR_SIGNAL:

FALSE.

REFERENCE — SLOW128_MIXED1

Combined:

64:
damage scenarios.

Median:
excess divergence area:

1.51953125.

Sustained:
full recovery rate:

0.078125.

Exact:
counterfactual match
at:
h32:

0.078125.

Median:
recovery time
among:
recovered scenarios:

14:
steps.

At:
h16:

whole-state divergence:

0.0546875.

lesion recovery:

0.60.

outside-lesion divergence:

0.04.

median:
damage spread:

5:
bits.

At:
h32:

whole-state divergence:

0.0390625.

lesion recovery:

0.6666666666666667.

outside-lesion divergence:

0.032.

median:
damage spread:

4:
bits.

N16_H5

Median:
excess divergence area:

1.48828125.

Relative:
AUC reduction:

approximately:
2.06%.

Full recovery rate:

0.078125.

At:
h16:

outside-lesion divergence:

0.032520325203252036.

This is:
approximately:
18.7%:
lower
than:
the:
passive:
reference.

But:

lesion recovery:

0.50.

At:
h32:

outside-lesion divergence:

0.03626016260162602.

lesion recovery:

0.60.

Thus:

CONTAINMENT_SIGNAL:

FALSE.

REPAIR_SIGNAL:

FALSE.

Interpretation:

mild:
H5:
homeostasis

changes:
the:
damage dynamics

but:
does not:
materially:
improve:
counterfactual:
recovery.

N16_H6

Median:
excess divergence area:

0.984375.

Relative:
AUC reduction:

0.35218508997429304.

Approximately:

35.2%:
less:
post-damage:
trajectory divergence.

At:
h16:

whole-state divergence:

0.03125.

outside-lesion divergence:

0.016.

Relative:
outside-spread reduction:

60%.

lesion recovery:

0.60.

At:
h32:

whole-state divergence:

0.03125.

outside-lesion divergence:

0.012065040650406504.

Relative:
outside-spread reduction:

0.6229674796747967.

Approximately:

62.3%.

Lesion recovery:

0.40.

Sustained:
full recovery rate:

0.140625.

Thus:

CONTAINMENT_SIGNAL:

TRUE.

REPAIR_SIGNAL:

FALSE.

STRONG_COUNTERFACTUAL_RECOVERY:

FALSE.

Interpretation:

H6:
nanites

behave:
like:
effective:
local:
firebreaks.

They:
substantially:
limit:
how far:
a:
lesion:
perturbs:
the:
rest:
of:
the:
organism.

But:

they:
do NOT:
know:
what:
the:
damaged:
worker bits
should:
have:
been.

Containment:

is:
real.

Correct-state:
reconstruction:

is:
not.

N16_H6_REPAIR

Relative:
excess-divergence-area reduction:

0.4267352185089974.

Approximately:

42.7%.

Relative:
outside-lesion divergence reduction
at:
h16:

0.6983739837398374.

Approximately:

69.8%.

Relative:
outside-lesion divergence reduction
at:
h32:

0.7459349593495934.

Approximately:

74.6%.

Thus:

its:
bounded:
repair:
mechanism

is:
even:
stronger
at:
CONTAINMENT.

CONTAINMENT_SIGNAL:

TRUE.

However:

relative:
lesion recovery gain
at:
h16:

-0.19999999999999996.

Relative:
lesion recovery gain
at:
h32:

-0.16666666666666674.

Thus:

REPAIR_SIGNAL:

FALSE.

STRONG_COUNTERFACTUAL_RECOVERY:

FALSE.

HOMEOSTATIC_REPAIR_CANDIDATE:

FALSE.

Mechanistic telemetry:

the:
repair controller

does:
perform:
additional:
local:
repair attempts /
state changes

after:
damage.

But:

the:
current:
one-bit:
consensus:
repair rule

often:
repairs:
toward:
the:
WRONG:
local:
state

relative:
to:
the:
undamaged:
counterfactual.

This is:
a:
critical:
distinction.

ACTIVE INTERVENTION
does NOT imply:

CORRECT:
RECONSTRUCTION.

N16_H6_DAMP

Relative:
excess-divergence-area reduction:

0.6580976863753213.

Approximately:

65.8%.

CONTAINMENT_SIGNAL:

TRUE.

REPAIR_SIGNAL:

FALSE.

But:

N16_H6_DAMP
was:
already:
demonstrated
in:
DG-1R-04

to:
be:
severely:
OVERSTABILIZED.

Therefore:

its:
low:
damage spread

is:
not:
healthy:
repair.

It is:

partly:
a:
consequence
of:
suppressing:
healthy:
dynamics.

It remains:

INELIGIBLE
as:
a:
primary:
repair:
candidate.

CORE TECHNICAL RESULT

DG-1R-05 establishes:

LOCAL:
HOMEOSTATIC:
CONTROLLERS

CAN:
CONTAIN:
DAMAGE

WITHOUT:
EXTRA:
PERSISTENT:
STATE.

Specifically:

H6:
reduces:
overall:
post-lesion:
divergence

by:
approximately:
35%.

H6_REPAIR:

by:
approximately:
43%.

They also:
reduce:
damage spread
outside:
the:
lesion

by:
roughly:

60-75%

at:
the:
later:
measured:
horizons.

This is:
a:
real:
mechanistic:
capability.

But:

the:
current:
controllers
cannot:
infer:

WHAT:
THE:
DAMAGED:
LOCAL:
STATE
SHOULD:
HAVE:
BEEN.

Their:
one-bit:
controller state
plus:
local:
majority /
consensus

contains:
insufficient:
information

for:
exact:
counterfactual:
reconstruction.

ARCHITECTURAL DISTINCTION

CONTAINMENT:

requires:

recognizing:
that:
a:
local:
disturbance

should:
not:
spread.

RECONSTRUCTION:

requires:

additional:
information
about:

the:
correct:
pre-damage /
counterfactual:
local:
state.

DG-1R-05 shows:

the:
first:
is:
possible
with:
the:
current:
nanites.

The:
second:
is:
not.

NEXT HYPOTHESIS

Do NOT:

give:
the:
nanites:
more:
hidden:
memory.

Instead:

make:
the:
organism's:
local:
state

REDUNDANTLY:
ENCODED

so:
damage
leaves:
enough:
local:
information

for:
a:
small:
controller
to:
infer:
the:
missing:
state.

Examples:

- parity:
  check cells;
- duplicated:
  local:
  developmental:
  motifs;
- sparse:
  local:
  error-correcting:
  signatures.

Fairness:

keep:
the:
total:
persistent:
organism

at:

128 bits.

Trade:

some:
ordinary:
worker:
capacity

for:

local:
redundancy /
check:
state.

This tests:

whether:

REDUNDANCY
+
LOCAL:
NANITE:
REPAIR

can:
turn:
containment
into:
actual:
counterfactual:
healing.

NEXT JUSTIFIED EXPERIMENT

DG-1R-06 —
BOUNDED LOCAL REDUNDANCY /
NANITE COUNTERFACTUAL REPAIR AUDIT.

Compare:

1.
H6 containment
without:
redundancy.

2.
H6_REPAIR
without:
redundancy.

3.
local:
parity /
check-bit:
encoding
without:
active:
nanite repair.

4.
local:
redundancy
+
nanite:
syndrome-guided:
repair.

Primary question:

can:
the:
same:
128-bit:
organism

sacrifice:
a:
small:
amount
of:
raw:
worker:
capacity

to:
gain:
enough:
local:
error-correcting:
information

that:
nanites
can:
restore:
the:
CORRECT:
counterfactual:
state

rather:
than:
merely:
contain:
the:
damage?

PLAIN-SPEAK SUMMARY

What did:
the:
nanites
actually:
do?

They:
worked:
like:
firebreaks.

When:
we:
damaged:
the:
software organism,

the:
H6:
nanites
kept:
the:
damage
from:
spreading
nearly:
as much
as:
it:
normally:
would.

The:
repair:
nanites
contained:
the:
damage
even:
more.

So:

the:
nanite:
idea
did:
produce:
a:
real:
useful:
behavior.

But:

they:
didn't:
know:
what:
the:
broken:
cells
were:
supposed:
to:
contain.

Imagine:

a:
maintenance:
crew
knows:
that:
a:
wall
is:
damaged,

but:
has:
no:
blueprint
showing:
what:
the:
wall
looked:
like.

They:
can:
stop:
the:
damage
from:
spreading.

They:
can:
patch:
something
into:
the:
hole.

But:

they:
cannot:
guarantee
that:
they:
rebuilt:
the:
right:
wall.

That:
is:
exactly:
what:
we:
observed.

The:
next:
experiment
gives:
the:
organism

small:
LOCAL:
CHECKS /
REDUNDANCY

inside:
the:
same:
128-bit:
budget.

Not:
extra:
memory.

Not:
a:
global:
backup.

Just:
enough:
local:
information

that:
a:
nanite
might:
be:
able
to:
say:

"this:
cell
is:
wrong,
and:
I:
can:
infer:
what:
it:
should:
be."

If:
that:
works,

we:
move:
from:

DAMAGE:
CONTAINMENT

to:

ACTUAL:
SELF-REPAIR.

canonical_scientific_execution = false.
stab18_r1_touched = false.


NON-CANONICAL SEMANTIC-MIRROR CORROBORATION 01

DATE:
2026-09-20.

STATUS:
NON-CANONICAL /
NON-EVIDENCE /
FROZEN PRIMARY REMAINS UNSPENT.

WHY THIS EXISTS

The:
one-shot:
GitHub Actions:
execution path

failed:
before:
runner assignment.

Observed:

runner_id = 0.

Job steps:

0.

Therefore:

no:
DG-1R-05:
primary:
damage scenario

was:
executed
by:
that:
failed:
hosted:
workflow.

The:
frozen:
canonical:
DG-1R-05:
harness

remains:

UNSPENT.

INDEPENDENT MIRROR

A:
local:
semantic mirror

implemented:

the:
frozen:
DG-1R-04:
parent mechanics

plus:

the:
frozen:
DG-1R-05:
damage /
counterfactual /
summary:
semantics.

It used:

- NumPy PCG64;
- the:
  exact:
  frozen:
  seed family:
  20260926050000..007;
- the:
  frozen:
  1024-step:
  pre-damage:
  development;
- four:
  unmapped:
  sibling:
  lesion blocks;
- SMALL3;
- LARGE5;
- the:
  same:
  post-damage:
  32-step:
  horizon;
- the:
  same:
  frozen:
  signal equations.

MIRROR REPRODUCIBILITY

RUN 1:

e0140825ce5e683095f3c7cb6b27bbe7c7bf09535fd447b38c7d4509f4e43a79.

RUN 2:

e0140825ce5e683095f3c7cb6b27bbe7c7bf09535fd447b38c7d4509f4e43a79.

Byte-exact mirror determinism:

PASS.

NO-DAMAGE CONTROL

mechanical_valid:

TRUE.

PRIMARY MIRROR RESULT

HOMEOSTATIC_REPAIR_CANDIDATES:

NONE.

FULL_SELF_REPAIR_SIGNAL:

FALSE.

SLOW128_MIXED1 reference:

median:
excess divergence area:

1.51953125.

h16:
whole-state divergence:

0.0546875.

h32:
whole-state divergence:

0.0390625.

h16:
lesion recovery:

0.6.

h32:
lesion recovery:

0.6666666666666667.

h16:
outside-lesion divergence:

0.04.

h32:
outside-lesion divergence:

0.032.

full sustained recovery rate:

0.078125.

N16_H6

Median:
excess divergence area:

0.984375.

Reduction versus reference:

35.218508997429304%.

h16:
outside-lesion divergence:

0.016.

Reduction versus reference:

60%.

h32:
outside-lesion divergence:

0.012065040650406506.

Reduction versus reference:

62.29674796747967%.

CONTAINMENT_SIGNAL:

TRUE.

However:

h16:
lesion recovery gain:

0.

h32:
lesion recovery gain:

-0.2666666666666667.

REPAIR_SIGNAL:

FALSE.

Interpretation:

H6:
strongly:
contains:
damage spread

but:

does NOT:
reconstruct:
the:
lost:
local:
counterfactual:
state.

N16_H6_REPAIR

Median:
excess divergence area:

0.87109375.

Reduction versus reference:

42.67352185089974%.

h16:
outside-lesion divergence:

0.012065040650406506.

Reduction versus reference:

69.83739837398374%.

h32:
outside-lesion divergence:

0.008130081300813009.

Reduction versus reference:

74.59349593495934%.

CONTAINMENT_SIGNAL:

TRUE.

But:

h16:
lesion recovery gain:

-0.2.

h32:
lesion recovery gain:

-0.16666666666666674.

REPAIR_SIGNAL:

FALSE.

Median:
damage-induced:
repair-state-change delta:

+2.

Interpretation:

the:
repair nanites

react:
to:
damage

and:
sharply:
reduce:
propagation,

but:

their:
one-bit:
local:
state

does NOT:
contain:
enough:
information

to:
restore:
the:
specific:
counterfactual:
worker pattern.

N16_H5

CONTAINMENT_SIGNAL:

FALSE.

REPAIR_SIGNAL:

FALSE.

N16_H6_DAMP

Negative:
overstabilized:
control only.

Median:
excess divergence area:

0.51953125.

Reduction:

65.80976863753213%.

CONTAINMENT_SIGNAL:

TRUE.

But:

it:
remains:
ineligible
because:
DG-1R-04:
already:
showed:
severe:
overstabilization.

MECHANISTIC CONCLUSION FROM MIRROR

The:
software-nanite:
idea

shows:
a:
real:
two-part:
behavior.

1.

LOCAL HOMEOSTATIC:
CONTAINMENT

is:
supported:
mechanically.

H6
and:
H6_REPAIR

reduce:

- damage spread;
- whole-organism:
  divergence area;
- outside-lesion:
  divergence.

2.

STATE RECONSTRUCTION

is:
NOT:
supported
by:
one-bit:
local:
controller state.

The:
nanites

can:
recognize /
resist:
local:
disruption

but:

they:
do not:
know:

WHAT:
THE:
LOST:
WORKER:
BITS

SHOULD:
HAVE:
BEEN.

This:
matches:
the:
pre-registered:
CONTAINMENT-ONLY:
branch.

NEXT JUSTIFIED NON-EVIDENCE PILOT

DG-1R-05A —
REDUNDANT:
LOCAL:
DEVELOPMENTAL:
ENCODING
+
NANITE:
REPAIR.

Hypothesis:

containment
already:
works.

The:
missing:
ingredient

is:
RECOVERY INFORMATION.

Instead of:
giving:
nanites:
hidden:
memory,

reserve:
part:
of:
the:
same:
128-bit:
organism

for:
local:
redundant:
state coding.

Then:
test:

can:
nanites

use:
local:
redundancy

to:
reconstruct:
damaged:
worker state

while:
preserving:

- fixed:
  128-bit:
  persistent:
  budget;
- local:
  rules;
- no:
  task:
  targets;
- no:
  external:
  history buffer;
- no:
  hidden:
  repair oracle?

CANONICAL STATUS

DG-1R-05:
canonical frozen primary:

NOT EXECUTED.

This:
mirror

must NOT:
be:
reported
as:

canonical:
DG-1R-05:
evidence.

canonical_scientific_execution = false.
stab18_r1_touched = false.
