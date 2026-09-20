TITLE: DG-1A-AR-H152 — Context + Bounded Local Functional Feedback Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh151-functional-cognitive-micropatch-audit.ice

PURPOSE

H151 established:

LOCAL DEVELOPMENTAL CONTEXT
CAN:
RECONSTRUCT
LEARNED FUNCTIONAL STATE

when:
specialization
is:
strongly locally organized.

H151 also established:

PURE NEIGHBOR CONTEXT
IS NOT ENOUGH

for:
MIXED
higher-frequency
specialization.

Primary H151
CONTEXT-HARMONIC
median final recovery:

MIXED:

1%:
approximately 0.81.

2%:
approximately 0.79.

5%:
approximately 0.70.

10%:
approximately 0.63.

The next question is:

CAN
A SMALL,
LOCAL,
FUNCTIONAL ERROR SIGNAL

CORRECT:
THE RESIDUAL
THAT:
DEVELOPMENTAL CONTEXT
CANNOT INFER

WITHOUT:

- restoring saved lost coefficients;
- globally retraining the colony;
- modifying surviving learned state?

BOUNDARY

Synthetic research only.

H152 does NOT:
- claim general cognition;
- train a frontier model;
- restore production weights;
- execute STAB-18-R1;
- spend canonical scientific execution;
- authorize runtime activation.

H152 is:
a bounded functional-state reconstruction audit.

PARENT COLONY

Reuse:
H151.

2D integer lattice disk.

Primary:

R=8.

N approximately:
197.

Gaussian RBF readout.

sigma:
0.22.

Learned-state classes:

SMOOTH:
12 graph-diffusion rounds.

MIXED:
3 rounds.

SCRAMBLED:
0 rounds.

Lesion fractions:

1%,
2%,
5%,
10%.

Lesion geometries:

COMPACT,
FOUR-PATCH.

Membership regeneration:

H150 / H151 frontier rule.

p:
0.50.

CONTEXT PRIOR

Reuse:
H151 CONTEXT-HARMONIC.

Lost mutable coefficients:
are never supplied.

Surviving original coefficients:
remain fixed.

LOCAL FUNCTIONAL FEEDBACK

Feedback is:
query -> desired output
for:
the original pre-lesion function.

This is:
an environment / task-feedback surrogate.

It is NOT:
a lost-weight checkpoint.

Feedback queries are:
LOCAL.

For each world:

build:
a disjoint feedback pool
of:
64 queries.

To draw one feedback query:

1.
choose:
one lesioned cell
uniformly;

2.
take:
its normalized response center;

3.
add:
isotropic Gaussian jitter;

primary jitter standard deviation:

0.12
body-radius units;

4.
reject / redraw:
outside:
the unit disk.

Thus:
feedback is concentrated
near:
the damaged functional support.

The target output:

Y_TARGET(x)

is:
the pre-lesion colony output
at:
that local query.

Feedback queries:
are disjoint from:
the 256 held-out evaluation queries.

FEEDBACK TIMING

Functional feedback begins:

ONLY AFTER:
all lesion membership
has regenerated.

Reason:

H152 tests:
mutable specialization correction
after:
the structural micro-patch
exists again.

During:
the 12 post-membership maturation steps,

a policy receives:
its declared number
of:
new feedback observations
per step.

No feedback observation:
is reused as:
a new budget item.

Accumulated feedback
may be:
reused computationally
inside:
the bounded local solve.

FEEDBACK SOLVE

Only:
currently regenerated lesion cells
may change.

Surviving original cells:
are immutable.

At each maturation step:

let:

Phi_R =
feedback basis responses
for:
regenerated cells.

Let:

r =
target output
minus:
the contribution
from:
surviving original cells.

Solve:

argmin_w

|| Phi_R w - r ||^2

+

lambda
|| w - w_prior ||^2.

Primary:

lambda = 0.10.

For:
CONTEXT+FEEDBACK policies,

w_prior =
current H151
context-harmonic
reconstruction.

For:
FEEDBACK-ONLY,

w_prior =
zero.

No original lost coefficient:
is read.

No held-out evaluation output:
is read.

FUNCTIONAL POLICIES

A — CONTEXT-0

Frozen:
H151 context-harmonic parent.

No:
functional feedback.

B — CONTEXT-FB1

Context prior
+
1 new local feedback observation
per maturation step.

Maximum:

12 observations.

C — CONTEXT-FB2

PRIMARY CANDIDATE.

Context prior
+
2 new local feedback observations
per maturation step.

Maximum:

24 observations.

D — CONTEXT-FB4

Context prior
+
4 new local feedback observations
per maturation step.

Maximum:

48 observations.

E — FEEDBACK-ONLY-FB2

No:
neighbor-context initialization
or:
context refinement.

Restored coefficient:
0.

After membership completion:

same:
2-observation / step
local feedback budget

and:
same ridge solve,

with:
zero prior.

This isolates:
the value
of:
developmental context.

F — CHECKPOINT-ORACLE

Same:
membership schedule.

Exact original coefficient
is restored
when:
membership returns.

Upper-bound comparator only.

FUNCTIONAL EVALUATION

Reuse:
H151.

256 held-out evaluation queries.

Y_BASE:
pre-lesion output.

MSE_LESION:
lesioned-output error.

FunctionalRecovery:

1 -
MSE(current,Y_BASE)
/
MSE_LESION.

Report:
raw
and:
clipped [0,1].

T50,
T90,
T99.

Functional downtime:

sum:
1 - clipped recovery
over:
repair / maturation steps.

PRIMARY FACTORIAL

Context:

3.

Damage fraction:

4.

Geometry:

2.

Underlying worlds / cell:

100.

Total underlying worlds:

3 x 4 x 2 x 100
=
2,400.

Policies:

6.

Total policy-world evaluations:

14,400.

COMMON-WORLD DISCIPLINE

Within one underlying world:

all policies receive:

- identical colony;
- identical learned coefficient field;
- identical lesion;
- identical membership repair schedule;
- identical held-out evaluation queries;
- identical local feedback pool;
- identical feedback targets.

Only:
feedback budget
and:
repair prior
differ.

PRIMARY METRICS

1.
final functional recovery;

2.
functional T50;

3.
functional T90;

4.
functional T99;

5.
fraction reaching:
T90;

6.
functional downtime;

7.
feedback observations consumed;

8.
final held-out MSE ratio;

9.
lesion-weight RMSE
for:
analysis only;

10.
context value:

CONTEXT-FB2
minus:
FEEDBACK-ONLY-FB2;

11.
feedback marginal value:

FB1,
FB2,
FB4
relative to:
CONTEXT-0;

12.
compact-versus-four-patch interaction;

13.
SMOOTH / MIXED / SCRAMBLED interaction;

14.
oracle gap.

PRIMARY ACCEPTANCE SHAPE

H152 supports:
BOUNDED FUNCTIONAL CORRECTION
FOR
COGNITIVE MICRO-PATCHING

if:

1.
MIXED,
1%..5%:

CONTEXT-FB2
median final functional recovery
>=0.90.

2.
MIXED,
1%..5%:

>=90%
of worlds
reach:
functional T90
inside:
the 12-step feedback maturation window
plus:
membership repair time.

3.
SMOOTH,
1%..5%:

CONTEXT-FB2
median final recovery
>=0.95

and:
does not fall
more than:
0.02
below:
CONTEXT-0.

4.
For:
SMOOTH and MIXED,
1%..5%:

CONTEXT-FB2
median final recovery
is:
>=0.05
above:
FEEDBACK-ONLY-FB2

in at least:
four of:
the six
context x damage groups.

This tests:
developmental-prior value.

5.
MIXED,
1%..5%:

CONTEXT-FB2
is:
within 0.03
median final recovery
of:
CONTEXT-FB4

in at least:
two of:
three damage fractions.

This tests:
whether:
24 observations
capture most:
of:
the bounded-feedback value.

6.
SCRAMBLED:

the context advantage:

CONTEXT-FB2
minus:
FEEDBACK-ONLY-FB2

is:
<0.05
median

for:
at least:
three of:
four damage fractions.

This is:
the mechanism-specificity gate.

7.
FOUR-PATCH
does not:
incur:
>20%
median T90 penalty
relative to:
COMPACT

for:
MIXED
1%..5%.

8.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H152 as:
mixed / negative
if:

- FB2 cannot raise:
  MIXED small-lesion recovery
  above:
  0.90;

- only:
  FB4
  closes the gap;

- feedback-only performs:
  as well as:
  context+feedback
  on:
  locally organized state;

- local feedback destabilizes:
  SMOOTH repair;

- SCRAMBLED gains:
  the same context advantage,
  implying:
  context is not mechanistically relevant;

- four-patch repair
  creates:
  feedback interference;

- bounded local feedback
  needs:
  more observations
  than:
  the number of missing mutable coefficients
  by:
  an order of magnitude;

- surviving original coefficients
  must be changed
  to:
  recover the patch.

ROBUSTNESS AFTER PRIMARY

Feedback ridge lambda:

0.03,
0.10,
0.30.

Local feedback jitter:

0.06,
0.12,
0.20.

Membership repair p:

0.25,
0.50,
1.00.

Body radius:

6,
8,
11.

No robustness value:
may be selected
from:
held-out primary outcomes.

PRIMARY SEEDS

20260919900000
through:
20260919902399.

SANITY SEEDS

20260919990000
family.

Sanity outputs:
NON-EVIDENCE.

No execution-semantic change
after:
the first held-out H152 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_CONTEXT_BOUNDED_FUNCTIONAL_FEEDBACK_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H152 HELD-OUT PRIMARY EXECUTION.

No H152 primary world
has been executed.

PARENT HARNESS SHA-256

H151:
3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

H152 WRAPPER SHA-256

e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

All H151 colony,
learned-state,
lesion,
membership,
and:
evaluation mechanics
are inherited unchanged.

LOCAL FEEDBACK QUERY REALIZATION

Feedback pool:

64 queries / world.

RNG:

SHA-256-derived
from:
world seed
and:
"feedback_queries".

For each query:

- choose:
  one lesion member
  uniformly;

- use:
  its normalized response center;

- add:
  isotropic Gaussian jitter
  sd=0.12;

- reject:
  points outside:
  the unit disk.

Feedback query points:
are disjoint
from:
the 256 held-out
evaluation query points.

Feedback target:

pre-lesion colony output
at:
that feedback query.

No lost coefficient:
is exposed.

FEEDBACK BEGINS

only after:
complete membership regeneration.

Twelve:
post-membership maturation steps.

Budgets:

CFB1:
1 new feedback pair / step.

CFB2:
2.

CFB4:
4.

FBONLY2:
2.

Maximum observations:

12,
24,
48,
24.

CONTEXT POLICIES

CONTEXT0,
CFB1,
CFB2,
CFB4

use:
the exact H151
context initialization
and:
0.50 harmonic refinement.

FUNCTIONAL RIDGE CORRECTION

At each feedback maturation step:

solve only for:
the lesion-cell coefficients.

Surviving original coefficients:
are fixed.

Use:
all accumulated feedback
available to:
that policy.

Objective:

||Phi_R w - r||^2
+
0.10 ||w - prior||^2.

CONTEXT feedback prior:

current harmonic
lesion-cell coefficients.

FBONLY2 prior:

zero vector.

The solve is:
ordinary dense linear solve.

Least-squares fallback:
only if:
the ridge system
cannot be directly solved.

ORACLE

restores:
exact lost coefficient
on:
membership return.

Evaluation only.

SANITY

Disjoint:
20260919990000...
family.

Five representative underlying worlds.

NON-EVIDENCE signals:

MIXED 1% compact:

CONTEXT0:
approximately 0.855.

CFB2:
approximately 0.974.

FBONLY2:
approximately 0.662.

MIXED 5% compact:

CONTEXT0:
approximately 0.491.

CFB2:
approximately 0.979.

FBONLY2:
approximately 0.915.

MIXED 5% four-patch:

CONTEXT0:
approximately 0.937.

CFB2:
approximately 0.969.

FBONLY2:
approximately 0.342.

SMOOTH 5% compact:

CFB2:
approximately 0.995.

SCRAMBLED 5% compact:

CFB2:
approximately 0.307.

FBONLY2:
approximately 0.295.

No:
policy,
budget,
lambda,
jitter,
threshold,
seed,
or:
sample size

was changed
from:
these sanity results.

PRIMARY FAMILY REMAINS

20260919900000..20260919902399.

No execution-semantic change
after:
the first held-out H152 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — CONTEXT + BOUNDED LOCAL FUNCTIONAL FEEDBACK

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE.

FROZEN H152 WRAPPER SHA-256

e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

ACCEPTED PRIMARY FAMILY

20260919900000..20260919902399.

PRIMARY MATRIX

2,400 underlying worlds.

6 policies.

14,400 policy-world evaluations.

Validation:

- exactly 2,400 unique accepted world seeds;
- exact held-out seed interval;
- exactly six policy results per seed;
- zero duplicate seed x policy rows;
- zero functionally-trivial worlds;
- no primary parameter tuning.

PRIMARY CANDIDATE

C —
CONTEXT-FB2.

Maximum local functional feedback:

24 observations
over:
12 post-membership maturation steps.

MIXED CONTEXT — PRIMARY TARGET

Pooled across:
COMPACT
and:
FOUR-PATCH.

CONTEXT-FB2 median final recovery:

1%:
0.9303.

2%:
0.9010.

5%:
0.9354.

10%:
0.9373.

Thus:

the primary H151 MIXED-context gap
is materially closed
at:
the median.

For:
1%..5%,

all three median recoveries
meet:
the frozen >=0.90 target.

However:

fraction of worlds reaching
functional T90:

1%:
65.5%.

2%:
50.5%.

5%:
66.0%.

These are:
far below:
the frozen 90% reliability gate.

Therefore:

BOUNDED FUNCTIONAL FEEDBACK
WORKS AS A REAL CORRECTION SIGNAL

but:

THE CURRENT LOCAL SOLVE
IS NOT YET
RELIABLE ENOUGH
WORLD-BY-WORLD.

SMOOTH CONTEXT

CONTEXT-FB2 median final recovery:

1%:
0.9956.

2%:
0.9955.

5%:
0.9967.

10%:
0.9947.

Compared with:
CONTEXT-0,

feedback does not degrade:
SMOOTH repair.

It improves:
or preserves
the already-strong developmental prior.

DEVELOPMENTAL PRIOR VALUE

CONTEXT-FB2
minus:
FEEDBACK-ONLY-FB2
median final recovery:

SMOOTH:

1%:
+0.584.

2%:
+0.737.

5%:
+0.546.

MIXED:

1%:
+0.511.

2%:
+0.638.

5%:
+0.485.

Thus:

local developmental context
provides:
large additional value
beyond:
the same feedback budget
with:
zero prior.

This gate:
strongly passes.

FB2 VERSUS FB4

MIXED final-recovery gap:

1%:
FB4 - FB2
approximately 0.0342.

2%:
approximately 0.0317.

5%:
approximately 0.0252.

Frozen requirement:

FB2 within:
0.03
of:
FB4

in:
at least two
of:
three
small-lesion groups.

Observed:

only:
5%
passes.

Therefore:

24 observations
do NOT yet capture:
most of the available
48-observation correction value
under:
the frozen criterion.

FOUR-PATCH INTERACTION

MIXED CONTEXT-FB2
median functional T90
among worlds reaching T90:

1%:

COMPACT:
3.5.

FOUR:
6.

2%:

COMPACT:
5.

FOUR:
8.

5%:

COMPACT:
9.

FOUR:
9.

Reach-T90 fractions:

1%:
COMPACT 74%.
FOUR 57%.

2%:
COMPACT 75%.
FOUR 26%.

5%:
COMPACT 78%.
FOUR 54%.

Therefore:

the H150 geometric parallel-frontier advantage
does NOT automatically transfer
to:
functional-feedback reconstruction.

At:
1%
and:
2%,

FOUR-PATCH
incurs:
>20%
functional-T90 penalty.

This gate:
FAILS.

Interpretation:

parallel membership regeneration
creates:
more repair boundaries,

but:
the fixed local feedback pool
must identify:
multiple independent functional residuals.

The information problem
can therefore:
be harder
even while:
the geometric repair problem
is easier.

SCRAMBLED MECHANISM-SPECIFICITY

CONTEXT-FB2
median final recovery:

1%:
0.5640.

2%:
0.3455.

5%:
0.5346.

10%:
0.6794.

FEEDBACK-ONLY-FB2:

1%:
0.3901.

2%:
0.2330.

5%:
0.3951.

10%:
0.4782.

Context advantage:

1%:
+0.174.

2%:
+0.112.

5%:
+0.139.

10%:
+0.201.

Frozen mechanism-specificity requirement:

context advantage <0.05
for:
at least three of four
SCRAMBLED damage fractions.

Observed:

0 / 4.

FAIL.

Therefore:

the H152 context prior
is NOT acting only as:
a developmental-structure recovery mechanism.

Under feedback,
harmonic context also acts as:
a useful generic regularizer
for:
some spatially scrambled coefficient fields.

This does not erase:
the strong SMOOTH / MIXED result,

but:
it prevents:
a clean mechanism-specific interpretation.

FEEDBACK EFFICIENCY WARNING

At:
R=8,
N=197,

declared damage counts are approximately:

1%:
2 cells.

2%:
4.

5%:
10.

10%:
20.

CONTEXT-FB2 can consume:
24 local functional observations.

Thus:

at the smallest 1% lesion,

feedback observations
are approximately:
12x
the number of missing mutable coefficients.

This violates:
the spirit of:
very-low-overhead micro-patching

even though:
the signal is local
and:
far below global retraining.

Future work should measure:
information per repaired coefficient

and:
stop feedback adaptively
when:
functional uncertainty closes.

CHECKPOINT ORACLE

Final functional recovery:
1.0.

It remains:
the upper-bound ceiling.

No deployable policy
systematically exceeds:
the oracle.

PREREGISTERED GATE REVIEW

PASS:

1.
MIXED 1%..5%
median final recovery
>=0.90.

2.
SMOOTH 1%..5%
median final recovery
>=0.95

with:
no >0.02 degradation
versus:
CONTEXT-0.

3.
CONTEXT-FB2
beats:
FEEDBACK-ONLY-FB2
by:
>=0.05

in:
all six
SMOOTH / MIXED
1%..5%
groups.

4.
CHECKPOINT-ORACLE
remains:
the ceiling.

FAIL:

1.
MIXED 1%..5%
>=90%
world-level T90 reliability.

Observed:
50.5%..66.0%.

2.
FB2 captures most FB4 value
in:
at least two of three
MIXED small-lesion groups.

Observed:
one of three.

3.
SCRAMBLED
mechanism-specificity gate.

Observed context advantage:
>0.05
in:
all four damage fractions.

4.
FOUR-PATCH
functional-T90 non-interference
at:
MIXED 1%..5%.

1%
and:
2%
exceed:
the allowed 20% penalty.

FINAL INTERPRETATION

H152 is:

MIXED-POSITIVE.

The experiment establishes:

A SMALL LOCAL FUNCTIONAL ERROR SIGNAL
CAN
CLOSE MOST OF
THE H151 MIXED-CONTEXT
MEDIAN RECOVERY GAP.

This is:
important.

A damaged computational micro-colony
does not require:
exact lost-state restoration

to recover:
>90%
median function

for:
1%..5%
MIXED lesions.

The combination:

LOCAL DEVELOPMENTAL PRIOR
+
BOUNDED TASK FEEDBACK

is materially stronger than:
either:
context alone
or:
feedback-only.

However:

the current solve is not:
reliable,
information-efficient,
or:
multi-patch-aware enough

for:
a clean cognitive micro-patch architecture.

THE NEXT PROBLEM IS NOT
MORE FEEDBACK.

It is:

BETTER FEEDBACK ALLOCATION.

The controller should determine:

- which regenerated coefficients
  remain functionally uncertain;
- which local queries
  maximally reduce that uncertainty;
- when:
  one micro-patch is already good enough;
- and:
  how to distribute:
  a fixed feedback budget
  across:
  multiple simultaneous wounds.

NEXT SCOPED DIRECTION

ACTIVE LOCAL
FUNCTIONAL PROBING
+
UNCERTAINTY-BOUNDED
EARLY STOPPING.

The goal is:

reach:
H152-level median recovery

with:
substantially fewer observations,

while:
raising:
world-level T90 reliability

and:
removing:
FOUR-PATCH feedback interference.

H152 DOES NOT AUTHORIZE

- production weight repair;
- live cognitive replacement;
- global model retraining;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — CONTEXT + BOUNDED LOCAL FUNCTIONAL FEEDBACK

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-POSITIVE.

FROZEN HARNESS

H151 parent:
3f6042716b4e5a26f41569376a4dca833f5bae5f3c053aa2280615bfadb32e37.

H152 wrapper:
e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

ACCEPTED PRIMARY FAMILY

20260919900000..20260919902399.

PRIMARY MATRIX

2,400 underlying worlds.

6 policies.

14,400 unique policy-world evaluations.

Validation:

- exact held-out seed interval;
- six policies per seed;
- no seed gaps;
- no policy gaps;
- overlapping sandbox checkpoint shards
  were verified:
  byte-identical
  for:
  duplicated seed-policy pairs;
- acceptance uses:
  one unique record
  per:
  seed x policy;
- zero functionally-trivial worlds;
- no post-primary tuning.

PRIMARY CANDIDATE

CONTEXT-FB2.

Maximum local functional feedback:

24 observations.

Only:
regenerated lesion coefficients
were mutable.

Surviving original coefficients:
remained fixed.

MIXED CONTEXT — PRIMARY TARGET

Median final functional recovery:

1%:
0.9303.

2%:
0.9010.

5%:
0.9354.

10%:
0.9373.

Thus:

the H151 MIXED-context gap
is:
substantially closed
at:
the median.

H151 parent
CONTEXT-0
in the same H152 worlds:

1%:
0.7977.

2%:
0.8015.

5%:
0.7080.

10%:
0.5769.

Therefore:

24 local functional observations
plus:
the developmental prior

recover:
a large residual
that:
neighbor context alone
cannot infer.

MIXED T90 WORLD FRACTION

CONTEXT-FB2:

1%:
65.5%.

2%:
50.5%.

5%:
66.0%.

10%:
68.0%.

Required
for:
1%..5%:

>=90%.

FAIL.

Interpretation:

median final quality
is:
high,

but:
reliability / latency
is:
not yet high enough
across:
worlds.

SMOOTH CONTEXT

CONTEXT-FB2
median final recovery:

1%:
0.9956.

2%:
0.9955.

5%:
0.9967.

10%:
0.9947.

Thus:

bounded functional feedback
does NOT:
destabilize
the already-good
developmental-context repair.

It improves:
or:
preserves
SMOOTH recovery.

DEVELOPMENTAL PRIOR VALUE

Median final recovery difference:

CONTEXT-FB2
minus:
FEEDBACK-ONLY-FB2.

SMOOTH:

1%:
+0.584.

2%:
+0.737.

5%:
+0.546.

MIXED:

1%:
+0.511.

2%:
+0.638.

5%:
+0.485.

Thus:

the 24-observation feedback budget
does NOT:
replace:
developmental context.

The local prior
provides:
large information value.

FEEDBACK BUDGET SCALING

MIXED median final recovery:

1%:

FB1:
0.8965.

FB2:
0.9303.

FB4:
0.9645.

2%:

FB1:
0.8770.

FB2:
0.9010.

FB4:
0.9327.

5%:

FB1:
0.9012.

FB2:
0.9354.

FB4:
0.9606.

CFB4 minus CFB2:

1%:
approximately 0.0342.

2%:
approximately 0.0317.

5%:
approximately 0.0252.

Frozen gate:

within:
0.03
for:
two of:
three.

Observed:
only:
5%
passes exactly.

This is:
a narrow fail.

Interpretation:

24 observations
capture:
most
but:
not all
of:
the 48-observation benefit.

MULTI-PATCH FEEDBACK ROUTING LIMIT

MIXED,
CONTEXT-FB2:

1%:

COMPACT:
final 0.9568,
median T90 3.5.

FOUR-PATCH:
final 0.9076,
median T90 6.

2%:

COMPACT:
final 0.9715,
T90 5.

FOUR-PATCH:
final 0.8639,
T90 8.

5%:

COMPACT:
final 0.9677,
T90 9.

FOUR-PATCH:
final 0.9089,
T90 9.

Thus:

H151 established:
distributed holes
can:
increase useful developmental boundary.

H152 shows:
a fixed undirected
functional-feedback pool

can:
waste that advantage.

With:
four damaged components,

the 24 observations
are not:
explicitly allocated
by:
component need.

The frozen
FOUR-PATCH
T90 non-inferiority gate
fails
at:
1%
and:
2%.

This is:
the clearest H152 controller defect.

SCRAMBLED CONTEXT

CONTEXT-FB2
median final recovery:

1%:
0.5640.

2%:
0.3455.

5%:
0.5346.

10%:
0.6794.

FEEDBACK-ONLY-FB2:

1%:
0.3901.

2%:
0.2330.

5%:
0.3951.

10%:
0.4782.

Context advantage:

approximately:

+0.174,
+0.112,
+0.139,
+0.201.

The preregistered
SCRAMBLED
<0.05
context-advantage gate
therefore:
FAILS.

Interpretation:

harmonic context
acts as:
a useful regularizer
even when:
the lost coefficient field
is:
spatially scrambled.

This means:

the H152
mechanism-specificity test
was:
too strict
for:
the combined
regularized inverse problem.

However:

SCRAMBLED final recovery
remains:
far below:
SMOOTH

and:
generally below:
MIXED.

Thus:

local representational organization
still matters materially.

OBSERVATION EFFICIENCY LIMIT

At:
R=8,
N=197,

nominal damaged cells:

1%:
2.

2%:
4.

5%:
10.

10%:
20.

CFB2 always consumes:
24 feedback observations.

Therefore:

at:
1%,

feedback count
is:
12x
the missing coefficient count.

At:
10%:

approximately:
1.2x.

A fixed:
24-observation budget

is:
inefficient
for:
very small patches

and:
potentially under-routed
for:
distributed patches.

This directly motivates:
adaptive budget allocation.

PREREGISTERED GATE REVIEW

SUPPORTED

1.
MIXED 1%..5%:

CFB2
median final recovery
>=0.90.

Observed:

0.9303,
0.9010,
0.9354.

PASS.

2.
SMOOTH 1%..5%:

CFB2
>=0.95

without:
>0.02 regression
from:
CONTEXT-0.

PASS.

3.
Developmental prior value:

CFB2
beats:
FBONLY2
by:
>=0.05

in:
all six
SMOOTH / MIXED
1%..5%
groups.

PASS.

4.
CHECKPOINT-ORACLE
remains:
the ceiling.

PASS.

FAILED / MIXED

1.
MIXED
T90-world fraction
>=90%.

Observed:
50.5%..66%.

FAIL.

2.
CFB2
within:
0.03
of:
CFB4
for:
two of:
three
MIXED small-damage groups.

Observed:
one of three.

NARROW FAIL.

3.
SCRAMBLED
context advantage
<0.05
for:
three of four
fractions.

FAIL.

4.
FOUR-PATCH
T90 penalty
<=20%
versus:
COMPACT
for:
MIXED 1%..5%.

FAIL
at:
1%
and:
2%.

FINAL INTERPRETATION

H152 is:

MIXED-POSITIVE.

The central hypothesis is:
SUPPORTED.

A small,
bounded,
local functional-error signal

can:
close most
of:
the higher-frequency
learned-state gap

left by:
developmental context.

But:

A FIXED FEEDBACK BUDGET
IS NOT:
A GOOD
MICRO-PATCH CONTROLLER.

The remaining problem is:

ROUTING
AND:
STOPPING.

The controller needs to decide:

- which damaged component
  receives:
  the next functional query;

- when:
  one component
  is:
  already sufficiently reconstructed;

- when:
  another component
  remains:
  underdetermined;

- how:
  feedback budget
  should scale
  with:
  missing mutable-state dimension.

NEXT SCOPED EXPERIMENT

H153 —
COMPONENT-AWARE
ADAPTIVE FUNCTIONAL FEEDBACK
MICRO-PATCH.

Primary hypothesis:

allocate:
local functional feedback
to:
the damaged component
with:
the highest current
held-local residual / uncertainty,

and:

stop:
querying
a component

once:
its bounded validation error
passes:
a frozen threshold.

Target:

preserve:
H152 MIXED
median recovery >=0.90

while:

- raising:
  T90-world fraction
  toward:
  >=90%;

- reducing:
  tiny-patch feedback waste;

- removing:
  FOUR-PATCH routing penalty;

- using:
  fewer observations
  than:
  fixed FB4.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — CONTEXT + BOUNDED LOCAL FUNCTIONAL FEEDBACK MICRO-PATCH

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE WITH POSITIVE DEVELOPMENTAL-PRIOR SIGNAL.

FROZEN H152 WRAPPER SHA-256

e8be77384de4fef8a6b8eda875575f581edfc97794d5060e57e4e3bfa7b3b4e3.

ACCEPTED PRIMARY FAMILY

20260919900000..20260919902399.

PRIMARY MATRIX

2,400 underlying worlds.

6 policies.

14,400 policy-world evaluations.

Validation:

- exactly 2,400 unique held-out world seeds;
- exact accepted seed interval;
- exactly six policy results per seed;
- zero functionally-trivial accepted worlds;
- no accepted seed gaps;
- no accepted seed duplicates;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

C —
CONTEXT-FB2.

MIXED CONTEXT — PRIMARY TARGET

Pooled across:
COMPACT
and:
FOUR-PATCH.

Median final functional recovery:

1%:
0.9303.

2%:
0.9010.

5%:
0.9354.

10%:
0.9373.

Thus:

24 local functional observations
combined with:
the developmental context prior

raise:
MIXED
1%..5%
median final recovery

above:
the preregistered 0.90 target.

This is:
a real positive result.

However:

fraction of MIXED worlds
reaching functional T90
inside:
the full membership + 12-step feedback window:

1%:
65.5%.

2%:
50.5%.

5%:
66.0%.

Required:
>=90%.

Therefore:

median quality improves,
but:
reliable fast recovery
does NOT pass.

SMOOTH CONTEXT

CONTEXT-FB2
median final recovery:

1%:
0.9956.

2%:
0.9955.

5%:
0.9967.

All exceed:
0.95.

Compared with:
CONTEXT-0:

1%:
0.9861.

2%:
0.9833.

5%:
0.9721.

Local feedback therefore:
does not destabilize
smooth developmental repair.

DEVELOPMENTAL-PRIOR VALUE

CONTEXT-FB2
minus:
FEEDBACK-ONLY-FB2
median final recovery:

SMOOTH:

1%:
+0.5839.

2%:
+0.7366.

5%:
+0.5460.

MIXED:

1%:
+0.5112.

2%:
+0.6380.

5%:
+0.4846.

All:
6 / 6

small-lesion
SMOOTH / MIXED groups

exceed:
the preregistered +0.05
developmental-prior gate.

Thus:

LOCAL DEVELOPMENTAL CONTEXT
AND
LOCAL FUNCTIONAL FEEDBACK

are:
complementary.

Feedback alone:
does not explain
the recovered function.

FB2 VERSUS FB4

MIXED median final recovery:

1%:

FB2:
0.9303.

FB4:
0.9645.

gap:
0.0342.

2%:

FB2:
0.9010.

FB4:
0.9327.

gap:
0.0317.

5%:

FB2:
0.9354.

FB4:
0.9606.

gap:
0.0252.

Only:
1 of 3
small MIXED damage fractions

places FB2
within:
0.03
of FB4.

Required:
at least 2 of 3.

FAIL.

Thus:

24 observations
do not yet capture:
most of the available bounded-feedback value.

SCRAMBLED CONTEXT — MECHANISM-SPECIFICITY LIMIT

CONTEXT-FB2
minus:
FEEDBACK-ONLY-FB2
median final recovery:

1%:
+0.1739.

2%:
+0.1125.

5%:
+0.1394.

10%:
+0.2012.

Required:

<0.05
for:
at least 3 of 4 damage fractions.

Observed:

0 of 4.

FAIL.

Important interpretation:

the H152 ridge solve
can extract useful correction
from:
the context prior

even when:
that prior is not strongly spatially smooth.

That means:
the present context-versus-feedback decomposition
is not sufficiently mechanism-specific.

It does NOT mean:
SCRAMBLED reaches strong absolute recovery.

CONTEXT-FB2 SCRAMBLED median final recovery remains:

1%:
0.5640.

2%:
0.3455.

5%:
0.5346.

10%:
0.6794.

MULTI-PATCH FEEDBACK INTERFERENCE

MIXED CONTEXT,
CONTEXT-FB2.

1% damage:

COMPACT:
median final recovery 0.9568.
T90 world rate 74%.
median T90 among reached worlds 3.5.

FOUR-PATCH:
median final recovery 0.9076.
T90 world rate 57%.
median T90 among reached worlds 6.

2% damage:

COMPACT:
median final recovery 0.9715.
T90 world rate 75%.
median T90 5.

FOUR-PATCH:
median final recovery 0.8639.
T90 world rate 26%.
median T90 8.

5% damage:

COMPACT:
median final recovery 0.9677.
T90 world rate 78%.
median T90 9.

FOUR-PATCH:
median final recovery 0.9089.
T90 world rate 54%.
median T90 9.

The frozen geometry gate
allows:
at most
20%
FOUR-PATCH T90 penalty.

Observed:

1%:
approximately 71%
penalty.

2%:
approximately 60%
penalty.

5%:
no median penalty.

Therefore:

the gate fails
at:
1%
and:
2%.

This is:
a key architectural result.

H150 showed:
multiple small wounds
can regenerate membership quickly
through:
parallel frontiers.

H152 now shows:

A FIXED,
UNDIRECTED
FUNCTIONAL-FEEDBACK BUDGET

CAN BE:
DILUTED
ACROSS:
MULTIPLE SMALL WOUNDS.

Geometry-level parallelism
does not automatically imply:
functional-correction parallelism.

FEEDBACK OBSERVATION DENSITY

Primary CFB2 always consumes:
24 observations.

Typical lost mutable coefficients:

1%:
2 coefficients.

2%:
4.

5%:
10.

Thus:

for:
1% damage,

the fixed FB2 budget
uses:
approximately 12 feedback observations
per missing coefficient.

Yet:
T90 reliability
still fails.

This indicates:

the main limitation
is not simply:
insufficient scalar observation count.

It is:
where,
when,
and:
to which wound component
feedback is allocated.

CHECKPOINT ORACLE

Remains:
the functional ceiling

at:
final recovery 1.0.

No context / feedback policy
systematically exceeds:
the oracle.

PREREGISTERED GATE REVIEW

SUPPORTED

1.
MIXED 1%..5%
CONTEXT-FB2
median final recovery >=0.90.

PASS.

2.
SMOOTH 1%..5%
CONTEXT-FB2
median final recovery >=0.95

and:
does not fall
>0.02
below:
CONTEXT-0.

PASS.

3.
Developmental-prior value:

CONTEXT-FB2
beats:
FEEDBACK-ONLY-FB2
by:
>=0.05

in:
6 / 6
required SMOOTH / MIXED
small-lesion groups.

PASS.

4.
CHECKPOINT-ORACLE
remains:
the ceiling.

PASS.

FAILED

1.
MIXED 1%..5%
T90-world fraction
>=90%.

Observed:
50.5%..66%.

FAIL.

2.
FB2 within:
0.03
of FB4

in:
at least 2 / 3
MIXED small-lesion groups.

Observed:
1 / 3.

FAIL.

3.
SCRAMBLED
context-specificity gate.

Observed:
0 / 4
damage levels
with:
CONTEXT-FB2 minus FBONLY2 <0.05.

FAIL.

4.
FOUR-PATCH
functional T90 penalty
<=20%

for:
MIXED 1%..5%.

Fails:
1%
and:
2%.

FAIL.

FINAL INTERPRETATION

H152 is:

MIXED-NEGATIVE.

The central hypothesis is:
partly supported.

A SMALL LOCAL FUNCTIONAL SIGNAL
CAN:
CLOSE MOST OF
THE MIXED-CONTEXT
FINAL-QUALITY GAP.

But:

A FIXED FEEDBACK BUDGET
IS NOT YET:
A RELIABLE
FUNCTIONAL MICRO-PATCH CONTROLLER.

The remaining problem is:

FEEDBACK ALLOCATION.

H152 provides strong evidence that:

- developmental context supplies a valuable prior;
- local task feedback can correct residual specialization;
- more feedback still has material marginal value;
- fixed undirected feedback is inefficient for very small lesions;
- separate wounds compete for the same functional-feedback budget.

ARCHITECTURAL CONSEQUENCE

Do NOT:
respond by:
globally increasing feedback
or:
globally retraining surviving state.

The next experiment should make:
feedback itself
developmentally local and wound-aware.

Each disconnected micro-patch
should receive:
its own:
error estimate,
budget,
and:
stopping rule.

Functional feedback should be:
allocated adaptively
to:
the wound component
with:
the highest residual contribution
to:
held-out local error.

This directly tests whether:

INTELLIGENCE MICRO-PATCHING
CAN SCALE
AS:
MANY SMALL
INDEPENDENT
FUNCTIONAL REPAIR JOBS

rather than:
one shared repair solve.

NEXT SCOPED EXPERIMENT

H153 —
COMPONENT-AWARE
ADAPTIVE FUNCTIONAL-FEEDBACK
MICRO-PATCH.

Primary questions:

1.
Can:
a fixed TOTAL feedback budget

allocated:
per wound component
by:
residual need

restore:
MIXED 1%..5%
T90 reliability
to:
>=90%?

2.
Can:
FOUR-PATCH
recover:
at least as fast as:
COMPACT

when:
feedback is:
component-aware?

3.
Can:
an early-stop rule
reduce:
observations spent
on:
already-recovered components?

4.
Can:
mechanism specificity
be restored
by:
requiring:
local context consistency
before:
context acts as a ridge prior?

H152 DOES NOT AUTHORIZE

- production repair budgets;
- semantic human-cognition claims;
- learned-model live patching;
- STAB-18-R1 execution;
- runtime activation.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
