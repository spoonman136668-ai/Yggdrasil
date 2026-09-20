TITLE: DG-1A-CLR3-H191-P8 — Sequential Triggered Shared-Core Micropatch Scaling Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE SEQUENTIAL DEVELOPMENTAL PILOT / NOT H191 PRIMARY
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION / TRIGGERED SHARED-CORE GROWTH
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p7-bounded-shared-core-factor-micropatch-audit.ice

PURPOSE

P7 established:

- decoder-only CAP4 addition is unreliable;
- one fixed-dictionary factor is sufficient to repair CAP4 on the median;
- old factors remain frozen;
- old decoder coefficients remain frozen;
- old predictions remain exact;
- PATCH1 is preferred over PATCH2.

P8 asks:

CAN:
THAT:
ONE-FACTOR:
MICROPATCH RULE

BE:
APPLIED:
SEQUENTIALLY

WITHOUT:
ADDING:
A NEW FACTOR
FOR:
EVERY:
NEW CAPABILITY?

BOUNDARY

NON-EVIDENCE synthetic developmental pilot only.

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

Exact P6/P7 geometry.

Every world contains:
8 potential capability contexts
from the beginning.

Context centers:
8 equally spaced points
on radius 0.60.

Context sd:
0.14.

Context ownership:
nearest of all 8 fixed centers.

SOURCE FAMILY

Exact P6/P7 source:

8 hidden shared Gaussian factors.

Source centers:
uniform unit disk.

Source sigmas:
uniform [0.12,0.42].

Decoder matrix:
8 x 8,
N(0,1).

Capability-specific remainder:
0.10 sinusoidal component
with exact P5 distributions.

DATA

Per capability:

128:
unlabeled distillation coordinates.

512:
held-out coordinates.

CORE3

Use capabilities:
0,
1,
2.

Recruit:
8 fixed multiscale DICT8 factors.

Fit:
old capability decoders.

Freeze:

- all 8 factor identities;
- all 8 scale slots;
- capability 0/1/2 decoder coefficients.

SEQUENTIAL ADDITION ORDER

Add:

capability 3,
then:
4,
then:
5,
then:
6,
then:
7.

At every addition:

STEP 1 — DECODER-ONLY ATTEMPT

Fit:
the new capability decoder
over:
the current shared factor set.

Use:
only:
the new capability's:
unlabeled distillation residual.

Compute:
new-capability:
distillation NMSE.

FROZEN PATCH TRIGGER

If:

decoder-only:
distillation NMSE
<=0.02,

do NOT:
grow:
the shared core.

Freeze:
the new decoder
as-is.

If:

decoder-only:
distillation NMSE
>0.02,

permit:

exactly:
ONE:
new:
fixed-dictionary factor.

No second factor
is allowed
inside:
P8.

PATCH RECRUITMENT

Candidate dictionary:

3209 parent centers
x
fixed scales:

0.22,
0.44,
0.88.

Exclude:

all factors
already present
in:
the shared core.

For:
each candidate:

append:
that candidate

and:
ridge-refit:
ONLY:
the new capability decoder.

Score:

new capability:
normalized:
distillation MSE.

Choose:

lowest score.

Tie:

candidate order.

Then:

freeze:
the selected new factor

and:
the new capability decoder.

OLD STATE

When:
a new factor
is appended,

every:
older capability decoder

receives:

implicit:
zero:
coefficient

for:
that new factor.

Do NOT:

- refit:
  old coefficients;
- move:
  old factors;
- delete:
  old factors;
- replace:
  old factors.

Therefore:

old predictions
must:
remain:
exact.

CAPABILITY-SPECIFIC ACTIVE SUPPORT

A capability evaluates:

only:
the factors
that existed
when:
its decoder
was frozen.

Future factors have:
exact:
zero contribution

and:
need not:
be evaluated
for:
that older capability.

Thus:

old per-query residual compute
does NOT:
increase
when:
later patches are added.

JOINT_REFIT8 REFERENCE

At:
each stage,

independently:
recruit:
a fresh:
8-factor DICT8 support

using:
all capabilities
currently active.

Fit:
all stage decoders.

Reference only.

This measures:
the quality cost
of:
incremental:
immutable-core development.

WORLD FAMILY

8:
disjoint worlds.

Seeds:

20260924900000
through:
20260924900007.

No:
P0-P7
seed reuse.

PRIMARY METRICS

Per stage:

- patch trigger rate;
- cumulative patch count;
- cumulative shared factor count;
- new-capability decoder-only distillation NMSE;
- post-rule new-capability distillation NMSE;
- post-rule new-capability held-out NMSE;
- world mean held-out NMSE;
- world worst held-out NMSE;
- gap versus JOINT_REFIT8:
  new capability;
- gap versus JOINT_REFIT8:
  world mean;
- old prediction drift;
- old decoder coefficient change;
- per-capability active factor count;
- per-capability residual compute;
- cumulative shared geometry metadata.

PATCH TELEMETRY

For every added factor:

- triggering capability;
- candidate ID;
- parent-site ID;
- scale slot;
- distance to nearest pre-patch factor center;
- whether candidate appears in:
  same-stage JOINT_REFIT8 support.

SCALING TELEMETRY

At final CAP8:

report:
per world:

- total new factors added
  beyond:
  CORE3;
- final shared factor count;
- factor additions / 5 new capabilities;
- oldest capability residual compute;
- newest capability residual compute.

FROZEN PILOT INTERPRETATION

STAGE ROBUST

if:

1.
median:
post-rule new-capability held-out NMSE
<=0.05;

2.
median:
new-capability gap
versus:
JOINT_REFIT8
<=0.04;

3.
median:
world-mean gap
versus:
JOINT_REFIT8
<=0.03;

4.
old prediction drift
<=1e-12;

5.
old decoder change
=
0.

STAGE TRANSITION

if:

new-capability gap:
>0.04
but:
<=0.08

OR:

world-mean gap:
>0.03
but:
<=0.06.

STAGE OVER-CAPACITY

if:

new-capability gap:
>0.08

AND:

world-mean gap:
>0.06.

Otherwise:

MIXED_UNCLASSIFIED.

SEQUENTIAL SCALING ENCOURAGEMENT

P8 supports:
bounded sequential micropatching

if:

- CAP4,
  CAP5,
  CAP6,
  CAP7,
  CAP8
  all:
  avoid:
  OVER-CAPACITY;

- old prediction drift:
  remains:
  <=1e-12;

- old decoder changes:
  remain:
  zero;

AND:

median:
total patch count
after:
five:
new capabilities

<
5.

This finite pilot
does NOT:
prove:
asymptotic sublinear growth.

It only tests:
whether:
factor addition
is:
less than:
one-for-one
over:
this sequence.

STRONG MECHANICAL SIGNAL

if:

all stages:
ROBUST

AND:

median:
final patch count
<=3.

RESOURCE ACCOUNTING

CORE3:

8 factors.

If:
P:
patches have accumulated:

stored shared factors:

8 + P.

Capability learned at:
shared factor count F
stores:

F:
decoder coefficients.

Older capabilities:

retain:
their:
birth-time:
decoder length

with:
implicit:
zeros
for:
future factors.

Per-query residual compute:

2 * birth-time factor count.

Thus:

resource growth
is:
measured:
per capability

rather than:
charging:
all later factors
to:
all old capabilities.

REPRODUCIBILITY

Two:
complete:
8-world:
all-stage sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P8 world,

do not alter:

- trigger 0.02;
- one-factor patch ceiling;
- candidate dictionary;
- factor scales;
- recruitment;
- ridge;
- capability order;
- source family;
- geometry;
- world family;
- metrics;
- thresholds.

NEXT

If:
P8 shows:
bounded:
less-than-one-for-one
patch growth,

proceed to:

H191-P9 —
OUT-OF-DISTRIBUTION
CAPABILITY INSERTION
AND:
ELASTIC CORE EXPANSION.

If:
P8 requires:
one factor
for:
essentially:
every new capability,

the shared core
is:
not:
showing:
the desired:
developmental reuse
under:
this geometry.

If:
P8 reaches:
OVER-CAPACITY,

do NOT:
increase:
the patch ceiling
inside:
P8.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P8 SEQUENTIAL TRIGGERED MICROPATCH HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P8 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p8_sequential_triggered_micropatch_v1.py

Harness commit:

b4d6b0bb28b7b85e6d7605838070a382979fc5c7.

Git blob SHA:

cd0ad363f6bf515f584ba3aaef8ff519dc728fa3.

Source SHA-256:

007644e97e88f6c1e178bbaddb6357804401dd1dc5c872fb93c427c2d071672f.

Source bytes:

13298.

DEPENDENCY

Frozen H191-P7 harness Git blob:

d39ae30800b27e9ddc65802026d41aa4d6dc973d.

Pinned P7 source SHA-256:

575471bf0c8bea2e62a7f8e80a6803c5c135f5173f8b7b3c5829ad03044f816a.

FROZEN WORLD FAMILY

20260924900000..20260924900007.

8 worlds.

FROZEN ADDITION ORDER

3,
4,
5,
6,
7.

FROZEN PATCH TRIGGER

decoder-only:
new-capability:
distillation NMSE

>0.02.

Patch ceiling:

exactly:
one factor
per:
new capability.

If:
trigger not crossed,

no:
factor growth.

REPRODUCIBILITY

Execute:
two complete:
8-world:
all-stage sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
