TITLE: DG-1A-AR-H151 — Functional Cognitive Micro-Patch / Developmental Context Reconstruction Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh150-regeneration-scaling-micropatch-audit.ice

PURPOSE

H150 established:

COGNITIVE MICRO-PATCHING
IS
GEOMETRICALLY /
RESOURCE PLAUSIBLE

when:

smaller computational cells
also reduce:
functional failure localization
approximately with:
cell area.

H150 did NOT establish:

that a regenerated cell
can regain:
learned functional specialization.

H151 asks:

CAN
A LOCAL COMPUTATIONAL COLONY
LOSE:
PART OF ITS LEARNED MUTABLE STATE

AND:

RECONSTRUCT
USEFUL FUNCTION

FROM:
SURVIVING DEVELOPMENTAL CONTEXT

WITHOUT:
RESTORING
THE LOST CELLS'
SAVED MUTABLE STATE?

The primary hypothesis is:

LOCAL FUNCTIONAL STATE
CAN BE
PARTIALLY REGENERATIVE

WHEN:
LEARNED SPECIALIZATION
IS ALIGNED
WITH:
LOCAL DEVELOPMENTAL CONTEXT.

BOUNDARY

Synthetic research only.

H151 does NOT:
- train or claim a frontier neural model;
- implement biological tissue;
- claim semantic human cognition;
- restore production model weights;
- execute STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

The colony is:
a synthetic distributed function approximator.

Its mutable cell state is:
a scalar learned-specialization surrogate.

The experiment tests:
functional state reconstruction mechanics,
not:
general intelligence.

COLONY

2D integer lattice disk.

Primary radius:

R = 8.

Expected cells:
approximately 197.

Each cell has:

IMMUTABLE DEVELOPMENTAL IDENTITY

- lattice position;
- local neighborhood;
- fixed response center.

and:

MUTABLE LEARNED STATE

- one scalar specialization coefficient w_i.

The mutable coefficient:
is NOT available
to a replacement cell
after:
lesion.

FUNCTIONAL READOUT

Queries are:
2D points
inside:
the normalized colony disk.

Each cell owns:
a fixed radial basis response

phi_i(x).

Primary basis width:

sigma = 0.22
in:
normalized body-radius units.

For query x:

phi_i(x) =
exp(
-distance(x, center_i)^2
/
(2 sigma^2)
).

Normalize:
phi(x)
to:
sum to 1.

Colony output:

y(x) =
sum_i
phi_i(x) w_i.

Thus:

the colony implements:
a distributed nonlinear spatial associative mapping.

LEARNED SPECIALIZATION SURROGATE

Post-training mutable state
is represented by:
a controlled coefficient field.

For each world:

draw:
iid Gaussian coefficient seeds.

Then create three:
developmental-context classes.

C0 — SMOOTH

Apply:
12 rounds
of:
graph-neighbor diffusion

with:
0.50 self retention
and:
0.50 neighbor mean.

Normalize final field:
mean 0,
standard deviation 1.

C1 — MIXED

Apply:
3 rounds
of:
the same diffusion.

Normalize:
mean 0,
standard deviation 1.

C2 — SCRAMBLED

No spatial diffusion.

Normalize:
mean 0,
standard deviation 1.

SCRAMBLED is:
the negative contextual control.

It tests:

whether:
developmental reconstruction
depends on:
local state regularity

rather than:
magically recovering
arbitrary lost parameters.

FUNCTIONAL EVALUATION SET

Per world:

256 held-out query points
sampled uniformly
inside:
the normalized disk.

The pre-lesion colony output
on these queries is:

Y_BASE.

Y_BASE is retained:
ONLY FOR EVALUATION.

Repair policies may NOT:
read:
lost original coefficients
or:
Y_BASE.

LESION

Primary damaged fractions:

1%,
2%,
5%,
10%,
20%.

Primary geometries:

L0 — COMPACT

one center-local compact lesion.

L1 — FOUR-PATCH

same total damaged-cell count
split as evenly as possible
across:
four spatially separated compact patches.

The total lost mutable-state count
is:
identical
between:
matched L0 / L1 worlds.

MEMBERSHIP REGENERATION

Reuse:
the H150 local frontier kernel.

A missing body cell
is membership-eligible
when:
at least one Moore neighbor
is live.

Primary membership repair probability:

0.50.

Synchronous steps.

No cell outside:
the original body
may appear.

Replacement cells receive:

their immutable:
developmental identity

but:

NO SAVED MUTABLE COEFFICIENT.

FUNCTIONAL REPAIR POLICIES

A — CONTEXT-HARMONIC

PRIMARY CANDIDATE.

When:
a missing cell is restored,

its mutable coefficient
is initialized from:

the arithmetic mean
of:
currently live Moore-neighbor coefficients.

If:
no live neighbor exists,

initialize:
0.

After:
every repair step,

all regenerated cells
receive:
one synchronous
context refinement:

w_i(new) =
0.50 w_i(old)
+
0.50 mean(
current live Moore-neighbor coefficients
).

Original surviving cells:
remain fixed.

No original lost coefficient:
is read.

No global target output:
is supplied.

B — ZERO-STATE

Replacement membership restores,

but:

w_i = 0.

No context refinement.

Tests:
topology recovery
without:
specialization recovery.

C — RANDOM-STATE

Replacement membership restores.

New coefficient:

sampled from:
the mean / standard deviation
of:
currently surviving original-cell coefficients.

No:
neighbor conditioning.

No context refinement.

Tests:
generic state replacement
without:
developmental locality.

D — CHECKPOINT-ORACLE

Upper-bound comparator only.

On:
membership restoration,

restore:
the original lost coefficient.

Not deployable
under:
the H151 hypothesis.

It defines:
the functional ceiling
for:
the same membership-regeneration schedule.

FUNCTIONAL RECOVERY

At each repair step:

evaluate:
policy output
Y_t
on:
the fixed 256 held-out queries.

Define:

MSE_LESION =
MSE(
Y_lesioned,
Y_BASE
).

FunctionalRecovery(t) =

1 -
MSE(Y_t,Y_BASE)
/
MSE_LESION.

Report:
the raw value
and:
a clipped [0,1] value
for threshold latency.

If:
MSE_LESION
is numerically negligible,

mark:
the world
as:
functionally trivial
and:
exclude it only from:
T50/T90 ratio calculations,

while:
retaining:
damage / geometry accounting.

Primary lesion sizes are expected
to avoid:
material triviality.

T50:

first step
with:
clipped FunctionalRecovery >=0.50.

T90:

first step
with:
>=0.90.

T99:

first step
with:
>=0.99.

POST-MEMBERSHIP MATURATION

After:
all lesion membership
has regenerated,

CONTEXT-HARMONIC
continues:
context refinement

for:
12 additional steps.

Other policies:
remain fixed

except:
CHECKPOINT-ORACLE,
which is already exact
after:
membership completion.

Maximum total horizon:

64 steps.

PRIMARY FACTORIAL

Context class:

3.

Damage fraction:

5.

Geometry:

2.

Worlds / cell:

100.

Worlds:

3 x 5 x 2 x 100
=
3,000 underlying worlds.

Policies:

4.

12,000 policy-world evaluations.

COMMON-WORLD DISCIPLINE

Inside each underlying world:

all policies receive:

- identical colony geometry;
- identical immutable response centers;
- identical learned baseline coefficient field;
- identical lesion members;
- identical membership repair opportunities;
- identical held-out functional queries.

Only:
mutable-state reconstruction policy
differs.

PRIMARY METRICS

1.
baseline functional variance;

2.
initial lesion functional MSE;

3.
membership T50 / T90 / completion;

4.
functional RecoveryFraction trajectory;

5.
functional T50;

6.
functional T90;

7.
functional T99;

8.
final functional recovery;

9.
final MSE / lesion MSE;

10.
reconstructed-weight RMSE
on:
lesioned cells
for analysis only;

11.
repair steps;

12.
context-refinement steps;

13.
functional downtime:

sum over steps
of:
1 - clipped FunctionalRecovery;

14.
fraction of worlds
reaching:
90% functional recovery;

15.
fraction reaching:
99%;

16.
compact-versus-four-patch difference;

17.
context-class interaction;

18.
oracle gap.

PRIMARY QUESTIONS

Q1.

Can:
CONTEXT-HARMONIC

restore:
>=90%
of:
pre-lesion function

for:
small
1%..5%
lesions

without:
lost mutable-state restoration?

Q2.

Does:
local developmental context

materially outperform:
ZERO-STATE
and:
RANDOM-STATE?

Q3.

Does:
functional regeneration

degrade:
smoothly
with:
lesion fraction

rather than:
collapse immediately?

Q4.

Does:
FOUR-PATCH
functional recovery

benefit from:
parallel spatial boundaries

as:
H150 geometric repair predicts?

Q5.

Does:
SCRAMBLED context

remove:
most of the context-reconstruction advantage?

A positive answer to Q5
is desirable:

it demonstrates:
the mechanism depends on:
local representational organization.

PRIMARY ACCEPTANCE SHAPE

H151 supports:
FUNCTIONAL COGNITIVE MICRO-PATCHING

if:

1.
SMOOTH,
1%..5%:

CONTEXT-HARMONIC
median final functional recovery
>=0.95.

2.
MIXED,
1%..5%:

median final functional recovery
>=0.90.

3.
For:
SMOOTH and MIXED
1%..10%,

CONTEXT-HARMONIC
median final recovery
is:
>=0.10 absolute

above:
both ZERO-STATE
and:
RANDOM-STATE

in at least:
three of:
the four
context x damage
small/mid comparison groups.

4.
For:
SMOOTH 1%..5%,

>=90%
of worlds
reach:
functional T90
within:
24 repair / maturation steps.

5.
Functional recovery
declines monotonically
or:
near-monotonically
as:
damage fraction grows
from:
1%
to:
20%
within:
SMOOTH.

6.
FOUR-PATCH
does not have:
worse median functional T90
than:
COMPACT

by more than:
20%

for:
SMOOTH
1%..10%.

7.
SCRAMBLED:

CONTEXT-HARMONIC
does NOT:
show the same strong advantage

as:
SMOOTH.

Specifically:

median CONTEXT-HARMONIC
minus:
the better of
ZERO / RANDOM

is:
<0.10

for:
at least three of:
five damage fractions.

This is:
a mechanism-specificity gate.

8.
CHECKPOINT-ORACLE
remains:
the ceiling

and:
CONTEXT-HARMONIC
does not:
systematically exceed it.

MIXED / NEGATIVE CONDITIONS

Treat H151 as:
mixed / negative

if:

- small smooth lesions
  fail to recover:
  >=90% function;

- context reconstruction
  is not materially better
  than:
  zero / random state;

- only:
  checkpoint restore
  recovers capability;

- recovery works equally well
  on:
  SCRAMBLED state,
  suggesting:
  the metric is insensitive
  to specialization;

- four-patch geometry
  causes:
  strong functional interference;

- large post-membership maturation
  is required
  even for:
  1%..2% lesions;

- functional recovery
  becomes unstable
  or:
  oscillatory.

ROBUSTNESS AFTER PRIMARY

Only after:
primary closure.

Repair probability:

0.25,
0.50,
1.00.

Context refinement mixing:

0.25,
0.50,
0.75.

Body radius:

6,
8,
11.

Basis width sigma:

0.15,
0.22,
0.30.

No robustness dimension
may be tuned
from:
held-out primary worlds.

PRIMARY SEEDS

Underlying world seed family:

20260919800000
through:
20260919802999.

SANITY SEEDS

20260919890000
family.

Sanity outputs:
NON-EVIDENCE.

No primary threshold
or:
policy parameter

may change
after:
the first held-out primary world
is executed.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_FUNCTIONAL_COGNITIVE_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H151 HELD-OUT PRIMARY EXECUTION.

No H151 primary world
has been executed.

COLONY REALIZATION

Primary body:

integer lattice disk
R=8.

N=197.

Moore 8-neighborhood.

IMMUTABLE RESPONSE CENTERS

Cell response center =
lattice coordinate
divided by:
R.

QUERY REALIZATION

Per world:

256 query points
sampled uniformly
inside:
the unit disk

using:
a deterministic SHA-256-derived
query RNG.

PRIMARY BASIS

Gaussian radial basis.

sigma:
0.22.

Each query row:
normalized to:
unit total response mass.

LEARNED-STATE FIELD

World RNG draws:
iid standard-normal
initial coefficients.

SMOOTH:

12 synchronous graph-diffusion rounds.

MIXED:

3 rounds.

SCRAMBLED:

0 rounds.

Every diffusion round:

0.50 self
+
0.50 Moore-neighbor mean.

Final field:

zero mean,
unit standard deviation.

LESION REALIZATION

Damage count:

ceil(fraction * N),

bounded:
1..N-1.

COMPACT:

select:
cells nearest:
body center.

FOUR-PATCH:

select:
four deterministic farthest-point centers

inside:
0.66R,

with:
held-out world RNG
resolving ties.

Split:
total lesion count
as evenly as possible.

Allocate:
nearest currently unused cells
around each center.

Both geometries:
lose the same declared total cell count.

MEMBERSHIP REGENERATION

Reuse:
H150 frontier membership rule.

A missing cell is eligible
iff:
at least one live Moore neighbor exists.

Primary restoration probability:

0.50.

Membership RNG:

SHA-256-derived
from:
world seed
and:
"membership".

Maximum membership schedule:

52 steps.

All four functional policies
receive:
the identical realized membership schedule.

CONTEXT-HARMONIC

At each membership step:

new cells initialize
synchronously

from:
the arithmetic mean
of:
pre-step live Moore-neighbor coefficients.

After initialization:

all currently regenerated cells
receive:
one synchronous refinement:

0.50 current
+
0.50 current live-neighbor mean.

Original surviving cells:
never change.

After:
membership completion,

continue:
12 context-refinement steps.

Maximum total functional horizon:

64.

ZERO-STATE

Restored coefficient:
0.

No refinement.

RANDOM-STATE

Restored coefficient:

Gaussian draw
using:
mean and standard deviation
of:
the original surviving-cell coefficients.

RNG:
SHA-256-derived
by:
world seed
and:
policy domain.

No:
neighbor conditioning.

No:
refinement.

CHECKPOINT-ORACLE

Restored coefficient:

exact original coefficient.

Evaluation comparator only.

FUNCTIONAL RECOVERY

Y_BASE:
pre-lesion colony output.

Y_BASE is:
evaluation-only.

Repair policies:
cannot read it.

Y_LESION:
output with:
all lesion members absent.

MSE_LESION:
MSE(Y_LESION,Y_BASE).

At each step:

FR_raw =
1 -
MSE(Y_t,Y_BASE)
/
MSE_LESION.

Threshold latency uses:

FR_clip =
clip(
FR_raw,
0,
1
).

T50 / T90 / T99:

first evaluated step
crossing:
0.50 / 0.90 / 0.99.

Functional downtime:

sum:
1 - FR_clip

over:
evaluated repair / maturation steps.

Weight RMSE on:
lesioned coefficients

is:
analysis only.

It is not:
available to repair policies.

FUNCTIONALLY TRIVIAL

MSE_LESION < 1e-14.

Such a world:
would remain in:
damage accounting

but:
be excluded from:
functional threshold-ratio analysis.

SANITY

Disjoint sanity family:

20260919890000...

Seven representative worlds
were executed.

NON-EVIDENCE signals:

SMOOTH:

2% compact:
CONTEXT final recovery
approximately 0.979.

5% four-patch:
approximately 0.970.

20% compact:
approximately 0.564.

SCRAMBLED:

context reconstruction
showed:
no strong recovery.

MIXED:

intermediate behavior.

These sanity values:
did NOT alter:

- policy identity;
- diffusion rounds;
- context mixing;
- basis width;
- lesion fractions;
- acceptance thresholds;
- primary sample size;
- primary seeds.

FROZEN SANDBOX HARNESS SHA-256

3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

No execution-semantic change
is permitted
after:
the first held-out H151 primary world.

PRIMARY SEEDS REMAIN

20260919800000
through:
20260919802999.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
