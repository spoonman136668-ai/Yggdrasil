TITLE: DG-1A-CLR3-H191-P5 — Fixed DICT8 Capability-Count Scaling Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE CAPABILITY-SCALING PILOT / NOT H191 PRIMARY
TRACK: DG-1 / CAPABILITY HIBERNATION / SHARED COORDINATION SCALING
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p4-dict8-capacity-stress-audit.ice

PURPOSE

P3 established:
a positive fixed-multiscale DICT8 design.

P4 established:
DICT8 remains mechanically ROBUST
as hidden shared residual-source complexity rises
from:
4
through:
12
generating factors.

P5 changes the scaling axis.

QUESTION

CAN:
ONE:
FIXED-SIZE:
EIGHT-FACTOR:
SHARED RESIDUAL CORE

SERVE:
AN INCREASING NUMBER
OF:
CAPABILITY CONTEXTS

WITHOUT:
GROWING:
SHARED FACTOR GEOMETRY
OR:
PER-QUERY FACTOR COMPUTE?

BOUNDARY

NON-EVIDENCE synthetic capability-scaling pilot only.

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

FIXED DICT8 ARCHITECTURE

Parent centers:

3209.

Fixed scale slots:

0.22,
0.44,
0.88.

Candidate dictionary:

3209 * 3
=
9627:
fixed:
(center, scale)
factors.

Jointly recruit:

8:
shared factors.

No:
rank growth.
No:
new scale.
No:
learned center.
No:
learned sigma.
No:
new physical cell.

CAPABILITY-COUNT CONDITIONS

CAP3.
CAP4.
CAP5.
CAP6.
CAP8.

The shared factor count:

remains:
8
for:
all conditions.

CONTEXT GEOMETRY

For:
K capabilities,

place:
K context centers
uniformly
around:
a radius-0.60 ring
inside:
the unit disk.

Center i:

angle:
2*pi*i/K.

Coordinate distribution:

2D Gaussian
around:
that center

with:

sd = 0.14.

Reject:
points outside:
the unit disk.

Also reject:
a point
unless:
its nearest:
declared context center
is:
the capability
being sampled.

This produces:
K:
non-overlapping:
Voronoi-defined:
context regions
with:
the same:
sampling rule
at:
every K.

SOURCE RESIDUAL FAMILY

Shared source complexity:

8:
hidden Gaussian factors.

Source centers:

uniform:
unit disk.

Source sigmas:

uniform:
[0.12,0.42].

Capability decoder matrix:

8 x K.

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

Where:

a_T:
uniform [0.5,1.5].

wx_T:
uniform [1,4].

wy_T:
uniform [1,4].

phase_T:
uniform [0,2*pi].

Per-capability residuals
are:
RMS-normalized
from:
the 128-point
distillation set
exactly as:
P0-P4.

DATA

Per:
world
per:
capability:

128:
distillation coordinates.

512:
held-out coordinates.

COMPARATORS

PROXY8

Separate:
8-site:
parent sigma=0.22
OMP cache

for:
each capability.

Learned coefficients:

8*K.

Structural site IDs:

8*K.

DICT8

One:
jointly recruited:
8-factor:
multiscale:
shared dictionary.

One:
8-coefficient decoder
per:
capability.

Learned coefficients:

8*K.

Shared structural metadata:

8:
site IDs

plus:

8:
scale slots.

Thus:

learned scalar count
grows:
linearly
with:
capability count

for:
both comparators.

But:

DICT8:
shared factor geometry
remains:
constant-size.

INFERENCE COMPUTE

For:
a selected capability
under:
DICT8:

8:
factor evaluations

+
8:
decoder multiply-adds

=
16:
sleep-residual proxy operations.

This is:

constant
with:
K.

Stored:
other capability decoders
do NOT:
need evaluation
for:
the selected context.

PROXY8:

also:
16:
residual proxy operations
for:
one selected capability,

but:
stores:
K:
separate support sets.

WORLD FAMILIES

6:
disjoint worlds
per:
condition.

CAP3:

20260924600000..20260924600005.

CAP4:

20260924610000..20260924610005.

CAP5:

20260924620000..20260924620005.

CAP6:

20260924630000..20260924630005.

CAP8:

20260924640000..20260924640005.

Total:

30:
capability-count worlds.

No:
P0-P4
seed reuse.

PRIMARY PILOT METRICS

Per condition:

PROXY8
and:
DICT8:

- median held-out NMSE
  across:
  capability-world rows;

- median:
  world mean-capability NMSE;

- P90:
  world mean-capability NMSE;

- median:
  world worst-capability NMSE;

- P90:
  world worst-capability NMSE;

- fraction:
  of worlds
  where:
  all capabilities <=0.01;

- fraction:
  all capabilities <=0.02;

- median:
  distillation-to-held-out gap.

Paired:

- DICT8 minus PROXY8
  world-mean NMSE;

- median paired delta;

- paired win rate.

Shared-state diagnostics:

- DICT8 decoder concentration;

- effective decoder participation
  per factor;

- factor center spread;

- scale-slot counts.

Memory / compute:

- learned decoder scalars = 8*K;

- DICT8 shared geometry metadata = 8 site IDs + 8 scale slots;

- PROXY8 geometry metadata = 8*K site IDs;

- DICT8 per-query residual compute = 16 operations;

- PROXY8 per-query residual compute = 16 operations.

MECHANICAL REGIME

ROBUST:

median paired DICT8-PROXY8
world-mean delta <=0

AND:

paired win rate >=50%.

TRANSITION:

median paired delta >0
but:
<=0.03

OR:

paired win rate:
25%..49.9%.

OVER-CAPACITY:

median paired delta >0.03

AND:

paired win rate <25%.

If a condition falls outside:
these exact combinations,

report:

MIXED_UNCLASSIFIED.

Worst-capability telemetry
must:
also be reported
even if:
mean performance remains robust.

REPRODUCIBILITY

Two:
complete:
30-world sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P5 world,

do not alter:

- capability counts;
- context geometry;
- context radius;
- context sd;
- source complexity;
- remainder amplitude;
- dictionary rank;
- dictionary scales;
- recruitment;
- ridge;
- comparator;
- world families;
- metrics;
- classification thresholds.

NEXT

If:
DICT8 remains:
ROBUST
through:
CAP8,

proceed to:

H191-P6 —
FROZEN SHARED-CORE
CAPABILITY ADDITION.

Recruit:
the shared support
on:
an initial capability set.

Freeze:
the eight factor locations
and:
scale slots.

Then:
add:
new capability decoders
without:
recruiting:
new factors
or:
changing:
old capability decoders.

This tests:
whether:
new capabilities
can:
join:
an existing:
shared coordination core.

If:
P5 reaches:
TRANSITION
or:
OVER-CAPACITY,

record:
the first:
capability-count boundary

and:
do NOT:
increase rank
inside:
P5.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
