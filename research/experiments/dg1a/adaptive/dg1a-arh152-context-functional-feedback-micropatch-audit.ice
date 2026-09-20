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
