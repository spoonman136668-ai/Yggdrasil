TITLE: DG-1A-CLR3-H191-P6 — Frozen Shared-Core Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE DEVELOPMENTAL-ADDITION PILOT / NOT H191 PRIMARY
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION / FROZEN SHARED COORDINATION CORE
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p5-capability-count-scaling-audit.ice

PURPOSE

P5 established:

DICT8 can:
serve:
3 through 8 capability contexts

while:

- shared factor geometry remains:
  8 factors;
- per-query residual compute remains:
  16 operations;
- only:
  8 decoder coefficients
  are added:
  per capability.

But:

P5 jointly re-recruited:
the shared support
for:
every capability-count condition.

P6 asks:

CAN:
NEW CAPABILITIES

JOIN:
AN EXISTING:
FROZEN:
EIGHT-FACTOR:
SHARED CORE

BY LEARNING:
ONLY:
A NEW:
8-COEFFICIENT DECODER?

BOUNDARY

NON-EVIDENCE synthetic developmental-addition pilot only.

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

FIXED WORLD GEOMETRY

Every P6 world contains:

8:
potential capability contexts

from:
the beginning.

Context centers:

8:
uniformly spaced
on:
the exact P5:
radius-0.60 ring.

Context sd:

0.14.

Ownership:

nearest:
of:
all 8:
fixed centers.

Thus:

adding:
later capabilities

does NOT:
move:
old capability distributions.

SOURCE FAMILY

Exact P5 CAP8-style source:

8:
hidden shared Gaussian factors.

Source centers:

uniform:
unit disk.

Source sigmas:

uniform:
[0.12,0.42].

Decoder matrix:

8 x 8.

Entries:

N(0,1).

Capability-specific remainder:

0.10
*
a_T
*
sin(
wx_T*x
+
wy_T*y
+
phase_T
).

Same:
P5 parameter distributions.

DATA

Per:
capability:

128:
distillation coordinates.

512:
held-out coordinates.

All:
8 capability datasets
are generated
before:
developmental staging.

INITIAL CORE

Stage:

CORE3.

Use:
capabilities:
0,
1,
2
only.

Jointly recruit:

8:
DICT8:
fixed multiscale factors

from:

3209 parent centers
x
scale slots:

0.22,
0.44,
0.88.

Then fit:

one:
8-coefficient decoder
for:
each of:
capabilities 0..2.

FREEZE

After CORE3:

freeze:

- all:
  8 selected:
  parent-site IDs;
- all:
  8 selected:
  scale slots;
- capability:
  0,
  1,
  2:
  decoders.

No:
support re-recruitment
is allowed
for:
the developmental candidate.

SEQUENTIAL ADDITION

Stages:

CAP4:
add capability 3.

CAP5:
add capability 4.

CAP6:
add capability 5.

CAP8:
add capabilities 6 and 7.

At:
each addition:

fit ONLY:

the new capability's:
8 decoder coefficients

against:

the frozen:
CORE3:
support.

Then:

freeze:
that new decoder.

At later stages:

do NOT:
refit:
any prior decoder.

Thus:

the candidate developmental path
adds:

8 learned scalars
per:
new capability

and:

ZERO:
new factor geometry.

JOINT-REFIT REFERENCE

At:
each stage:

independently:
recruit:
a fresh:
DICT8:
shared support

using:
all capabilities
present
at:
that stage.

Then:
fit:
all stage decoders.

This is:

REFERENCE ONLY.

It measures:
the cost:
of refusing:
to:
reorganize:
the shared core.

It is NOT:
the developmental candidate.

PRIMARY METRICS

Per stage:

FROZEN_CORE:

- held-out NMSE:
  per:
  active capability;

- world mean-capability NMSE;

- world worst-capability NMSE;

- new-capability NMSE;

- all-capability <=0.02;

- distillation-to-held-out gap.

JOINT_REFIT:

same:
prediction metrics.

DEVELOPMENTAL COST

Report:

FROZEN_CORE
minus:
JOINT_REFIT

for:

- world mean NMSE;
- world worst NMSE;
- newly added capabilities.

PRESERVATION

For:
every capability
that existed:
before:
a stage,

compare:

its:
frozen-core prediction

before
and:
after:
the later capability addition.

Maximum normalized prediction drift:

must be:
reported.

Because:

support
and:
old decoders
are:
frozen,

expected:

0
within:
floating-point reproducibility.

SUPPORT PRESSURE

At:
each stage:

compare:
CORE3 support
against:
the:
JOINT_REFIT support.

Report:

- exact shared candidate count;
- Jaccard overlap;
- scale-slot distribution.

This tells us:

how much:
the optimal:
shared geometry
would like:
to reorganize

even if:
the frozen candidate
still performs adequately.

MEMORY

FROZEN_CORE learned decoder scalars:

CORE3:
24.

CAP4:
32.

CAP5:
40.

CAP6:
48.

CAP8:
64.

Shared geometry metadata:

always:

8:
site IDs

+
8:
scale slots.

Geometry growth:

ZERO.

PER-QUERY RESIDUAL COMPUTE

Always:

8:
factor evaluations

+
8:
selected-capability decoder multiply-adds

=
16:
operations.

No:
other capability decoder
needs:
evaluation.

WORLD FAMILY

6:
disjoint worlds.

Seeds:

20260924700000
through:
20260924700005.

Each:
single world
contains:
all:
8 potential capabilities

and:
all:
developmental stages.

No:
P0-P5
seed reuse.

FROZEN PILOT CRITERIA

Per:
CAP4,
CAP5,
CAP6,
CAP8:

ROBUST developmental reuse
if:

1.
Median:
FROZEN_CORE minus JOINT_REFIT
world-mean NMSE

<=0.02.

2.
Median:
new-capability:
FROZEN_CORE minus JOINT_REFIT
NMSE

<=0.03.

3.
Median:
new-capability:
FROZEN_CORE
held-out NMSE

<=0.05.

4.
Maximum:
old-capability:
prediction drift

<=1e-12.

5.
Geometry growth:

0.

6.
Per-query residual compute:

16.

TRANSITION:

world-mean gap:
>0.02
but:
<=0.05

OR:

new-capability gap:
>0.03
but:
<=0.07.

OVER-CAPACITY:

world-mean gap:
>0.05

AND:

new-capability gap:
>0.07.

If:
a stage
falls outside:
these exact combinations,

report:

MIXED_UNCLASSIFIED.

REPRODUCIBILITY

Two:
complete:
6-world:
all-stage sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P6 world,

do not alter:

- CORE3 capability identities;
- 8-context geometry;
- source family;
- factor rank;
- factor scales;
- recruitment;
- ridge;
- addition order;
- stage definitions;
- thresholds;
- seeds.

NEXT

If:
FROZEN_CORE
remains:
ROBUST
through:
CAP8,

the next experiment
should:
introduce:
a capability
whose geometry
is:
deliberately:
out-of-distribution
relative to:
the original:
CORE3 support.

That would test:
whether:
bounded:
shared-core expansion
is needed
and:
whether:
one or two:
new factors
can be:
micropatched
without:
retraining:
the old core.

If:
a transition
appears
before:
CAP8,

that stage
becomes:
the first:
developmental shared-core
capacity boundary.

Do NOT:
expand:
the factor core
inside:
P6.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P6 FROZEN SHARED-CORE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P6 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p6_frozen_shared_core_addition_v1.py

Harness commit:

b7d23c935d0656fc535b3212dfd66ee49c89d4cc.

Git blob SHA:

6e945c8a6d5ac1f1891ce79945717acd1192a5c6.

Source SHA-256:

8460bdef124a1d42f9e338249fbbbf99c88e85494bea35a56ecc7530cfc1d31e.

Source bytes:

13772.

DEPENDENCY

Frozen H191-P5 harness Git blob:

85407e300382d8c918c2d51156582a5d69444e2f.

Pinned P5 source SHA-256:

b832f2a9030fae786e18f596360c4ed4eb880048336e5043373a76e1119ab87c.

P5 transitively pins:

H191-P0 helper blob:

6ac31f5cc3e091be7ef24ea74879903dd21cc2fa.

FROZEN WORLD FAMILY

20260924700000..20260924700005.

6 worlds.

Every world contains:
all 8 potential capability datasets
before:
CORE3 recruitment.

FROZEN DEVELOPMENTAL STAGES

CORE3:
0,1,2.

CAP4:
add 3.

CAP5:
add 4.

CAP6:
add 5.

CAP8:
add 6 and 7.

Candidate developmental core:

support:
frozen after CORE3.

Old decoders:
frozen after first fit.

Only:
new 8-coefficient decoders
may be added.

JOINT_REFIT:

reference only.

REPRODUCIBILITY

Execute:
two complete:
6-world:
all-stage sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
