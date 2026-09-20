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


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P7 BOUNDED SHARED-CORE MICROPATCH HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P7 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p7_bounded_shared_core_micropatch_v1.py

Harness commit:

32f3db885223b41d26d54e3d964e5947b32dee7b.

Git blob SHA:

d39ae30800b27e9ddc65802026d41aa4d6dc973d.

Source SHA-256:

575471bf0c8bea2e62a7f8e80a6803c5c135f5173f8b7b3c5829ad03044f816a.

Source bytes:

12689.

DEPENDENCY

Frozen H191-P6 harness Git blob:

6e945c8a6d5ac1f1891ce79945717acd1192a5c6.

Pinned P6 source SHA-256:

8460bdef124a1d42f9e338249fbbbf99c88e85494bea35a56ecc7530cfc1d31e.

FROZEN WORLD FAMILY

20260924800000..20260924800011.

12 worlds.

FROZEN POLICIES

PATCH0:
8 frozen CORE3 factors;
new capability decoder only.

PATCH1:
CORE3 +
exactly 1:
new fixed-dictionary factor.

PATCH2:
nested PATCH1 +
exactly 1:
additional fixed-dictionary factor.

JOINT_REFIT8:
reference only.

Patch factor recruitment:

new capability 3:
unlabeled distillation residual only.

No:
old decoder refit.
No:
old support move.
No:
factor replacement.
No:
factor deletion.

REPRODUCIBILITY

Execute:
two complete:
12-world sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P7 NON-EVIDENCE PILOT CLOSURE — BOUNDED SHARED-CORE FACTOR MICROPATCH

DATE:
2026-09-20.

STATUS:
COMPLETE /
POSITIVE ONE-FACTOR MICROPATCH RESULT /
PATCH1 PREFERRED /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

575471bf0c8bea2e62a7f8e80a6803c5c135f5173f8b7b3c5829ad03044f816a.

CANONICAL OUTPUT

RUN 1 SHA-256:

5cbdca1c55980487059ad16c1d0fe4eae066ba4f6186bba012e66fa5ea8960d8.

RUN 2 SHA-256:

5cbdca1c55980487059ad16c1d0fe4eae066ba4f6186bba012e66fa5ea8960d8.

Byte-identical:

PASS.

REFERENCE

JOINT_REFIT8:

median CAP4 held-out NMSE:

0.013278544858767356.

Median four-capability world-mean NMSE:

0.009513592573576321.

Median world-worst NMSE:

0.02212671272711558.

CORE3-vs-JOINT_REFIT8
exact support overlap median:

0 / 8.

Jaccard median:

0.

Thus:

CAP4 creates:
strong:
geometry pressure

relative to:
the original:
CORE3 support.

PATCH0 — DECODER ONLY

Median CAP4 held-out NMSE:

0.08807601818132867.

P90:

0.3243280544331875.

Median CAP4 gap
versus:
JOINT_REFIT8:

+0.0707364584340544.

Median:
world-mean gap:

+0.01269033694022106.

Median:
distillation-to-held-out
CAP4 gap:

0.016022570226603604.

Old prediction drift:

0.

Old decoder change:

0.

Classification:

MIXED_UNCLASSIFIED.

This reproduces:

the P6 finding
that:
decoder-only addition
is:
not:
reliable enough.

PATCH1 — ONE NEW FACTOR

Median CAP4 held-out NMSE:

0.005538819338426324.

P90:

0.04812101479582891.

Median CAP4 gap
versus:
JOINT_REFIT8:

-0.0028729326412371935.

Thus:

on:
the median,

PATCH1
slightly:
outperforms:
the fully:
jointly re-recruited:
8-factor reference

for:
the new capability.

Median:
four-capability:
world-mean NMSE:

0.011389480884563288.

Median:
world-mean gap
versus:
JOINT_REFIT8:

-0.0006339155554066613.

P90:
world-mean gap:

0.005481030523138516.

Median:
distillation-to-held-out
CAP4 gap:

0.0022510884009005042.

Old prediction drift:

0.

Old decoder change:

0.

Geometry growth:

1 / 8
=
12.5%.

New capability:

9 decoder scalars.

New-cap residual compute:

18:
operations.

Old-cap residual compute:

remains:
16.

Classification:

ROBUST_MICROPATCH.

All:
frozen PATCH1 gates:

PASS.

PATCH2 — TWO NEW FACTORS

Median CAP4 held-out NMSE:

0.0029130099256414795.

Median CAP4 gap
versus:
JOINT_REFIT8:

-0.00599850263378141.

Median:
world-mean gap:

-0.002310317467609388.

Old prediction drift:

0.

Old decoder change:

0.

Classification:

ROBUST_MICROPATCH.

However:

PATCH2
uses:

25%:
shared geometry growth

versus:

12.5%
for:
PATCH1.

Since:

PATCH1
already:
passes:
all:
quality
and:
preservation gates,

PATCH1 is:

the preferred:
minimum:
micropatch.

PATCH FACTOR GEOMETRY

PATCH1:
scale-slot selections
across:
12 worlds:

sigma 0.22:
9.

sigma 0.44:
2.

sigma 0.88:
1.

Median:
distance:
from:
the nearest:
existing:
CORE3 factor center:

0.4085611334217505.

Only:

8.33%

of:
PATCH1 factors

are:
exact candidate matches
to:
the:
JOINT_REFIT8:
support.

Thus:

the successful:
micropatch

does NOT:
simply:
recover:
one:
obvious factor
from:
the:
fully reoptimized:
joint support.

Instead:

it finds:
a:
new-capability-local:
increment

that:
works:
alongside:
the old:
frozen core.

PRESERVATION

For:
all:
old capabilities:

maximum decoder change:

0.

Maximum prediction drift:

0.

This is:

exact:
non-regression.

TECHNICAL INTERPRETATION

P7 resolves:
the central:
P6 failure
with:
the smallest:
allowed:
structural growth.

The result supports:

BOUNDED:
INCREMENTAL:
SHARED-CORE:
MICROPATCHING.

A:
three-capability:
shared core

does NOT:
need:
full:
geometry reorganization

when:
CAP4 arrives.

Instead:

one:
new:
fixed-dictionary:
factor

recruited:
from:
the:
new capability's:
own:
unlabeled:
distillation residual

is:
sufficient
on:
the:
median

to:
repair:
the newcomer

while:

- old factors:
  remain frozen;
- old decoders:
  remain frozen;
- old predictions:
  remain exact;
- old per-query residual compute:
  remains unchanged;
- shared geometry:
  grows only:
  12.5%.

This is:

a direct:
mechanical analogue
of:
developmental:
micropatching.

IMPORTANT LIMIT

P7 tests:

only:
the:
first:
new capability.

It does NOT:
show:

that:
one-factor patches

remain:
sufficient
through:
many:
sequential:
capability additions.

The next:
critical question

is:

whether:
small patches
can:
accumulate

without:

- patch-count explosion;
- old-state drift;
- uncontrolled active compute;
- eventual:
  need:
  for:
  global:
  shared-core replacement.

NEXT JUSTIFIED EXPERIMENT

H191-P8 —
SEQUENTIAL:
BOUNDED:
SHARED-CORE:
MICROPATCH
SCALING.

Start:
CORE3.

For:
each:
new:
capability
in:
3,
4,
5,
6,
7:

first:
attempt:
decoder-only
on:
the:
current:
shared core.

If:
the:
new capability's:
distillation fit
fails:
a frozen:
predeclared:
trigger,

allow:

at most:

ONE:
new:
fixed-dictionary:
factor

for:
that capability.

Then:

freeze:
that factor.

Extend:
all:
older:
capability decoders
with:
implicit:
zero
for:
the new factor.

Never:

- move:
  existing factors;
- delete:
  factors;
- refit:
  old decoder coefficients.

Measure:

- number:
  of:
  factors:
  actually added;
- total:
  factor growth;
- new-capability:
  held-out fidelity;
- old prediction drift;
- per-query compute:
  old versus:
  newest capability;
- cumulative:
  shared-core size;
- gap:
  versus:
  fresh:
  JOINT_REFIT
  reference.

Primary North-Star question:

does:
shared coordination structure

grow:

SUBLINEARLY

relative to:

capability count

under:
sequential:
developmental:
micropatching?

PLAIN-SPEAK SUMMARY

What did we try?

The frozen:
three-capability:
core
could not:
handle:
the fourth capability
well enough.

So:
instead of:
rebuilding:
the whole core,

we let it:
grow:
one:
new shared factor.

Nothing old
was allowed:
to move.

What happened?

One:
new factor
was enough.

The new capability's:
median error
fell from:

about:
8.8%

to:

about:
0.55%.

The:
freshly rebuilt:
joint reference
was:
about:
1.33%.

So:
the one-factor patch
was:
at least:
as good
on:
the median

without:
reorganizing:
the old core.

Did it work?

Yes.

One factor:
passed:
all:
the frozen:
micropatch criteria.

The:
second:
factor
helped further,

but:
was:
not necessary.

What did we actually learn?

The P6 problem
was:
not:
that:
the whole:
shared core
had become:
obsolete.

It was:

missing:
a:
small:
piece
of:
geometry

for:
the newcomer.

Adding:
that:
small piece
fixed:
the newcomer

while:
leaving:
everything old
exactly:
unchanged.

Why does it matter?

This is:
much closer
to:
the developmental behavior
Yggdrasil is:
trying to achieve.

Instead of:
retraining:
the organism
or:
building:
a:
new:
mini-network

for:
every:
new capability,

the architecture
can:

keep:
what it already knows

and:
grow:
a:
tiny:
structural patch

only:
where:
the:
existing body
is:
insufficient.

What should we try next?

Repeat:
this:
developmentally.

Add:
capability 5,
then:
6,
then:
7,
then:
8.

At:
each step:

try:
the:
existing core
first.

Only:
grow:
one:
new factor
when:
the:
new capability
actually:
needs it.

Then:
measure:

whether:
the:
shared core
grows:
slower
than:
the:
number of:
capabilities.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
