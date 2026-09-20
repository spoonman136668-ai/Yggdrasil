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
