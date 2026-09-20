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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — SMALL-CELL SCALE-TRANSFER HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H160 HELD-OUT PRIMARY EXECUTION.

FINAL H160 SANDBOX HARNESS

File:

h160_scale_transfer_frozen_v1.py

SHA-256:

dde8d09cf75085c521c12960e408aa017581b1f308509c7df2c5c71ded9ac564.

CELL-SCALE REALIZATION

g:

1.00,
0.75,
0.50,
0.35,
0.25.

R(g):

round(
8 / g
).

Observed body sizes:

g=1.00:
N=197.

g=0.75:
N=377.

g=0.50:
N=797.

g=0.35:
N=1653.

g=0.25:
N=3209.

BETA-2 DAMAGE

For:
base defect f0,

actual fraction:

f0 * g^2.

Damage count:

ceil(
N(g) * f0 * g^2
).

Thus:

the intended small-cell architecture
keeps:
absolute local patch size
approximately bounded

while:
the total body grows.

RESOLUTION-INVARIANT FUNCTIONAL FIELD

SMOOTH:

24 continuous Gaussian macro anchors.

width:
0.35.

MIXED:

16 broad anchors:
width 0.35.

32 fine anchors:
width 0.10.

Contribution weights:

0.65 broad,
0.35 fine.

The same:
continuous macro field parameters

are sampled
at:
every g

inside:
one macro world.

Each sampled coefficient field
is normalized:
mean 0,
standard deviation 1.

FUNCTIONAL READOUT

Gaussian RBF:

sigma=0.22
in:
normalized macro coordinates.

The same:
256 evaluation query points

are used:
across:
all g

inside:
one macro world.

FOUR-PATCH GEOMETRY

Four normalized centers:

radius:
0.55.

One:
macro-world rotation.

Centers:
90 degrees apart.

The same:
macro geometry

is mapped
to:
each cell resolution.

REPAIR

START100:

serial functional-calibration baseline.

START50:

H159 selected policy.

Both:

- p=0.50 membership frontier;
- lambda=0.01;
- 24 feedback observations maximum;
- 6 observations / active step;
- precomputed leverage query sequence;
- expanding joint solve;
- surviving coefficients fixed.

ORACLE:

evaluation ceiling only.

NOISE

eta:

0,
0.25.

Noise:
scaled to:
lesion-induced functional error.

SANITY

Disjoint macro family:

20260920990000...

12 macro worlds.

5 g values.

2 eta classes.

3 policies.

360 policy-condition evaluations.

Mechanical checks:

- all declared scales completed;
- no functionally-trivial worlds;
- body size rises:
  approximately as 1/g^2;
- no non-oracle policy exceeds:
  24 observations;
- ORACLE remains:
  evaluation-only.

NON-EVIDENCE SIGNAL

Representative MIXED
f0=0.10
FOUR-PATCH:

g=1.00:

N=197.
damage approximately 20 cells.

START100 stable T90:
approximately 3.5.

START50:
approximately 2.

g=0.50:

N=797.
damage approximately 20 cells.

START100:
approximately 2.5.

START50:
approximately 2.5.

g=0.25:

N=3209.
damage approximately 21 cells.

START100:
approximately 2.

START50:
approximately 2.

Final recovery
remained:
approximately 0.997..0.999+
across:
these representative scales
and:
both eta classes.

This sanity output is:

NON-EVIDENCE.

No:
g value,
beta,
field generator,
macro geometry,
lambda,
feedback budget,
noise level,
sample size,
or:
acceptance gate

is changed.

PRIMARY MACRO FAMILY

20260920900000..20260920900479.

480 held-out macro worlds.

4,800 g x eta condition-worlds.

14,400 policy-condition evaluations.

H160 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H160 condition-world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — SMALL-CELL FUNCTIONAL MICRO-PATCH SCALE TRANSFER

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE SCALE TRANSFER.

FINAL PINNED HARNESS SHA-256

dde8d09cf75085c521c12960e408aa017581b1f308509c7df2c5c71ded9ac564.

ACCEPTED PRIMARY MACRO FAMILY

20260920900000..20260920900479.

PRIMARY MATRIX

480 held-out macro worlds.

5 cell scales.

2 feedback-noise classes.

4,800 g x eta condition-worlds.

3 policies.

14,400 policy-condition evaluations.

Validation:

- exactly 480 unique macro seeds;
- exactly 4,800 macro-seed x g x eta conditions;
- exactly three policy rows per condition;
- zero duplicate condition x policy rows;
- zero functionally-trivial worlds;
- no non-oracle policy exceeds the 24-observation cap;
- START50 and START100 use identical query-sequence hashes in every paired condition;
- no post-primary parameter tuning.

BODY SCALE

Observed body sizes:

g=1.00:
N=197.

g=0.75:
N=377.

g=0.50:
N=797.

g=0.35:
N=1653.

g=0.25:
N=3209.

Thus:

the finest tested representation
contains:
approximately 16.3x
as many computational cells
as:
the reference body.

BETA-2 PATCH SIZE

Median damaged-cell count
across:
g.

f0=0.05:

10,
11,
10,
11,
11
cells
for:
g=1.00,
0.75,
0.50,
0.35,
0.25.

f0=0.10:

20,
22,
20,
21,
21.

Coefficient of variation
across g:

approximately:
3.6%..4.6%
depending on:
f0 / geometry.

Frozen limit:
<=20%.

PASS.

Therefore:

the H150 beta=2
localization law
successfully converts:

LARGER BODY
+
SMALLER CELLS

into:

APPROXIMATELY CONSTANT
LOCAL REPAIR BURDEN.

FUNCTIONAL QUALITY

MIXED START50
median final recovery
across:
all g
and:
both eta classes

has:
minimum group median:

approximately:
0.9973.

This exceeds:

f0=0.05 target:
0.95.

f0=0.10 target:
0.93.

PASS:
every g,
both noise classes.

STABLE-T90 RELIABILITY

MIXED START50
stable-T90 world fraction

across:
all g,
f0,
and:
eta

has:
minimum group rate:

approximately:
98.33%.

Frozen target:
>=90%.

PASS:
every group.

START50 REGRESSION

Maximum MIXED
T90-regression rate
across:
g x f0 x eta:

approximately:
0.83%.

Frozen limit:
<=10%.

PASS.

SMOOTH CONTROL

START50
SMOOTH
minimum group
median final recovery:

approximately:
0.9976.

Frozen target:
>=0.98.

PASS:
every g,
f0,
eta.

INTERLEAVING ADVANTAGE ACROSS SCALE

MIXED
FOUR-PATCH
f0=0.10.

Median stable T90:

g=1.00:

START100:
3.

START50:
2.

reduction:
33.3%.

g=0.75:

3
->
2.

33.3%.

g=0.50:

3
->
2.

33.3%.

g=0.35:

2
->
2.

0%.

g=0.25:

2
->
2.

0%.

The pattern is:
identical
for:
eta=0
and:
eta=0.25.

Frozen gate:

>=20% improvement
at:
4 / 5
g values

for:
both eta classes.

Observed:

3 / 5.

FAIL.

Interpretation:

START50 does NOT:
break
at:
fine granularity.

Instead:

the serial START100 baseline
itself reaches:
the two-step latency floor

at:
g=0.35
and:
g=0.25.

There is:
no remaining latency
for:
interleaving
to remove.

This is:
a SATURATION
of:
the interleaving advantage,

not:
a scale-transfer loss
of:
functional recovery.

FINE-SCALE STABLE-T90 TRANSFER

MIXED START50.

Compare:

g=0.25
to:
g=1.00

within:
each f0 x geometry group.

eta=0:

f0=.05 COMPACT:
2 vs 2.

f0=.05 FOUR:
2 vs 2.

f0=.10 COMPACT:
3 vs 2.

f0=.10 FOUR:
2 vs 2.

eta=.25:

same pass/fail shape.

Thus:

g=0.25
is:
no more than 25% slower

in:
3 / 4 groups

for:
each noise class.

Frozen gate:
3 / 4.

PASS
at:
the boundary.

NORMALIZED DOWNTIME GATE

The preregistered
normalized functional-downtime
comparison
does NOT pass.

g=0.25 / g=1.00
median normalized downtime ratios:

eta=0:

f0=.05 COMPACT:
approximately 1.30.

f0=.05 FOUR:
1.85.

f0=.10 COMPACT:
1.05.

f0=.10 FOUR:
1.54.

Only:
1 / 4
meets:
the <=1.25 limit.

eta=.25:

approximately:

1.24,
1.56,
1.01,
1.29.

Only:
2 / 4
pass.

Frozen requirement:
3 / 4.

FAIL.

POST-PRIMARY DIAGNOSTIC —
ABSOLUTE FUNCTIONAL ERROR EXPOSURE

This diagnostic does NOT:
replace
the failed preregistered gate.

It explains:
what the normalized metric is measuring.

As:
g shrinks,

the beta=2 lesion occupies:
a much smaller fraction
of:
the macro body.

Accordingly:

lesion-induced functional MSE
falls sharply.

Define,
for diagnostic interpretation only:

absolute_error_exposure_proxy =
normalized functional downtime
*
lesion MSE.

Median:
g=0.25 / g=1.00
ratios

across:
MIXED
f0 x geometry groups

are:

eta=0:

approximately:

0.037,
0.008,
0.019,
0.011.

eta=.25:

approximately:

0.031,
0.008,
0.017,
0.009.

Thus:

although:
recovery can consume
more lesion-normalized downtime

at:
fine granularity,

the absolute macro functional-error exposure
is only:
approximately 0.8%..3.7%

of:
the g=1.0 reference
in these groups.

This diagnostic is:
consistent with:

smaller cells
shrinking:
the functional blast radius

rather than:
creating:
a larger macro failure.

It does NOT:
retroactively pass
the normalized-downtime gate.

CHECKPOINT ORACLE

Remains:
the functional ceiling
at:
1.0.

PASS.

PREREGISTERED GATE REVIEW

PASS:

1.
Bounded damaged-cell count
under:
beta=2.

2.
MIXED f0=.05
final quality.

3.
MIXED f0=.10
final quality.

4.
Stable-T90 reliability
across scale.

6.
Fine-scale stable-T90 transfer:
3 / 4 groups
for:
each eta.

8.
Low T90-regression rate.

9.
Fixed 24-observation cap.

10.
SMOOTH quality.

11.
ORACLE ceiling.

FAIL / MIXED:

5.
START50
retains:
>=20%
advantage
at:
4 / 5 scales.

Observed:
3 / 5.

7.
Fine-scale
normalized functional-downtime transfer.

Observed:
1 / 4
for:
eta=0

and:
2 / 4
for:
eta=.25.

FINAL INTERPRETATION

H160 is:

MIXED-POSITIVE.

The central:
SMALL-CELL
SCALE-TRANSFER
hypothesis

is strongly supported.

A macro body
can grow from:

197
to:
3209
computational cells

while:

- local patch size remains:
  approximately constant;
- final functional recovery remains:
  approximately 0.997..1.000;
- stable-T90 reliability remains:
  approximately 98%..100%;
- the same:
  24-observation
  local functional budget
  remains sufficient;
- noisy feedback
  eta=.25
  does not:
  break scale transfer.

The important correction is:

INTERLEAVING AUTHORITY
SHOULD NOT:
BE A FIXED
GRANULARITY-INDEPENDENT RULE.

At:
coarser scales,

START50 materially reduces:
end-to-end latency.

At:
the finest scales,

membership regeneration
already reaches:
the latency floor,

so:
START50 offers:
no additional speedup.

This suggests:

repair-control policy
should depend on:

EXPECTED STRUCTURAL REPAIR LATENCY,

not:
cell scale
or:
membership percentage
alone.

SECOND ARCHITECTURAL RESULT

The preregistered normalized downtime
becomes:
a poor sole macro-cost indicator
when:
the lesion's own macro functional impact
shrinks strongly with:
cell granularity.

Future long-horizon work should report:

BOTH:

1.
lesion-normalized recovery latency / downtime;

AND:

2.
absolute macro functional-error exposure.

NEXT SCOPED QUESTION

The small-cell architecture
has now passed:

- geometric scaling;
- functional reconstruction;
- weak-prior calibration;
- noisy-feedback robustness;
- structural/functional interleaving;
- scale transfer.

The next high-leverage risk is:

CUMULATIVE DRIFT
UNDER:
REPEATED CELL TURNOVER.

A regenerative intelligence architecture
is useful only if:

many local cognitive micro-patches

do NOT:
slowly corrupt
the global function.

NEXT:

H161 —
LONG-HORIZON
REPEATED COGNITIVE TURNOVER /
MICRO-PATCH DRIFT AUDIT.

Use:

- fine-grained bodies;
- beta=2 bounded local lesions;
- lambda=0.01;
- fixed 24-observation ceiling;
- H159 START50 where structural ETA
  leaves overlap headroom;
- serial completion
  as:
  a comparator;
- repeated local wounds
  across:
  many repair cycles;
- no checkpoint restoration;
- cumulative:
  final-function drift,
  repair latency,
  absolute error exposure,
  and:
  local-state turnover.

H160 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
