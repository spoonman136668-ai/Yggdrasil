TITLE: DG-1A-CLR3-H191-P10 — Repeated OOD Insertion / Elastic Patch Reuse Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / NON-EVIDENCE REPEATED-NOVELTY PILOT / NOT H191 PRIMARY
TRACK: DG-1 / DEVELOPMENTAL NOVELTY / ELASTIC PATCH REUSE
BRANCH: dg1a-ar
PARENT_PILOT: dg1a-clr3-h191-p9-ood-capability-elastic-core-expansion-audit.ice

PURPOSE

P9 established:

- a P8-developed core can absorb one central,
  high-frequency OOD capability;
- one new fixed-dictionary factor is sufficient;
- old factors, old decoder coefficients, old predictions,
  and old active compute remain unchanged;
- the fixed 0.22 / 0.44 / 0.88 dictionary is capable.

P10 asks:

DO:
EARLIER:
OOD PATCHES

BECOME:
REUSABLE:
SHARED STRUCTURE

FOR:
LATER:
OOD CAPABILITIES,

OR:

DOES:
EACH:
NEW:
OOD CAPABILITY

REQUIRE:
ANOTHER:
NEW FACTOR?

BOUNDARY

NON-EVIDENCE synthetic repeated-novelty pilot only.

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

IN-DISTRIBUTION BASE

Every world first develops capabilities 0..7
using the exact P8 trigger rule:

- CORE3 on capabilities 0,1,2;
- additions 3,4,5,6,7;
- decoder-only attempt first;
- add exactly one factor only when
  new-capability distillation NMSE >0.02;
- old factors and old decoder coefficients remain frozen.

REPEATED OOD CAPABILITIES

Sequentially insert four OOD capabilities:

OOD8,
OOD9,
OOD10,
OOD11.

Capability IDs:

8,
9,
10,
11.

All OOD contexts occupy the inner region,
outside the original radius-0.60 ring regime.

Fixed OOD centers:

OOD8:
(0.00, 0.00).

OOD9:
(+0.18, 0.00).

OOD10:
(0.00, +0.18).

OOD11:
(-0.18, 0.00).

OOD sampling sd:

0.08.

OOD ownership:

a sampled point is accepted for one OOD capability only if
that capability center is the nearest of all four fixed OOD centers.

Also require:

global radius <=0.40.

Thus:

the repeated OOD contexts form a bounded,
partly adjacent inner-region family
that can potentially reuse earlier inner-region patches.

SOURCE FAMILY

All 12 capabilities share:

8 hidden Gaussian source factors.

Source centers:
uniform unit disk.

Source sigmas:
uniform [0.12,0.42].

Decoder matrix:

8 x 12.

Entries:
N(0,1).

Capabilities 0..7:

sinusoidal remainder frequencies:
wx,wy uniform [1,4].

OOD8..OOD11:

sinusoidal remainder frequencies:
wx,wy uniform [5,8].

Remainder amplitude:

0.10.

DATA

Per capability:

128:
unlabeled distillation coordinates.

512:
held-out coordinates.

SEQUENTIAL OOD RULE

For each new OOD capability:

1.
fit a decoder over the current shared support;

2.
compute decoder-only distillation NMSE;

3.
if NMSE <=0.02:
   add NO factor;

4.
if NMSE >0.02:
   add exactly ONE new factor
   from the frozen parent-center x scale dictionary;

5.
patch recruitment sees ONLY
   the current new capability's
   unlabeled distillation residual;

6.
freeze the new factor if added;

7.
freeze the new capability decoder;

8.
all earlier factor identities
   and earlier decoder coefficients
   remain immutable.

No:
factor replacement.
No:
factor deletion.
No:
old-decoder refit.
No:
second factor per OOD insertion.

CAPABILITY-SPECIFIC ACTIVE SUPPORT

Each capability retains:

the shared-factor set
that existed
when its decoder was frozen.

Future patch factors:

have implicit zero coefficients
and need not be evaluated
for older capabilities.

Therefore:

old active compute
must remain unchanged.

OOD_LOCAL8 REFERENCES

At each OOD insertion stage:

independently recruit:

8 fresh fixed-dictionary factors

using ONLY:

the current OOD capability's
distillation data.

This is:

the per-newcomer dictionary ceiling.

It is reference only.

WORLD FAMILY

6:
disjoint worlds.

Seeds:

20260925100000
through:
20260925100005.

No:
P0-P9
seed reuse.

PRIMARY METRICS

Per OOD stage:

- decoder-only distillation NMSE;
- patch trigger rate;
- post-rule distillation NMSE;
- post-rule held-out NMSE;
- held-out P90;
- OOD_LOCAL8 held-out NMSE;
- gap versus OOD_LOCAL8;
- error reduction versus decoder-only;
- cumulative OOD patch count;
- cumulative shared factor count;
- new-capability active factor count;
- new-capability residual ops;
- oldest capability residual ops;
- previous OOD capability residual ops;
- old prediction drift;
- old decoder change.

Patch geometry:

- factor candidate ID;
- parent-site ID;
- scale slot;
- center radius;
- nearest existing factor-center distance;
- exact overlap with the stage OOD_LOCAL8 support.

FINAL SCALING METRICS

After OOD11:

- total OOD patches added;
- total final shared factors;
- OOD patches / 4 OOD capabilities;
- factor growth beyond pre-OOD developed core;
- oldest ring-capability residual ops;
- OOD8 residual ops;
- OOD11 residual ops.

STAGE INTERPRETATION

ROBUST OOD INSERTION

if:

1.
median:
post-rule OOD held-out NMSE
<=0.05;

2.
median:
gap versus OOD_LOCAL8
<=0.04;

3.
old prediction drift
<=1e-12;

4.
old decoder change
=
0.

TRANSITION

if:

median:
OOD held-out NMSE
>0.05
but:
<=0.10

OR:

gap versus OOD_LOCAL8
>0.04
but:
<=0.08.

OVER-CAPACITY

if:

median:
OOD held-out NMSE
>0.10

AND:

gap versus OOD_LOCAL8
>0.08.

Otherwise:

MIXED_UNCLASSIFIED.

REPEATED-OOD REUSE ENCOURAGEMENT

P10 supports:
elastic patch reuse

if:

- OOD8,
  OOD9,
  OOD10,
  OOD11
  all:
  avoid OVER-CAPACITY;

- old prediction drift
  remains:
  <=1e-12;

- old decoder change
  remains:
  zero;

AND:

median:
total OOD patch count

<
4.

This finite pilot does NOT prove
asymptotic sublinear growth.

It tests only whether:

some:
later OOD capabilities

reuse:
earlier OOD patches
well enough
to avoid:
one-factor-per-novelty growth.

STRONG MECHANICAL SIGNAL

if:

all four OOD stages:
ROBUST

AND:

median:
final OOD patch count
<=2.

REPRODUCIBILITY

Two:
complete:
6-world:
P8-development
plus:
four-OOD-insertion sweeps.

Canonical output bytes
must:
match exactly.

NO POST-RUN TUNING

After:
the first P10 world,

do not alter:

- P8 trigger 0.02;
- OOD trigger 0.02;
- one-factor patch ceiling;
- OOD centers;
- OOD sd;
- OOD ownership rule;
- OOD radius cutoff;
- OOD frequency range;
- source family;
- dictionary;
- scale slots;
- ridge;
- insertion order;
- world family;
- metrics;
- thresholds.

NEXT

If:
P10 shows:
repeated OOD reuse,

the next experiment should test:

PATCH CONSOLIDATION / SLEEP-TIME MERGING

without:
changing:
waking predictions.

Question:

can:
multiple accumulated:
micropatches

be:
distilled:
into:
a smaller:
shared patch basis

during:
sleep

while:
preserving:
all:
capability predictions?

If:
P10 requires:
one patch
for:
essentially every OOD capability,

the next question becomes:

whether:
sleep-time consolidation
can:
compress:
those patches
after:
learning.

If:
P10 reaches:
OVER-CAPACITY,

test:
bounded:
two-factor:
OOD patching
or:
new fixed scale slots.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-RUN IMPLEMENTATION FREEZE 01 — H191-P10 REPEATED OOD PATCH-REUSE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE THE FIRST H191-P10 WORLD.

HARNESS

research/experiments/dg1a/adaptive/harnesses/h191_p10_repeated_ood_patch_reuse_v1.py

Harness commit:

841e9582f75edaf3707fe9ae4b1c845bf580aa9e.

Git blob SHA:

736e78364340dd355a8ecd163a2deef29edf1a2a.

Source SHA-256:

9efde966ddf02c4695462af2959555098edfdcc447e6c5c95e26c86c9540d8b4.

Source bytes:

17830.

IMPLEMENTATION FORM

Self-contained.

No:
transient parent harness
is required
for:
P10 execution.

FROZEN WORLD FAMILY

20260925100000..20260925100005.

6 worlds.

FROZEN OOD ORDER

OOD8:
(0.00,0.00).

OOD9:
(+0.18,0.00).

OOD10:
(0.00,+0.18).

OOD11:
(-0.18,0.00).

OOD sd:

0.08.

OOD global radius cutoff:

<=0.40.

OOD frequency range:

[5,8].

PATCH RULE

At:
each:
OOD insertion,

try:
decoder-only.

If:
distillation NMSE
>0.02,

allow:
exactly:
one:
new:
fixed-dictionary:
factor.

Otherwise:

no:
factor growth.

REPRODUCIBILITY

Execute:
two complete:
6-world:
P8-development
plus:
four-OOD-insertion sweeps.

Canonical output SHA-256
must:
match exactly.

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL H191-P10 NON-EVIDENCE PILOT CLOSURE — REPEATED OOD ELASTIC PATCH REUSE

DATE:
2026-09-20.

STATUS:
COMPLETE /
STRONG POSITIVE REPEATED-OOD REUSE RESULT /
NON-EVIDENCE.

FROZEN HARNESS SHA-256

9efde966ddf02c4695462af2959555098edfdcc447e6c5c95e26c86c9540d8b4.

CANONICAL OUTPUT

RUN 1 SHA-256:

e7626fddaaf1db1a6c1e507785247ff11fed3a7064c5b4b289ee262d4e610b5c.

RUN 2 SHA-256:

e7626fddaaf1db1a6c1e507785247ff11fed3a7064c5b4b289ee262d4e610b5c.

Byte-identical:

PASS.

PRE-OOD DEVELOPED CORE

Median:
in-distribution:
P8-style patch count:

4.

Median:
shared factor count:

12.

Thus:

the repeated-OOD test
starts from:
an already:
developmentally expanded core.

OOD8

Patch trigger rate:

1 / 6
=
16.67%.

Median:
decoder-only:
distillation NMSE:

0.010505184225344372.

Median:
post-rule:
held-out NMSE:

0.006934396764246683.

P90:

0.014446474291452651.

Median:
OOD_LOCAL8
held-out NMSE:

0.003163097311714153.

Median:
gap
versus:
OOD_LOCAL8:

+0.003513640797229118.

Classification:

ROBUST.

OOD9

Patch trigger rate:

1 / 6
=
16.67%.

Median:
post-rule:
held-out NMSE:

0.0011650393153787878.

OOD_LOCAL8:

0.0010728521519970968.

Median gap:

+0.0006170936387880548.

Classification:

ROBUST.

OOD10

Patch trigger rate:

0 / 6.

Median:
decoder-only:
distillation NMSE:

0.002394959859668701.

No:
new factor
was required
in:
any:
P10 world.

Median:
held-out NMSE:

0.0031825888715247457.

OOD_LOCAL8:

0.0006210414979781172.

Median gap:

+0.0011782391165119776.

Classification:

ROBUST.

OOD11

Patch trigger rate:

1 / 6
=
16.67%.

Median:
post-rule:
held-out NMSE:

0.0027923702072896327.

P90:

0.06185935009714711.

OOD_LOCAL8:

0.0009332324205214242.

Median gap:

+0.002625437427365987.

Classification:

ROBUST.

TAIL NOTE

OOD11:
P90 held-out NMSE

exceeds:
0.05

even though:
the frozen:
stage classification
is based on:
median quality
and:
remains:
ROBUST.

Therefore:

the result
should NOT:
be interpreted
as:
uniformly:
tail-free.

The:
median reuse signal
is:
strong,

but:
some:
world-specific:
OOD tails
remain.

REPEATED-OOD PATCH SCALING

Four:
OOD capabilities

x:
6 worlds

=
24:
observed:
OOD insertions.

Only:

3:
insertions

triggered:
a:
new factor.

Observed:
aggregate trigger fraction:

12.5%.

Median:
final OOD patch count:

0.

P90:

1.5.

Median:
OOD patches
per:
OOD capability:

0.

Thus:

the:
new OOD capabilities

usually:
reuse:
the:
already developed:
shared geometry

without:
requiring:
one:
new factor
per:
novel capability.

FROZEN:
REPEATED-OOD REUSE ENCOURAGEMENT:

PASS.

FROZEN:
STRONG MECHANICAL SIGNAL:

PASS.

FINAL SHARED STRUCTURE

Median:
pre-OOD:
shared factor count:

12.

Median:
final:
shared factor count:

12.5.

Thus:

repeated:
OOD novelty

adds:
very little:
additional:
shared geometry

over:
the already:
developmental:
P8 core.

PRESERVATION

Maximum:
old prediction drift:

0.

Maximum:
old decoder change:

0.

PASS:
exact.

ACTIVE COMPUTE

Oldest ring capability:

median:
final residual ops:

16.

OOD8:

24.

OOD11:

25.

Thus:

later:
novelty

does NOT:
increase:
the active compute
of:
older capabilities.

Each:
capability
retains:
its:
birth-time:
active support.

PATCH GEOMETRY

Across:
the:
three:
triggered:
OOD patches:

scale slots:

sigma 0.22:
3.

sigma 0.44:
0.

sigma 0.88:
0.

Median:
patch center radius:

0.24407030237208294.

Median:
distance:
to:
nearest:
existing factor center:

0.19764235376052372.

Exact:
OOD_LOCAL8 support overlap:

0%.

Thus:

the few:
required:
OOD patches

are:
small-scale:
inner-region:
local complements

rather than:
pieces
of:
the:
fresh:
8-factor:
new-capability-local optimum.

TECHNICAL INTERPRETATION

P10 changes:
the:
scaling picture
from:
P8.

P8:
in-distribution:
capability additions

needed:

4:
new factors
for:
5:
new capabilities
on:
the median.

P10:
repeated:
inner-region:
high-frequency:
OOD capabilities

needed:

0:
new factors
for:
4:
OOD additions
on:
the median.

This means:

patch demand
is:
NOT:
simply:
a function
of:
how:
novel
a capability
appears
from:
its:
task label
or:
context class.

Once:
the shared core
contains:
a sufficiently:
diverse:
developmental basis,

later:
related:
OOD capabilities
can:
reuse:
that geometry.

This is:
the strongest:
shared-structure reuse
signal
in:
the:
H191 mechanical line
so far.

IMPORTANT LIMIT

P10's:
four OOD capabilities

occupy:
a:
related:
inner-region family.

Therefore:

the result
does NOT:
show:

universal:
novelty reuse.

It shows:

FAMILY-LEVEL:
NOVELTY REUSE.

The:
right next question
is:

whether:
accumulated:
developmental patches

can:
be:
compressed:
during:
sleep

without:
changing:
waking predictions.

NEXT JUSTIFIED EXPERIMENT

H191-P11 —
SLEEP-TIME:
PATCH CONSOLIDATION /
MERGE AUDIT.

Use:
a:
developmentally grown:
P8/P10-style core.

Identify:
all:
post-CORE3:
patch factors.

During:
sleep:

attempt:
to:
replace:
the accumulated:
patch-factor set

with:
a:
smaller:
fixed-dictionary:
consolidated patch basis.

Keep:

the original:
CORE3 factors
frozen.

Do NOT:
change:
the:
original:
CORE3 decoder coefficients.

For:
each capability:

fit:
only:
coefficients
on:
the:
consolidated:
patch basis

to:
reproduce:
its:
pre-sleep:
waking prediction.

Primary question:

can:
multiple:
developmental:
patches

be:
merged:
into:
fewer:
shared:
sleep factors

while:

- preserving:
  all:
  pre-sleep:
  capability predictions;
- reducing:
  stored patch geometry;
- reducing:
  later-capability:
  active compute;
- leaving:
  original:
  core semantics
  untouched?

PLAIN-SPEAK SUMMARY

What did we try?

We took:
the:
already developed:
organism

and:
gave it:
four:
new:
out-of-distribution:
capabilities
one after another.

Each newcomer
had:
the right
to:
grow:
one:
new factor

if:
the:
current core
could not:
fit it
well enough.

What happened?

Most:
of:
the:
newcomers

did not:
need:
new structure
at all.

Across:
24:
OOD insertions,

only:
3
needed:
a:
new factor.

In:
the:
median world,

none:
of:
the:
four:
OOD capabilities
needed:
a:
new factor.

Did it work?

Yes.

This passes:
the:
strong:
repeated-novelty:
reuse gate.

What did we actually learn?

Earlier:
developmental patches
can:
become:
useful:
shared structure
for:
later:
novel capabilities.

The system
is:
not:
stuck
in:
a:
one-new-factor-for-every-new-skill
growth pattern.

Why does it matter?

That is:
one of:
the:
core:
Yggdrasil goals.

The:
organism
should:
grow:
new structure
when:
it truly:
needs it,

but:
later:
learning
should:
reuse:
that structure

instead of:
growing:
forever
at:
one-for-one:
capability cost.

P10 finally:
shows:
that behavior
inside:
this:
controlled:
mechanical regime.

What should we try next?

Now:
compress:
the:
patches
that:
were accumulated
during:
development.

Let:
the system
sleep

and:
ask:

can:
several:
small:
developmental patches

be:
merged:
into:
fewer:
shared factors

without:
changing:
what:
any:
waking capability
does?

H191 accepted-lineage primary remains:
NOT STARTED / PROVENANCE BLOCKED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
