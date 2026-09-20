TITLE: DG-1A-AR-H156 — Joint Measurement Conditioning / Prior-Strength Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh155-residual-routed-global-joint-repair-audit.ice

PURPOSE

H155 closed:
residual routing
as:
the primary explanation
for:
the remaining micro-patch reliability limit.

The best 24-observation policies
were:
simple global-joint
fixed / uncertainty designs.

H156 asks:

IS THE REMAINING FAILURE
AN
INVERSE-PROBLEM
CONDITIONING LIMIT?

Two candidate causes
are separated:

1.
MEASUREMENT DESIGN.

Do the 24 local queries
span:
the lost coefficient subspace
well enough?

2.
PRIOR STRENGTH.

Does:
ridge lambda = 0.10

overweight:
the developmental prior
relative to:
the information carried
by:
24 local functional observations?

This is:
a diagnostic dependency
before:
adding more repair-controller complexity.

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse:
H152/H153 colony and functional model.

R=8.
N=197.
sigma=0.22.
repair p=0.50.
12 post-membership maturation steps.

Contexts:

SMOOTH,
MIXED,
SCRAMBLED.

Damage:

1%,
2%,
5%,
10%.

Geometry:

COMPACT,
FOUR-PATCH.

LOCAL FEEDBACK POOL

Per world:

64 local candidate queries.

Use:
the H152 candidate-pool realization.

Each query:

- chooses:
  one lesion member;
- centers on:
  that member's normalized response center;
- adds:
  Gaussian jitter sd=0.12;
- rejects:
  outside the unit disk.

All policies in a world
share:
the same candidate query points
and:
the same target outputs.

Unselected query targets
are:
hidden from:
query-selection policies.

GLOBAL JOINT SOLVE

All regenerated lesion coefficients
are solved:
jointly.

Surviving original coefficients:
remain fixed.

Objective:

||Phi_R w_R - r||^2
+
lambda ||w_R - w_prior||^2.

w_prior:

the current H151
context-harmonic reconstruction.

No:
lost original coefficient
is read.

No:
held-out evaluation target
is read.

QUERY DESIGN 1 — FIXED

Consume:
the shared candidate pool
in:
deterministic generated order.

This is:
the H152-style
measurement-design comparator.

QUERY DESIGN 2 — GLOBAL D-OPT / LEVERAGE

Let:

A =
Phi_S,R^T Phi_S,R
+
lambda I.

For unqueried candidate row p_j:

u_j =
p_j^T A^-1 p_j.

Choose:
maximum u_j.

By:
the matrix determinant lemma,

this also maximizes:
the one-step
log-determinant gain:

log det(A + p_j p_j^T)
-
log det(A).

Thus:

GLOBAL LEVERAGE
IS:
GREEDY D-OPTIMAL
UNDER THIS LINEAR-RIDGE MODEL.

No separate D-opt policy
is needed.

QUERY DESIGN 3 — GLOBAL A-OPT

Let:

Sigma =
A^-1.

Expected trace-covariance reduction
from candidate p_j:

a_j =
(p_j^T Sigma^2 p_j)
/
(1 + p_j^T Sigma p_j).

Choose:
maximum a_j.

This directly targets:
total posterior coefficient variance.

PRIOR STRENGTH

Primary candidate ridge strengths:

lambda =
0.03
and:
0.10.

lambda=0.03
was:
already preregistered
as:
an H152 post-primary robustness value.

It is not:
invented from:
H155 primary outcomes.

lambda=0.30
is retained:
only as:
a strong-prior diagnostic
on the sanity subset,
not:
as a primary policy.

FUNCTIONAL POLICIES

A — FIXED-L10

Frozen:
H152-style
generated-order feedback.

lambda=0.10.

24 observations maximum.

B — FIXED-L03

Same:
fixed query order.

lambda=0.03.

24 observations.

Isolates:
prior-strength effect.

C — LEV-L10

Global leverage / greedy D-opt query selection.

lambda=0.10.

24 observations.

Isolates:
measurement-design effect
at:
the parent prior.

D — LEV-L03

PRIMARY CANDIDATE.

Global leverage / greedy D-opt.

lambda=0.03.

24 observations.

Tests:
joint conditioning
plus:
weaker prior.

E — AOPT-L03

Global A-optimal trace-reduction design.

lambda=0.03.

24 observations.

Tests:
whether:
total variance reduction
is better aligned
with:
functional reconstruction
than:
D-optimal volume reduction.

F — CONTEXT0

No:
functional feedback.

Developmental-prior floor.

G — CHECKPOINT-ORACLE

Exact lost coefficient restore.

Evaluation ceiling only.

MEASUREMENT SUFFICIENCY METRICS

After:
24 observations,

compute on:
the lesion coefficient design:

1.
rank
of:
Phi_S,R;

2.
smallest singular value;

3.
largest singular value;

4.
condition number
when:
full column rank;

5.
effective rank:

exp(
entropy
of:
normalized singular values
);

6.
trace posterior covariance:

trace(
(Phi^T Phi + lambda I)^-1
);

7.
log determinant precision:

log det(
Phi^T Phi + lambda I
).

These are:
analysis metrics.

They do not:
alter primary policy behavior.

PRIMARY FACTORIAL

3 contexts
x
4 damage fractions
x
2 geometries
x
100 worlds

=
2,400 underlying worlds.

7 policies.

16,800 policy-world evaluations.

COMMON-WORLD DISCIPLINE

All policies in one world share:

- colony;
- learned coefficient field;
- lesion;
- membership schedule;
- 64-query feedback pool;
- feedback targets;
- 256 held-out evaluation queries.

Only:
query selection,
lambda,
or:
oracle access
differs.

PRIMARY METRICS

1. final functional recovery;
2. T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. feedback observations;
6. observations / missing coefficient;
7. design rank;
8. smallest singular value;
9. condition number;
10. effective rank;
11. posterior covariance trace;
12. log-det precision;
13. FIXED-L03 minus FIXED-L10;
14. LEV-L10 minus FIXED-L10;
15. LEV-L03 minus FIXED-L03;
16. AOPT-L03 minus LEV-L03;
17. compact/four interaction;
18. oracle gap.

PRIMARY ACCEPTANCE SHAPE

H156 supports:
MEASUREMENT-CONDITIONED
COGNITIVE MICRO-PATCHING

if:

1.
MIXED 1%..5%,
LEV-L03
median final recovery
>=0.95.

2.
MIXED 1%..5%,
LEV-L03
T90 world fraction
>=0.80
for:
all three

and:
>=0.85
for:
at least two of three.

3.
Relative to:
FIXED-L10,

LEV-L03
improves:
T90 world fraction
by:
>=15 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

4.
PRIOR-STRENGTH DIAGNOSTIC.

FIXED-L03
must improve:
T90 world fraction
over:
FIXED-L10

by:
>=5 percentage points

in:
at least two of:
MIXED 1%,2%,5%

for:
prior over-regularization
to count as:
material.

5.
MEASUREMENT-DESIGN DIAGNOSTIC.

LEV-L10
must improve:
T90 world fraction
over:
FIXED-L10

by:
>=5 percentage points

in:
at least two of:
MIXED 1%,2%,5%

for:
query conditioning
to count as:
material
at:
the parent prior.

6.
LEV-L03
must improve:
T90 world fraction
over:
FIXED-L03

by:
>=5 percentage points

in:
at least two of:
MIXED 1%,2%,5%

for:
design and prior effects
to be:
complementary.

7.
For:
MIXED 1%..5%,

AOPT-L03
must be:
within:
0.03
median final recovery
of:
LEV-L03

in:
at least two of three.

This prevents:
one design objective
from being:
uniquely fragile.

8.
For:
MIXED 1%..5%,

FOUR-PATCH
LEV-L03
T90 world fraction
must be:
within:
15 percentage points
of:
COMPACT

in:
at least two of three.

9.
SMOOTH 1%..5%
LEV-L03
median final recovery
>=0.95.

10.
CHECKPOINT-ORACLE
remains:
the ceiling.

DIAGNOSTIC INTERPRETATION

If:
lambda change helps
but:
query design does not,

then:
the main H152-H155 limit
was:
prior calibration.

If:
query design helps
but:
lambda does not,

then:
measurement conditioning
is:
the main limit.

If:
both help
and:
their combination helps most,

then:
the micro-patch inverse problem
requires:
joint:
experimental design
and:
prior calibration.

If:
neither materially helps,

then:
the 64-query local support itself
or:
the scalar-output functional model
is:
the next bottleneck.

MIXED / NEGATIVE CONDITIONS

Treat H156 as:
mixed / negative
if:

- LEV-L03
  remains:
  below:
  80% T90 reliability;
- weaker prior
  improves held-out error
  only by:
  overfitting local feedback;
- D-opt / A-opt
  produce:
  better matrix conditioning
  without:
  better held-out function;
- FOUR-PATCH
  remains:
  much less reliable;
- fixed order performs:
  as well as:
  information-optimal design;
- the design matrix
  is already:
  effectively full rank
  and:
  well conditioned
  at:
  24 queries,
  implying:
  the bottleneck lies elsewhere.

SANITY

Disjoint sanity family:

20260920490000...

20 worlds / cell:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 2% FOUR;
SCRAMBLED 5% FOUR.

Sanity policies additionally include:

FIXED-L30
and:
LEV-L30

as:
non-primary strong-prior diagnostics.

Sanity:
NON-EVIDENCE.

No:
primary lambda,
query rule,
budget,
or:
acceptance gate
may change
from:
sanity outcomes.

PRIMARY SEEDS

20260920400000
through:
20260920402399.

No execution-semantic change
after:
the first held-out H156 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_JOINT_MEASUREMENT_CONDITIONING_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — JOINT MEASUREMENT CONDITIONING HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H156 HELD-OUT PRIMARY EXECUTION.

UNIQUE SANDBOX HARNESS SHA-256

eeac43258028700bb8d7c7bd00e6e7eee48ba9c55a22307e611e195ab4a75d2d.

The harness is pinned under:
a unique H156-specific filename.

No generic prior-experiment filename
is used
for:
accepted H156 execution.

FIXED DESIGN

Consumes:
the H152 64-query local candidate pool
in:
deterministic generated order.

GLOBAL LEVERAGE DESIGN

Greedy:
maximum

p^T A^-1 p

over:
all unqueried local candidates.

This is:
the frozen greedy D-optimal design.

GLOBAL A-OPT DESIGN

Greedy:
maximum expected
trace-covariance reduction

(p^T Sigma^2 p)
/
(1 + p^T Sigma p).

All query-selection policies:

- read query geometry / basis rows;
- do NOT read:
  unacquired target values.

RIDGE VALUES

Primary:

0.10
and:
0.03.

Sanity-only diagnostic:

0.30.

All were:
declared before:
sanity.

SANITY MATRIX

Disjoint:
20260920490000...
family.

140 underlying worlds.

1,260 policy-world evaluations.

Validation:

- exactly 140 unique sanity seeds;
- nine declared sanity policies / seed;
- zero duplicate seed x policy rows;
- zero functionally-trivial worlds.

SANITY — NON-EVIDENCE SCIENTIFIC SIGNAL

The dominant effect is:
PRIOR STRENGTH.

Representative MIXED results:

1% COMPACT:

FIXED-L10
T90 reach:
80%.

FIXED-L03:
85%.

1% FOUR:

FIXED-L10:
40%.

FIXED-L03:
80%.

LEV-L03:
95%.

AOPT-L03:
95%.

2% FOUR:

FIXED-L10:
20%.

FIXED-L03:
60%.

LEV-L03:
85%.

AOPT-L03:
90%.

5% FOUR:

FIXED-L10:
55%.

FIXED-L03:
85%.

LEV-L03:
90%.

AOPT-L03:
90%.

Strong prior lambda=0.30
is generally worse.

Thus:

the sanity evidence
is consistent with:
lambda=0.10
over-regularizing
the small local inverse problem.

Information-optimal design
appears:
secondary but potentially useful,
especially:
for:
multi-wound geometry.

No:
lambda,
query policy,
budget,
candidate pool,
or:
acceptance threshold
is changed
from:
these sanity outcomes.

PRIMARY FAMILY REMAINS

20260920400000..20260920402399.

No execution-semantic change
is permitted
after:
the first held-out H156 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — JOINT MEASUREMENT CONDITIONING / PRIOR STRENGTH

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / POSITIVE.

FROZEN HARNESS SHA-256

eeac43258028700bb8d7c7bd00e6e7eee48ba9c55a22307e611e195ab4a75d2d.

ACCEPTED PRIMARY FAMILY

20260920400000..20260920402399.

PRIMARY MATRIX

2,400 underlying worlds.

7 policies.

16,800 policy-world evaluations.

Validation:

- exactly 2,400 unique accepted world seeds;
- exact held-out seed interval;
- exactly seven policy rows / seed;
- zero duplicate seed x policy rows;
- zero functionally-trivial worlds;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

LEV-L03.

Global greedy leverage /
D-optimal local-query design.

Ridge lambda:
0.03.

24-observation maximum.

MIXED CONTEXT — PRIMARY TARGET

LEV-L03
median final recovery:

1%:
0.9877.

2%:
0.9678.

5%:
0.9829.

10%:
0.9857.

Thus:

all:
1%..5%
groups
exceed:
the frozen
0.95 median target.

T90 world fraction:

1%:
92.0%.

2%:
83.5%.

5%:
96.0%.

10%:
96.0%.

Frozen reliability requirement:

>=80%
for:
all 1%..5%

and:
>=85%
for:
at least two of three.

PASS.

PRIOR-STRENGTH EFFECT

FIXED-L10
T90 world fraction:

1%:
62.5%.

2%:
57.0%.

5%:
71.5%.

FIXED-L03:

1%:
88.5%.

2%:
76.5%.

5%:
92.5%.

Absolute gain from:
weaker prior

with:
identical query order:

1%:
+26.0 percentage points.

2%:
+19.5.

5%:
+21.0.

Therefore:

lambda=0.10
was:
materially over-regularizing
the local lost-state inverse problem.

This is:
the dominant H156 result.

MEASUREMENT-DESIGN EFFECT
AT:
PARENT PRIOR

LEV-L10
T90 world fraction:

1%:
68.5%.

2%:
60.0%.

5%:
78.5%.

Versus:
FIXED-L10:

gain:

1%:
+6.0 points.

2%:
+3.0.

5%:
+7.0.

The frozen:
>=5-point
two-of-three diagnostic
passes:

1%
and:
5%.

Thus:

information-optimal query placement
is:
material,

but:
smaller
than:
the prior-strength effect.

COMBINED EFFECT

LEV-L03
versus:
FIXED-L10
T90 gain:

1%:
+29.5 points.

2%:
+26.5.

5%:
+24.5.

The full combined policy
therefore:
closes most
of:
the H152-H155
reliability gap

without:
increasing:
the 24-observation cap.

COMPLEMENTARITY TEST

LEV-L03
versus:
FIXED-L03
T90 gain:

1%:
+3.5 points.

2%:
+7.0.

5%:
+3.5.

Only:
2%
exceeds:
the frozen
5-point threshold.

Therefore:

query design
and:
prior weakening
are NOT:
strongly complementary
under:
the frozen gate.

Interpretation:

once:
prior bias
is corrected,

simple local feedback order
already performs:
much better.

Information design
provides:
incremental robustness,
especially:
where geometry
is harder.

A-OPTIMAL COMPARATOR

AOPT-L03
median final recovery:

1%:
0.9874.

2%:
0.9678.

5%:
0.9846.

T90 world fraction:

1%:
92.0%.

2%:
83.5%.

5%:
97.5%.

Difference from:
LEV-L03
median final recovery:

well below:
0.03
for:
all three
small-lesion groups.

PASS.

Thus:

the positive result
does not depend on:
one fragile
experimental-design objective.

FOUR-PATCH RELIABILITY

LEV-L03
T90 world fraction:

1%:

COMPACT:
91%.

FOUR:
93%.

2%:

COMPACT:
91%.

FOUR:
76%.

5%:

COMPACT:
93%.

FOUR:
99%.

FOUR-PATCH
is:
within 15 percentage points
of:
COMPACT

in:
all three
small-lesion groups
at:
the frozen boundary.

The severe:
H152-H155
multi-wound reliability failure
is therefore:
substantially reduced.

Median T90
can still be:
longer
for:
distributed wounds.

Example:

1%:
COMPACT 4
versus:
FOUR 6.

2%:
5
versus:
8.

5%:
6
versus:
7.

Thus:

reliability
and:
latency
remain:
distinct optimization targets.

SMOOTH CONTEXT

LEV-L03
median final recovery:

1%:
0.9993.

2%:
0.9989.

5%:
0.9990.

T90 reach:

99.5%,
100%,
100%.

PASS.

CHECKPOINT ORACLE

Final functional recovery:
1.0.

It remains:
the ceiling.

MEASUREMENT-CONDITIONING DIAGNOSTIC

Information-optimal designs
generally:

- increase:
  useful singular-direction coverage;
- reduce:
  posterior covariance
  relative to:
  same-lambda fixed order;
- improve:
  held-out T90 reliability
  modestly.

However:

the main performance jump
comes from:
reducing prior strength.

This means:

the prior was:
too authoritative
relative to:
the local task evidence.

A developmental prior
should be:

A STARTING POINT,

not:

A HARD ANCHOR.

This is directly analogous to:
the earlier structural-repair lesson:

use:
existing organization

while:
it remains informative,

but:
do not let:
historical structure
overrule:
fresh local evidence.

PREREGISTERED GATE REVIEW

PASS:

1.
LEV-L03
MIXED 1%..5%
median final recovery
>=0.95.

2.
LEV-L03
T90 reliability:
>=80% all three

and:
>=85%
in:
1%
and:
5%.

3.
LEV-L03
improves:
FIXED-L10
by:
>=15 points

in:
all three.

4.
FIXED-L03
improves:
FIXED-L10
by:
>=5 points

in:
all three.

Prior over-regularization:
material.

5.
LEV-L10
improves:
FIXED-L10
by:
>=5 points
in:
two of three.

Measurement design:
material.

6.
AOPT-L03
remains:
within 0.03
of:
LEV-L03
in:
all three.

7.
FOUR-PATCH reliability
is:
within:
the frozen 15-point boundary
for:
all three
small-lesion groups.

8.
SMOOTH quality:
PASS.

9.
ORACLE ceiling:
PASS.

FAIL:

LEV-L03
does not improve:
FIXED-L03
by:
>=5 points
in:
two of three.

Strong design/prior
complementarity:
NOT SUPPORTED.

FINAL INTERPRETATION

H156 is:

POSITIVE.

The H152-H155 reliability limit
was not:
primarily a failure
of:
cognitive micro-patching.

It was substantially:
a calibration failure.

The developmental prior
was:
too strong
for:
the amount of:
fresh local functional evidence.

Once:
the prior is weakened
to:
the preregistered
lambda=0.03 regime,

24 local functional observations
can recover:

approximately:
0.97..0.99
median function

for:
MIXED
1%..5%
micro-lesions

with:
approximately:
84%..96%
T90 world reliability.

Global information-optimal
query design
adds:
a smaller but real gain.

ARCHITECTURAL CONSEQUENCE

The emerging micro-patch rule is:

1.
regenerate:
membership locally;

2.
initialize:
from developmental context;

3.
treat that context as:
a SOFT PRIOR;

4.
allow:
fresh local task evidence
to override:
the prior;

5.
choose:
informative local measurements
when:
geometry is difficult;

6.
solve:
all coupled lost state
jointly.

This is:
a substantially stronger
cognitive micro-patch architecture
than:
H151-H155.

NEXT SCOPED QUESTION

H157 should test:

ADAPTIVE PRIOR AUTHORITY.

Can:
the system infer,
from:
observable local evidence,

how strongly:
to trust:
developmental context

per:
micro-patch,

instead of:
hard-coding
lambda=0.03?

The goal is:

preserve:
H156 reliability

while:
automatically increasing:
prior authority
when:
feedback is sparse/noisy

and:
decreasing it
when:
fresh evidence
strongly contradicts:
the inherited local prior.

H156 DOES NOT AUTHORIZE

- production model repair;
- live cognitive replacement;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
