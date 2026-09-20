TITLE: DG-1A-CLR3-H191-P9 — Out-of-Distribution Capability Insertion / Elastic Core Expansion Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE OOD DEVELOPMENTAL PILOT / NOT H191 PRIMARY
TRACK: DG-1 / DEVELOPMENTAL NOVELTY / ELASTIC SHARED-CORE EXPANSION
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p8-sequential-triggered-micropatch-scaling-audit.ice

PURPOSE

P8 established:

- sequential triggered micropatching
  can:
  add capabilities 3..7;
- all addition stages:
  remain ROBUST;
- old decoder coefficients:
  remain exact;
- old predictions:
  remain exact;
- median:
  4 new factors
  are added:
  for:
  5 new capabilities;
- shared geometry reuse is:
  positive,
  but:
  not strongly sublinear.

P9 asks a different question:

CAN:
THE:
DEVELOPED:
SHARED CORE

ABSORB:
A:
GENUINELY:
OUT-OF-DISTRIBUTION:
CAPABILITY

WITH:
ONLY:
ONE
OR:
TWO:
ADDITIONAL:
FIXED-DICTIONARY FACTORS?

BOUNDARY

NON-EVIDENCE synthetic OOD developmental pilot only.

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

IN-DISTRIBUTION DEVELOPMENTAL BASE

Each P9 world first develops:

capabilities:
0..7

using:
the exact:
P8 rule.

Initial:
CORE3.

Sequential additions:

3,
4,
5,
6,
7.

Trigger:

decoder-only:
distillation NMSE
>0.02.

Patch ceiling:

one:
new factor
per:
in-distribution:
new capability.

All:
old factors
and:
old decoder coefficients
remain:
frozen.

Thus:

P9 OOD insertion
starts from:
an actually:
developed:
P8-style core,

not:
a freshly:
jointly optimized:
eight-capability core.

OOD CAPABILITY

New capability ID:

8.

This is:
the ninth:
total capability.

OOD CONTEXT GEOMETRY

Original:
capabilities 0..7

remain:
the:
radius-0.60:
ring contexts

with:
sd:
0.14.

Capability 8:

center:

(0.0, 0.0).

sd:

0.10.

Accept:
only:
points
with:

radius <=0.30.

Thus:

capability 8
occupies:
the:
central:
region

rather than:
the:
original:
ring-context:
regime.

OOD RESIDUAL FAMILY

All:
nine capabilities
share:

the same:
8:
hidden Gaussian:
source factors
within:
each world.

Source centers:

uniform unit disk.

Source sigma:

uniform:
[0.12,0.42].

Decoder matrix:

8 x 9.

N(0,1).

For:
capabilities 0..7:

capability-specific:
sinusoidal remainder

uses:
the exact:
P5/P8:

frequency:
wx,
wy
uniform [1,4].

For:
OOD capability 8:

same:
remainder amplitude:

0.10,

but:

wx,
wy
uniform:

[5,8].

Thus:

OOD novelty
changes:

- context geometry;
- local residual frequency;

while:

preserving:
the same:
shared Gaussian:
source family.

DATA

Per capability:

128:
unlabeled distillation coordinates.

512:
held-out coordinates.

OOD INSERTION POLICIES

Let:

F

be:
the number:
of:
shared factors

after:
P8-style:
capabilities 0..7
have developed.

PATCH0

Fit:
capability 8 decoder

over:
the:
existing:
F-factor:
developed core.

No:
new factor.

PATCH1

Add:
exactly:
one:
new:
fixed-dictionary factor.

Candidate dictionary:

3209 parent centers
x
scale slots:

0.22,
0.44,
0.88.

Exclude:
all:
existing:
developed-core factors.

Recruit:
using:
ONLY:
capability 8:
unlabeled:
distillation residual.

Refit:
ONLY:
capability 8 decoder.

Old:
factors:
frozen.

Old:
decoder coefficients:
frozen.

PATCH2

Nested from:
PATCH1.

Add:
exactly:
one:
additional:
fixed-dictionary factor.

Refit:
ONLY:
capability 8 decoder.

Maximum:
OOD geometry expansion:

2 factors.

No:
replacement.

No:
deletion.

No:
old-factor movement.

OOD_LOCAL8 REFERENCE

Recruit:

8:
fresh:
fixed-dictionary:
factors

using:
ONLY:
capability 8:
distillation data.

Fit:
capability 8 decoder.

This is:

an:
expressivity ceiling
for:
the:
existing:
fixed:
0.22 / 0.44 / 0.88:
dictionary family

under:
an:
8-factor:
new-capability-local budget.

If:
OOD_LOCAL8
itself:
fails badly,

the result indicates:

DICTIONARY FAMILY LIMIT,

not:
merely:
insufficient:
elastic patch count.

JOINT_REFIT8 REFERENCE

Also:
recruit:
fresh:
8-factor DICT8

jointly
using:
all:
capabilities 0..8.

Reference only.

PRESERVATION

For:
capabilities 0..7:

all:
previously frozen:
decoder coefficients
must:
remain unchanged.

All:
old predictions
must:
remain unchanged
within:
normalized drift:

<=1e-12.

Old:
per-query active support
must:
remain:
at:
its:
birth-time:
factor count.

RESOURCE ACCOUNTING

PATCH0:

OOD decoder scalars:

F.

OOD residual ops:

2F.

PATCH1:

OOD decoder scalars:

F+1.

OOD residual ops:

2(F+1).

Shared factor growth:

+1.

PATCH2:

OOD decoder scalars:

F+2.

OOD residual ops:

2(F+2).

Shared factor growth:

+2.

All:
old-capability:
residual ops:

unchanged.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260925000000
through:
20260925000007.

No:
P0-P8
seed reuse.

PRIMARY METRICS

Pre-OOD developed core:

- in-distribution patch count;
- developed shared factor count;
- old capability residual ops.

For:
PATCH0,
PATCH1,
PATCH2,
OOD_LOCAL8,
JOINT_REFIT8:

- OOD distillation NMSE;
- OOD held-out NMSE.

For:
PATCH0/1/2:

- nine-capability:
  world mean NMSE;
- world worst NMSE;
- old prediction drift;
- old decoder change;
- OOD generalization gap;
- OOD error reduction
  versus:
  PATCH0;
- OOD gap
  versus:
  OOD_LOCAL8;
- OOD gap
  versus:
  JOINT_REFIT8.

Patch geometry:

- candidate IDs;
- scale slots;
- distance:
  to:
  nearest:
  prepatch factor center;
- exact overlap:
  with:
  OOD_LOCAL8 support;
- exact overlap:
  with:
  JOINT_REFIT8 support.

FROZEN INTERPRETATION

First classify:
the dictionary family.

DICTIONARY CAPABLE

if:

median:
OOD_LOCAL8
held-out NMSE

<=0.05.

DICTIONARY FAMILY LIMIT

if:

median:
OOD_LOCAL8
held-out NMSE

>0.05.

If:
the dictionary is capable:

PATCH1 is:
ROBUST ELASTIC

if:

1.
median:
PATCH1:
OOD held-out NMSE
<=0.05;

2.
median:
PATCH1:
OOD error reduction
versus:
PATCH0
>=50%;

3.
median:
PATCH1 gap
versus:
OOD_LOCAL8
<=0.04;

4.
old prediction drift
<=1e-12;

5.
old decoder change
=
0;

6.
median:
PATCH1:
OOD distillation-to-held-out gap
<=0.05.

PATCH2 is:
ROBUST ELASTIC
under:
the same gates

if:
PATCH1
does not:
pass.

PATCH1:
preferred
if:
it passes.

PATCH-BUDGET LIMIT

if:

OOD_LOCAL8:
passes:
dictionary-capable gate

but:

PATCH2:
OOD held-out NMSE
>0.05

or:

PATCH2:
gap:
versus:
OOD_LOCAL8
>0.04.

MIXED

otherwise.

REPRODUCIBILITY

Two:
complete:
8-world:
P8-development
plus:
OOD-insertion sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P9 world,

do not alter:

- P8 developmental trigger;
- P8 one-factor ceiling;
- OOD center;
- OOD sd;
- OOD radius cutoff;
- OOD frequency range;
- OOD remainder amplitude;
- fixed dictionary;
- scale slots;
- OOD patch budgets;
- ridge;
- world family;
- metrics;
- thresholds.

NEXT

If:
PATCH1
or:
PATCH2
is:
ROBUST ELASTIC,

proceed to:
repeated:
OOD insertions
and:
test:
whether:
elastic patches
remain:
bounded.

If:
PATCH-BUDGET LIMIT,

test:
localized:
factor adaptation
or:
bounded:
factor replacement.

If:
DICTIONARY FAMILY LIMIT,

the next:
architectural question
is:
whether:
new:
fixed scale slots
can:
be:
developmentally:
added

without:
changing:
old factors.

Do NOT:
increase:
dictionary scales
inside:
P9.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
