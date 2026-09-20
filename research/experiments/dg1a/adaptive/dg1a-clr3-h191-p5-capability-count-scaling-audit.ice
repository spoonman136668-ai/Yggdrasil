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


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P5 CAPABILITY-COUNT HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P5 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p5_capability_count_scaling_v1.py

Harness commit:

9f66f4589c1879188334550adc4e7cace57493bc.

Git blob SHA:

85407e300382d8c918c2d51156582a5d69444e2f.

Source SHA-256:

b832f2a9030fae786e18f596360c4ed4eb880048336e5043373a76e1119ab87c.

Source bytes:

12707.

DEPENDENCY

Frozen H191-P0 helper harness Git blob:

6ac31f5cc3e091be7ef24ea74879903dd21cc2fa.

Pinned P0 source SHA-256:

da6643d35ae6bd5256d400d219702e37ed379ac867ea81583acd2986fa45eabb.

FROZEN CONDITIONS

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

6 worlds per condition.
30 worlds total.

Shared source factors:
8.

DICT8 shared factor count:
8.

Fixed scales:
0.22,
0.44,
0.88.

Context radius:
0.60.

Context sd:
0.14.

REPRODUCIBILITY

Execute:
two complete 30-world sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P5 NON-EVIDENCE PILOT CLOSURE — CAPABILITY-COUNT SCALING

DATE:
2026-09-20.

STATUS:
COMPLETE / POSITIVE CAPABILITY-SCALING RESULT /
DICT8 ROBUST THROUGH CAP8 /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

b832f2a9030fae786e18f596360c4ed4eb880048336e5043373a76e1119ab87c.

CANONICAL OUTPUT

RUN 1 SHA-256:

32565fd836f67da19798e3c3138466f8448660aab7be8eb9bc253db924ef0b24.

RUN 2 SHA-256:

32565fd836f67da19798e3c3138466f8448660aab7be8eb9bc253db924ef0b24.

Byte-identical:

PASS.

MECHANICAL RESULT

DICT8 remains:

ROBUST

at:

CAP3,
CAP4,
CAP5,
CAP6,
and:
CAP8.

No:
TRANSITION
or:
OVER-CAPACITY
condition
was reached.

CAP3

PROXY8
median world-mean NMSE:

0.04916488473771472.

DICT8:

0.011911339922129607.

Paired median delta:

-0.03749456153458612.

Win rate:

83.33%.

CAP4

PROXY8:

0.038427543982785806.

DICT8:

0.014047568006810965.

Paired median delta:

-0.018264385068262858.

Win rate:

100%.

CAP5

PROXY8:

0.03972977147828376.

DICT8:

0.029652565122721162.

Paired median delta:

-0.016772129555774666.

Win rate:

83.33%.

CAP6

PROXY8:

0.030613119359411238.

DICT8:

0.024245175325622877.

Paired median delta:

-0.01223530621397731.

Win rate:

83.33%.

CAP8

PROXY8:

0.020300520369964.

DICT8:

0.013000500876131603.

Paired median delta:

-0.006592096587869552.

Win rate:

83.33%.

CAP8 WORST-CAPABILITY TELEMETRY

Median:
world worst-capability NMSE:

PROXY8:

0.04063982752973476.

DICT8:

0.03968481035919817.

P90:

PROXY8:

0.08878713451595702.

DICT8:

0.051714471734825.

Thus:

the:
shared-core advantage
does NOT:
come only from:
averaging away:
one badly served capability.

MEMORY SCALING

Learned decoder scalars:

CAP3:
24.

CAP4:
32.

CAP5:
40.

CAP6:
48.

CAP8:
64.

This is:

exactly:
8:
new learned decoder coefficients
per:
additional capability.

DICT8 shared geometry metadata:

remains:

8 site IDs
+
8 scale slots

at:
every capability count.

PROXY8 geometry metadata:

grows:

24,
32,
40,
48,
64:
site IDs.

PER-QUERY RESIDUAL COMPUTE

DICT8:

16 operations

at:
CAP3
through:
CAP8.

PROXY8:

also:
16 operations

for:
one selected capability,

but:
with:
separate per-capability support geometry.

Thus:

the:
shared structural coordination core

stays:
constant-size
and:
constant-active-compute

while:

capability-specific decoder memory
grows:
linearly.

SHARING TELEMETRY

DICT8:
effective decoder participation median:

CAP3:
1.6797415068272223.

CAP4:
2.52429299441836.

CAP5:
2.756901423033268.

CAP6:
3.0854940687769883.

CAP8:
4.634632966535009.

Decoder concentration median:

CAP3:
0.7407498344304928.

CAP4:
0.5515515692203633.

CAP5:
0.5216409775296245.

CAP6:
0.48389156882571005.

CAP8:
0.3672319321515812.

Interpret cautiously:

the metric's scale
changes naturally
as:
capability count increases.

However:

the selected factors
do NOT:
collapse
into:
single-capability ownership.

GENERALIZATION

DICT8:
median distillation-to-held-out
mean NMSE gap:

CAP3:
0.005428825553493338.

CAP4:
0.002859007532959452.

CAP5:
0.010260561048714405.

CAP6:
0.0070969609105704.

CAP8:
0.0037610740371577123.

No:
gross generalization failure
appears.

IMPORTANT INTERPRETATION LIMIT

The condition seed families
are:
disjoint.

Therefore:

do NOT:
interpret:
the absolute NMSE sequence
across:
CAP3..CAP8

as:
a monotonic:
difficulty curve.

The supported conclusion is:

within:
every preregistered:
capability-count condition,

DICT8 remained:
mechanically ROBUST
relative to:
PROXY8

while:
shared support size
and:
per-query residual compute
stayed:
fixed.

TECHNICAL INTERPRETATION

P5 supplies:
a stronger:
scaling signal
than:
P4.

P4 showed:

shared residual complexity
can:
rise
without:
forcing:
shared factor-count growth.

P5 shows:

capability count
can:
also rise

while:

shared factor geometry:
remains:
8 factors,

per-query factor compute:
remains:
16 operations,

and:
only:
capability-specific decoder state
grows.

This is:

the desired:
separation

between:

SHARED COORDINATION STRUCTURE

and:

CAPABILITY-SPECIFIC MEMORY.

But:

P5 still:
jointly recruits
the shared DICT8 support
using:
all capabilities
present
in:
each condition.

Therefore:

it does NOT:
yet demonstrate:
developmental addition
into:
a frozen:
existing:
shared core.

NEXT JUSTIFIED EXPERIMENT

H191-P6 —
FROZEN SHARED-CORE
CAPABILITY ADDITION.

Procedure:

1.
Recruit:
DICT8
on:
an initial:
three-capability set.

2.
Freeze:

- 8 site IDs;
- 8 scale slots;
- old capability decoders.

3.
Introduce:
capability 4,
then:
5,
then:
6,
then:
8.

4.
For:
each new capability,

fit ONLY:

its:
new:
8-coefficient decoder.

5.
No:
shared-support re-recruitment.

6.
No:
old-decoder refit.

Measure:

- new-capability fidelity;
- old-capability exact preservation;
- gap versus:
  jointly recruited:
  DICT8 reference;
- incremental memory:
  +8 scalars/capability;
- geometry growth:
  zero;
- per-query residual compute:
  constant 16.

This is:
the developmental:
shared-core test
that:
P5 now justifies.

PLAIN-SPEAK SUMMARY

What did we try?

We stopped:
making three capabilities
more complicated

and instead:
gave the system:
more capabilities.

We tested:
3,
4,
5,
6,
and:
8
different capability contexts.

The shared core
was always limited to:
the same eight factors.

What happened?

It held up.

At every tested capability count,
the shared DICT8 representation
was still:
better overall
than:
giving every capability
its own:
eight-site PROXY8 cache.

Did it work?

Yes,
for:
this non-evidence pilot.

We reached:
eight capabilities
without:
growing:
the shared factor geometry
or:
the per-query residual compute.

What did we actually learn?

The part of the system
that describes:
shared coordination

does not:
have to grow
one-for-one
with:
capability count

in:
this tested regime.

The only thing
that had to grow
was:
the small:
eight-number decoder
for:
each new capability.

Why does it matter?

That is:
much closer
to:
the Yggdrasil end goal.

Instead of:
building:
another mini-network
every time:
the organism learns:
something new,

the system can:
reuse:
one:
small:
shared structural core

and add:
compact:
capability-specific state.

What should we try next?

Make the test:
developmental.

Build:
the shared core
using:
only the first:
three capabilities.

Then:
freeze it.

After that,
add:
new capabilities
without:
letting:
the old core
move.

If:
the newcomers
can still:
plug in
by learning:
only:
their own:
small decoder,

that would be:
a much stronger:
proof-of-mechanism
for:
incremental cognitive growth.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
