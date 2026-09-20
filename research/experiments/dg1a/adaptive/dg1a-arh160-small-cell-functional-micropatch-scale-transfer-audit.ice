TITLE: DG-1A-AR-H160 — Small-Cell Functional Micro-Patch Scale-Transfer Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh159-interleaved-structural-functional-micropatch-audit.ice

PURPOSE

H150 established:

small-cell geometry
becomes:
repair-advantageous

when:
damage localization
improves approximately
with:
cell area

(beta approximately 2).

H159 established:

functional recalibration
can safely begin
at:
approximately 50%
local membership return.

H160 combines these results.

Question:

CAN
A LARGER COGNITIVE BODY
BUILT FROM:
MORE,
SMALLER,
COMPUTATIONAL CELLS

RETAIN:

- micro-patch latency;
- functional quality;
- reliability;
- fixed feedback cost

when:
a defect localizes
according to:
the H150 beta=2 regime?

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

MACRO BODY / CELL SCALE

Hold:
normalized macro body
fixed.

Reference:

g=1.0
uses:
R=8.

Cell linear scale:

g =
1.00,
0.75,
0.50,
0.35,
0.25.

Resolution:

R(g) =
round(
8 / g
).

Thus:

smaller g
creates:
more computational cells

over:
the same normalized macro area.

Expected cell count:

approximately proportional to:
1 / g^2.

MACRO DEFECT

Base defect fractions:

f0 =
0.05,
0.10.

Use:
the H150
beta=2
localization law:

f_damage(g) =
f0 * g^2.

Damage count:

ceil(
f_damage(g) * N(g)
).

Thus:

as:
cells become smaller,

the damaged fraction
shrinks

while:
the absolute number
of damaged computational cells

should remain:
approximately bounded.

This is:
the architecture under test.

GEOMETRY

COMPACT.

One:
macro-centered local wound.

FOUR-PATCH.

The same total damaged-cell count
is:
split across:
four normalized macro centers.

The four centers:

share:
one deterministic world rotation

and:
lie at:
normalized radius 0.55

with:
90-degree separation.

This preserves:
macro wound geometry

across:
cell resolutions.

RESOLUTION-INVARIANT LEARNED FIELD

H151 graph diffusion
is:
grid-resolution dependent.

H160 therefore uses:
a continuous macro coefficient field

sampled at:
each cell center.

All g values
inside:
one macro world

share:
the same continuous field parameters.

SMOOTH

24 Gaussian macro anchors.

Anchor centers:
uniform inside:
the unit disk.

Anchor weights:
iid standard normal.

Width:

0.35
body-radius units.

MIXED

Two-scale field:

16 broad anchors
with:
width 0.35

plus:

32 fine anchors
with:
width 0.10.

Broad / fine contribution weights:

0.65 / 0.35

before:
final normalization.

For each g:

sample:
the same continuous field

at:
that resolution's
cell centers.

Normalize sampled coefficients:

mean 0,
standard deviation 1.

This preserves:
macro representational organization

while:
changing:
cell granularity.

FUNCTIONAL READOUT

Reuse:
H151 Gaussian RBF readout.

sigma:

0.22
normalized body-radius units.

Held-out evaluation:

256 normalized query points

shared across:
all g values
inside:
one macro world.

Thus:

the macro task
is:
resolution-comparable.

REPAIR ARCHITECTURE

A — START100

Serial comparator.

Begin:
functional calibration

after:
100%
local membership return.

B — START50

H159 selected architecture.

Begin:
functional calibration

after:
50%
local membership return.

C — CHECKPOINT-ORACLE

Exact lost coefficient restore
on:
membership return.

Evaluation ceiling only.

START50 / START100

Membership repair:

H150/H151 local frontier.

p=0.50.

Functional feedback:

- lambda=0.01;
- 24-observation cap;
- 6 observations / active step;
- global leverage ordered query sequence;
- accumulated feedback reused;
- solve expands
  as:
  regenerated cells join;
- surviving original coefficients fixed.

FEEDBACK NOISE

eta:

0,
0.25.

Noise scale:

eta
*
sqrt(
lesion-induced functional MSE
).

Noise-free evaluation.

COMMON MACRO-WORLD DISCIPLINE

One macro-world seed
defines:

- continuous learned field;
- held-out evaluation query set;
- four-patch macro orientation.

Every:
g

within:
that macro world
uses:
the same macro latent field
and:
evaluation queries.

Membership and feedback stochasticity
receive:
g-specific deterministic
sub-seeds.

PRIMARY FACTORIAL

Context:

SMOOTH,
MIXED.

Base defect f0:

0.05,
0.10.

Geometry:

COMPACT,
FOUR-PATCH.

Macro worlds / cell:

60.

Macro worlds:

2 x 2 x 2 x 60
=
480.

Cell scales:

5.

Feedback noise:

2.

Condition-worlds:

480 x 5 x 2
=
4,800.

Policies:

3.

Executed policy-condition evaluations:

14,400.

PRIMARY METRICS

1.
body cells N(g);

2.
damaged cells;

3.
realized damage fraction;

4.
damaged-cell scaling CV
across:
g;

5.
membership completion;

6.
final functional recovery;

7.
first T90;

8.
stable T90;

9.
stable-T90 world fraction;

10.
stable T90 before:
membership completion;

11.
functional downtime;

12.
feedback observations;

13.
query-sequence identity;

14.
T90 regression rate;

15.
g x f0 interaction;

16.
COMPACT / FOUR interaction;

17.
eta interaction;

18.
START50 advantage
versus:
START100;

19.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H160 supports:
SMALL-CELL
FUNCTIONAL MICRO-PATCH
SCALE TRANSFER

if:

1.
For:
each f0 x geometry macro group,

median damaged-cell count
across:
g

has:
coefficient of variation
<=20%.

This verifies:
the intended beta=2
bounded patch-size regime.

2.
MIXED,
f0=0.05:

START50
median final recovery
>=0.95

for:
every g
and:
both eta classes.

3.
MIXED,
f0=0.10:

START50
median final recovery
>=0.93

for:
every g
and:
both eta classes.

4.
MIXED,
both f0 values:

START50
stable-T90 world fraction
>=0.90

for:
every g
and:
both eta classes.

5.
For:
MIXED
FOUR-PATCH
f0=0.10,

START50
reduces:
median stable T90
versus:
START100

by:
>=20%

at:
at least:
4 / 5
g values

for:
eta=0

and:
at least:
4 / 5
for:
eta=0.25.

6.
MIXED START50
median stable T90
at:
g=0.25

is:
no more than:
25%
slower

than:
g=1.0

for:
at least:
three of:
four
f0 x geometry groups

under:
each eta class.

7.
MIXED START50
median functional downtime
at:
g=0.25

is:
no more than:
25%
higher

than:
g=1.0

for:
at least:
three of:
four
f0 x geometry groups

under:
each eta class.

8.
START50
T90-regression rate
<=10%

for:
every:
MIXED
g x f0 x eta group.

9.
All non-oracle policies
remain:
within:
the fixed 24-observation cap.

10.
SMOOTH START50
median final recovery
>=0.98

for:
every g,
f0,
and:
eta.

11.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H160 as:
mixed / negative
if:

- damaged-cell count
  grows strongly
  as:
  g shrinks
  despite:
  beta=2 localization;

- functional quality
  degrades:
  at fine granularity;

- stable T90
  grows:
  materially with:
  total body size;

- fixed 24-query feedback
  becomes:
  insufficient
  at:
  fine resolution;

- START50 loses:
  its interleaving advantage;

- smaller cells
  create:
  long-tail repair instability;

- macro task representation
  changes:
  qualitatively
  across:
  g.

PRIMARY MACRO-WORLD SEEDS

20260920900000
through:
20260920900479.

Each macro seed
expands into:
5 g values
x
2 eta classes.

SANITY MACRO-WORLD SEEDS

20260920990000...

Sanity:
NON-EVIDENCE.

No:
cell scale,
beta,
field definition,
lambda,
feedback budget,
noise level,
or:
acceptance gate

may change
after:
the first held-out H160 condition-world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_SMALL_CELL_FUNCTIONAL_MICROPATCH_SCALE_TRANSFER

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
