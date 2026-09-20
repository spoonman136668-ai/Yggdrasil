TITLE: DG-1A-CLR3-H191-P7 — Bounded Shared-Core Factor Micropatch Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DEVELOPMENTAL MICROPATCH PILOT / NOT H191 PRIMARY
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION / BOUNDED SHARED-CORE GROWTH
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p6-frozen-shared-core-capability-addition-audit.ice

PURPOSE

P6 established:

- decoder-only capability addition
  preserves:
  all old capability predictions
  exactly;

- but:
  the CORE3-recruited:
  eight-factor support
  is:
  geometrically insufficient
  for:
  later capabilities;

- CAP4 already enters:
  TRANSITION;

- CAP6 reaches:
  OVER-CAPACITY;

- joint-refit support overlap
  falls:
  almost immediately
  toward:
  zero.

P7 tests:

BOUNDED:
INCREMENTAL:
SHARED-CORE:
GEOMETRY GROWTH.

QUESTION

WHEN:
CAP4
DOES NOT FIT
THE:
FROZEN:
CORE3:
EIGHT-FACTOR SUPPORT,

CAN:

ONE
OR:
TWO

NEW:
FIXED-DICTIONARY FACTORS

REPAIR:
THE NEW CAPABILITY

WITHOUT:

- moving:
  the old eight factors;
- refitting:
  old decoders;
- changing:
  old predictions?

BOUNDARY

NON-EVIDENCE synthetic developmental micropatch pilot only.

No:
accepted H190 parent.
No:
H191 acceptance claim.
No:
living tissue.
No:
wetware.
No:
biological implementation claim.
No:
production modification.
No:
canonical scientific execution.
No:
STAB-18-R1 execution.

WORLD GEOMETRY

Exact P6 geometry.

Each world contains:

8:
potential capability contexts

with:

radius:
0.60.

sd:
0.14.

Ownership:

nearest:
of:
all 8:
fixed centers.

P7 uses:

capabilities:
0,
1,
2

to:
form:
CORE3,

then:

capability:
3

as:
the:
new:
CAP4 capability.

SOURCE FAMILY

Exact P6 / P5 CAP8-style source:

8:
hidden shared Gaussian factors.

Source sigma:

uniform:
[0.12,0.42].

Decoder matrix:

8 x 8.

Capability-specific remainder:

0.10:
sinusoidal component

with:
the exact:
P5 distributions.

DATA

Per:
capability:

128:
distillation coordinates.

512:
held-out coordinates.

CORE3

Jointly recruit:

8:
DICT8:
factors

using:
capabilities:
0,
1,
2.

Fixed candidate dictionary:

3209 parent centers

x:

sigma:
0.22,
0.44,
0.88.

Fit:

8-coefficient:
old decoders

for:
capabilities:
0,
1,
2.

Then freeze:

- core support;
- scale slots;
- old decoders.

CAP4 PATCH POLICIES

PATCH0

No:
new factor.

Fit:
capability 3
decoder

on:
the frozen:
8-factor core.

This reproduces:
P6's:
decoder-only:
CAP4 mechanism.

PATCH1

Add:
exactly:
one:
new:
fixed dictionary factor.

Core:
8 factors
remain:
unchanged.

Recruit:
the new factor
using:

ONLY:

capability 3:
unlabeled:
distillation residual
against:
the frozen core.

At:
candidate scoring:

append:
one candidate factor

and:
ridge-refit:

ONLY:
capability 3's:
decoder

over:
core + candidate.

Choose:
lowest:
capability-3:
normalized:
distillation MSE.

Tie:
candidate order.

Old:
capability decoders:

remain:
unchanged

with:
implicit:
zero coefficient
for:
the new factor.

PATCH2

Nested:
from PATCH1.

Add:
one:
additional:
fixed dictionary factor

using:
the same:
new-capability-only
residual criterion.

Total factors:

10.

Again:

refit:
ONLY:
capability 3's decoder.

Old:
support
and:
old:
functional coefficients

remain:
frozen.

CANDIDATE EXCLUSION

A:
patch candidate
may NOT:
duplicate:
an existing:
core factor

or:
an already selected:
patch factor.

No:
factor replacement.

No:
old factor deletion.

JOINT_REFIT8 REFERENCE

Reference only.

Recruit:
a fresh:
8-factor DICT8 core

jointly
using:

capabilities:
0,
1,
2,
3.

Fit:
all:
four decoders.

This is:

NOT:
the developmental candidate.

It measures:
how close:
bounded micropatching
comes:
to:
full:
shared-core reorganization.

PRESERVATION

For:
capabilities:
0,
1,
2,

PATCH1
and:
PATCH2:

old decoder values:

must:
remain:
exactly unchanged.

Patch-factor coefficients
for:
old capabilities:

implicit:
zero.

Old predictions:

must:
match:
CORE3 predictions

within:
normalized drift:
<=1e-12.

RESOURCE ACCOUNTING

PATCH0:

factors:
8.

New-cap decoder scalars:
8.

New-cap per-query residual operations:
16.

Geometry growth:
0%.

PATCH1:

factors:
9.

New-cap decoder scalars:
9.

New-cap per-query residual operations:
18.

Old-cap per-query residual operations:
16.

Geometry growth:

1 / 8
=
12.5%.

PATCH2:

factors:
10.

New-cap decoder scalars:
10.

New-cap per-query residual operations:
20.

Old-cap per-query residual operations:
16.

Geometry growth:

2 / 8
=
25%.

Old:
24 learned:
CORE3 decoder scalars
remain:
unchanged.

WORLD FAMILY

12:
disjoint worlds.

Seeds:

20260924800000
through:
20260924800011.

No:
P0-P6
seed reuse.

PRIMARY METRICS

For:
PATCH0,
PATCH1,
PATCH2,
JOINT_REFIT8:

- CAP4:
  held-out NMSE;

- CAP4:
  distillation NMSE;

- four-capability:
  world mean NMSE;

- four-capability:
  world worst NMSE;

- distillation-to-held-out gap.

Paired:

PATCH0 / 1 / 2
minus:
JOINT_REFIT8

for:

- CAP4 new-capability NMSE;
- world mean NMSE.

Preservation:

- old decoder max absolute change;
- old prediction drift.

Micropatch geometry:

- selected patch:
  parent-site IDs;
- selected:
  scale slots;
- distance:
  from:
  nearest:
  existing core factor center;
- whether:
  PATCH1 / PATCH2
  factors:
  overlap:
  JOINT_REFIT8 support.

FROZEN PILOT CRITERIA

PATCH1 is:
ROBUST MICROPATCH
if:

1.
Median:
CAP4 held-out NMSE
<=0.05.

2.
Median:
CAP4 gap
versus:
JOINT_REFIT8
<=0.03.

3.
Median:
four-capability:
world-mean gap
versus:
JOINT_REFIT8
<=0.02.

4.
Old prediction drift:
<=1e-12.

5.
Old decoder change:
0.

6.
Generalization:
median:
distillation-to-held-out
CAP4 gap
<=0.05.

PATCH2 is:
ROBUST MICROPATCH
under:
the same:
quality gates

if:
PATCH1
does not:
pass.

Interpretation:

PATCH1:
preferred
over:
PATCH2

because:
it uses:
less:
shared geometry growth.

TRANSITION:

CAP4 gap:
>0.03
but:
<=0.07

OR:

world-mean gap:
>0.02
but:
<=0.05.

OVER-CAPACITY:

CAP4 gap:
>0.07

AND:

world-mean gap:
>0.05.

No:
rank / patch-budget change
inside:
P7.

REPRODUCIBILITY

Two:
complete:
12-world sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P7 world,

do not alter:

- patch budgets;
- candidate dictionary;
- factor scales;
- candidate scoring;
- ridge;
- CORE3 definition;
- new capability identity;
- geometry;
- world family;
- thresholds.

NEXT

If:
PATCH1
or:
PATCH2
is:
ROBUST,

proceed to:
sequential:
bounded micropatching
for:
CAP5,
CAP6,
and:
CAP8.

Old:
factors
must:
remain:
immutable.

New:
factors
may:
accumulate
only when:
the current capability
cannot:
fit:
the existing shared core.

If:
PATCH2
fails:

the next mechanism
should:
test:
bounded:
factor replacement
or:
localized:
shared-factor adaptation

rather than:
unbounded:
factor accumulation.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
