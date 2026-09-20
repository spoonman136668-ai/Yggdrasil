TITLE: DG-1A-AR-H155 — Residual-Routed Global Joint Functional Micro-Patch Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh154-residual-directed-component-local-repair-audit.ice

PURPOSE

H154 established:

FUNCTIONAL ERROR
CAN BE:
LOCALLY OBSERVED

without:
being:
PARAMETER-SEPARABLE
BY WOUND.

Independent component solves:
underperformed
the H152 global lesion solve.

H155 therefore keeps:

LOCAL QUERY ROUTING

but restores:

ONE GLOBAL JOINT SOLVE
OVER:
ALL REGENERATED LESION COEFFICIENTS.

Question:

CAN
OBSERVED PER-WOUND
FUNCTIONAL RESIDUAL

DECIDE:
WHERE TO SPEND
THE NEXT LOCAL FEEDBACK QUERY

while:

JOINT INFERENCE
preserves:
cross-wound coupling?

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
H152/H153/H154.

R=8.
N=197.
sigma=0.22.
repair p=0.50.
ridge lambda=0.10.
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

COMPONENT FEEDBACK POOLS

Each initial Moore-connected wound component
receives:
32 deterministic
local candidate queries.

Jitter:
0.12 body-radius units.

Candidate query targets
are hidden
until:
that query is selected.

ALL ACQUIRED QUERIES
ARE TRAINING DATA.

H155 does NOT:
reserve half the feedback budget
for:
validation.

This is:
a deliberate correction
to:
H154's information inefficiency.

GLOBAL JOINT SOLVE

After:
each acquired feedback query,

solve:

all lesion coefficients
jointly.

Objective:

||Phi_R w_R - residual_target||^2
+
0.10 ||w_R - w_prior||^2.

Surviving original coefficients:
remain fixed.

No:
lost coefficient
is read.

No:
held-out evaluation target
is read.

WITHIN-COMPONENT QUERY CHOICE

For the selected wound component:

choose:
the unqueried candidate
with:
maximum posterior leverage

u_j =
phi_j,R^T
(Phi_R^T Phi_R + 0.10 I)^-1
phi_j,R.

Thus:

component routing uses:
functional residual
or:
uncertainty comparator,

while:
query location inside the component
uses:
geometric information value.

OBSERVED PREFIT RESIDUAL

When query j
is selected:

before:
including its target
in:
the fit,

compute:

e_j =
(y_j - yhat_j)^2.

Compute:
the lesioned-baseline error
for:
the same query:

b_j =
(y_j - y_lesion_j)^2.

Normalized innovation:

z_j =
e_j
/
(b_j + 1e-12).

Clip:
z_j
to:
[0,10].

Each component maintains:

s_c =
EWMA
of:
its acquired z_j

with:
alpha = 0.50.

This score uses only:
already-acquired feedback.

No:
unacquired target
enters:
routing.

BOOTSTRAP

Before:
residual routing,

every wound component
must receive:
at least one acquired query

when:
budget allows.

After bootstrap:

route:
the next query

to:
the component
with:
largest s_c

that still has:
unqueried candidates.

UNCERTAINTY ROUTING COMPARATOR

Component uncertainty score:

mean posterior coefficient variance
over:
lesion coefficients
inside:
that component.

Route:
the next query
to:
largest uncertainty score.

This provides:
a same-pool,
same-global-solve
comparison
against:
residual routing.

FUNCTIONAL POLICIES

A — CONTEXT0

No functional feedback.

B — H152-FIXED-FB2

Frozen H152 comparator.

Generated-order shared local pool.

Global solve.

24 observations.

C — JOINT-FIXED24

Component pools.

Round-robin component routing.

Within component:
maximum leverage query.

Global joint solve.

24 observations.

D — JOINT-UNCERT24

Component pools.

Posterior-uncertainty component routing.

Within component:
maximum leverage.

Global joint solve.

24 observations.

E — JOINT-RESID24

PRIMARY CANDIDATE.

Component pools.

Observed residual component routing.

Within component:
maximum leverage.

Global joint solve.

24 observations.

F — JOINT-RESID48

Same:
residual routing.

48-observation ceiling comparator.

G — CHECKPOINT-ORACLE

Exact lost-state restore.

Evaluation ceiling only.

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

PRIMARY METRICS

1. final functional recovery;
2. T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. feedback observations;
6. observations / missing coefficient;
7. residual-routing score trajectory;
8. routing entropy across wound components;
9. query count per component;
10. compact/four interaction;
11. JOINT-RESID24 versus H152-FIXED;
12. JOINT-RESID24 versus JOINT-FIXED24;
13. JOINT-RESID24 versus JOINT-UNCERT24;
14. JOINT-RESID24 versus JOINT-RESID48;
15. lesion-weight RMSE, analysis only;
16. oracle gap.

PRIMARY ACCEPTANCE SHAPE

H155 supports:
RESIDUAL-ROUTED GLOBAL JOINT REPAIR

if:

1.
MIXED 1%..5%,
JOINT-RESID24
median final recovery >=0.94.

2.
MIXED 1%..5%,
JOINT-RESID24
T90 world fraction >=0.85
for all three damage fractions

and:
>=0.90
for at least two of three.

3.
Relative to:
H152-FIXED-FB2,

JOINT-RESID24
improves:
T90 world fraction
by:
>=10 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

4.
Relative to:
JOINT-FIXED24,

JOINT-RESID24
improves:
FOUR-PATCH
T90 world fraction
by:
>=10 percentage points

in:
at least two of:
MIXED 1%,2%,5%.

5.
For:
MIXED 1%..5%,

FOUR-PATCH
median functional T90
is:
no more than 20%
worse than:
COMPACT

in:
at least two of three
damage fractions.

6.
JOINT-RESID24
is within:
0.03
median final recovery
of:
JOINT-RESID48

for:
at least two of:
MIXED 1%,2%,5%.

7.
JOINT-RESID24
matches or exceeds:
JOINT-UNCERT24
T90 world fraction

in:
at least two of:
MIXED 1%,2%,5%.

8.
SMOOTH 1%..5%
median final recovery
remains:
>=0.95.

9.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H155 as:
mixed / negative
if:

- residual routing
  does not beat:
  fixed routing;
- residual routing
  does not beat:
  uncertainty routing;
- multi-wound T90 interference
  remains;
- only 48 observations
  provide reliable recovery;
- global joint solve
  becomes unstable
  under residual-prioritized sampling;
- residual score
  repeatedly starves:
  one wound component;
- surviving original coefficients
  must change.

SANITY

Disjoint sanity family:

20260920290000...

20 worlds / cell:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 2% FOUR;
SCRAMBLED 5% FOUR.

Sanity:
NON-EVIDENCE.

No:
threshold,
budget,
routing alpha,
or:
acceptance gate
may change
from:
sanity outcomes.

PRIMARY SEEDS

20260920200000
through:
20260920202399.

No execution-semantic change
after:
the first held-out H155 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_RESIDUAL_ROUTED_GLOBAL_JOINT_MICROPATCH

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — RESIDUAL-ROUTED JOINT SOLVE HARNESS

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H155 HELD-OUT PRIMARY EXECUTION.

SANDBOX HARNESS SHA-256

8f786b54cfdc42e4f48aa9b35d4682cd754c3212a37ba3bf2b5ac85938464d8c.

COMPONENT POOLS

32 candidate local feedback queries
per:
initial lesion component.

All acquired queries:
enter:
the global joint training solve.

No:
separate validation pool.

PREFIT INNOVATION

For selected query j:

measure:
the current model residual

BEFORE:
training on j.

Normalize by:
the same query's
lesioned-baseline residual.

Clip:
to:
[0,10].

Component score:

EWMA alpha 0.50.

BOOTSTRAP

Each wound component
receives:
at least one observation
when:
budget permits

before:
pure residual ranking.

GLOBAL SOLVE

After:
each acquired query,

all lesion coefficients
are:
jointly solved

using:
all acquired training observations.

Within one maturation step:

the harmonic context state
at:
the beginning of the step

is used as:
the ridge prior

for:
all sequential query updates
inside:
that step.

Surviving original coefficients:
remain fixed.

WITHIN-COMPONENT SELECTION

Maximum posterior leverage
among:
unqueried candidates
of:
the selected component.

COMPARATORS

JOINT-FIXED24:

round-robin component routing.

JOINT-UNCERT24:

mean posterior coefficient variance
per component.

JOINT-RESID24:

observed prefit residual EWMA.

JOINT-RESID48:

same residual routing
with:
48 nominal maximum observations.

NOTE:

a single-component lesion
has:
only 32 candidate queries.

Therefore:
JOINT-RESID48
can consume:
at most 32
in:
that geometry.

This is:
a candidate-pool ceiling,

not:
an execution error.

SANITY

140 underlying worlds.

980 policy-world evaluations.

Disjoint:
20260920290000
family.

NON-EVIDENCE.

Mechanical checks:

- all seven policies completed;
- acquired targets
  entered:
  global joint inference;
- unacquired targets
  did not:
  enter routing;
- surviving coefficients
  remained fixed;
- oracle remained:
  evaluation-only.

Scientific sanity signal:

- residual routing sometimes improves:
  FOUR-PATCH T90 reach;
- it is not:
  uniformly superior
  to:
  fixed or uncertainty routing;
- larger local-feedback budget
  can:
  reduce held-out final recovery
  in:
  some single-component worlds,
  consistent with:
  local-support overfitting.

No:
threshold,
budget,
alpha,
pool size,
or:
acceptance gate
is changed.

PRIMARY FAMILY REMAINS

20260920200000..20260920202399.

No execution-semantic change
after:
the first held-out H155 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY HARNESS CORRECTION 02 — PINNED RESTORE / PRIMARY-SEED ROLLOVER

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE ACCEPTED H155 PRIMARY EXECUTION.

PROVENANCE INCIDENT

After:
the H155 sanity run
and:
the first pre-primary freeze,

the generic sandbox filename:

h155_sim.py

was overwritten
by:
an older interrupted draft

before:
the nominal 202609202... primary batch
completed.

The resulting 202609202... files
contain:
a different policy matrix

and therefore:
DO NOT MATCH
the frozen H155 protocol.

DISPOSITION

The entire seed family:

20260920200000..20260920202399

is:

CONTAMINATED /
NON-EVIDENCE.

No numerical result
from:
that family

may be used
for:
H155 acceptance,
threshold selection,
or:
scientific interpretation.

No H155 threshold,
budget,
routing coefficient,
or:
acceptance gate
was tuned
from:
those contaminated outputs.

PINNED RESTORED HARNESS

The intended H155 semantics
were reconstructed
from:
the preregistered artifact
and:
the first freeze.

The restored harness
is stored under:
a unique immutable working filename

and has:

SHA-256

f2d9269f93d3d9e8d570d175f9ada0677167f94488e2e46c2505a4f484f178d6.

It implements exactly:

- CONTEXT0;
- H152-FIXED-FB2;
- JOINT-FIXED24;
- JOINT-UNCERT24;
- JOINT-RESID24;
- JOINT-RESID48;
- CHECKPOINT-ORACLE;

with:

- global joint lesion solve;
- component-tagged local feedback pools;
- all acquired queries used for training;
- residual-routing EWMA alpha 0.50;
- posterior-leverage selection inside the routed component;
- surviving original coefficients immutable.

FRESH SANITY FAMILY

The pinned harness was replayed
only on:
a new disjoint
NON-EVIDENCE
sanity family:

20260920390000...

Sanity matrix:

140 underlying worlds.

980 policy-world evaluations.

Validation:

- exactly 140 unique seeds;
- seven policies per seed;
- zero duplicate seed x policy rows;
- zero functionally-trivial worlds.

Scientific sanity signal:

- residual routing
  sometimes helps:
  multi-wound repair;
- it is not:
  uniformly superior
  to:
  fixed or uncertainty routing;
- 48 observations
  may:
  overfit compact local-support geometry.

No:
threshold,
budget,
alpha,
pool size,
or:
acceptance criterion
is changed.

FINAL HELD-OUT H155 PRIMARY FAMILY

20260920300000
through:
20260920302399.

This family
has not been used
for:
sanity,
debugging,
threshold selection,
or:
exploratory interpretation.

No execution-semantic change
is permitted
after:
the first accepted primary world
under:
the pinned harness hash.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — RESIDUAL-ROUTED GLOBAL JOINT FUNCTIONAL REPAIR

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / NEGATIVE.

FINAL PINNED HARNESS SHA-256

f2d9269f93d3d9e8d570d175f9ada0677167f94488e2e46c2505a4f484f178d6.

ACCEPTED PRIMARY FAMILY

20260920300000..20260920302399.

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
- contaminated 202609202... family excluded completely;
- no post-primary parameter tuning.

PRIMARY CANDIDATE

JOINT-RESID24.

MIXED CONTEXT — PRIMARY TARGET

Pooled across:
COMPACT
and:
FOUR-PATCH.

Median final functional recovery:

1%:
0.9384.

2%:
0.9271.

5%:
0.9398.

10%:
0.9547.

Frozen 1%..5% target:

>=0.94.

Observed:

1%:
narrow fail.

2%:
fail.

5%:
narrow fail.

T90 world fraction:

1%:
60.5%.

2%:
59.0%.

5%:
67.5%.

Frozen reliability target:

>=85%
for all three

and:
>=90%
for at least two.

FAIL.

RESIDUAL ROUTING VERSUS H152 FIXED

H152-FIXED-FB2
T90 world fraction:

1%:
57.5%.

2%:
56.0%.

5%:
66.5%.

JOINT-RESID24:

1%:
60.5%.

2%:
59.0%.

5%:
67.5%.

Improvement:

+3,
+3,
+1
percentage points.

Frozen target:

>=10 percentage points
in:
at least two of three.

FAIL.

RESIDUAL ROUTING VERSUS JOINT FIXED / UNCERTAINTY

JOINT-FIXED24
T90 world fraction:

1%:
61.0%.

2%:
59.5%.

5%:
73.0%.

JOINT-UNCERT24:

1%:
61.0%.

2%:
59.5%.

5%:
73.5%.

JOINT-RESID24:

1%:
60.5%.

2%:
59.0%.

5%:
67.5%.

Thus:

residual routing
does NOT:
beat:
fixed component allocation

and:
does NOT:
beat:
posterior-uncertainty routing.

At:
5% damage,

it is:
materially worse.

FOUR-PATCH RESULT

JOINT-RESID24
MIXED median T90
among worlds reaching T90:

1%:

COMPACT:
4.

FOUR:
5.

ratio:
1.25.

2%:

COMPACT:
5.

FOUR:
5.

ratio:
1.00.

5%:

COMPACT:
7.

FOUR:
8.

ratio:
approximately 1.14.

Frozen <=20% penalty gate:

passes:
2%
and:
5%.

fails:
1%.

Thus:

the joint solve
does:
reduce the severe
H154 parameter-separation failure.

However:

world-level T90 reach
still differs strongly
between:
COMPACT
and:
FOUR-PATCH

at:
2%:

80%
versus:
38%.

The multi-wound
reliability problem
remains.

FOUR-PATCH ROUTING COMPARISON

T90 world fraction:

1%:

JOINT-FIXED24:
57%.

JOINT-UNCERT24:
57%.

JOINT-RESID24:
56%.

2%:

39%,
39%,
38%.

5%:

70%,
71%,
59%.

Residual routing:
does not improve
FOUR-PATCH reliability.

FAIL.

24 VERSUS 48 OBSERVATIONS

JOINT-RESID48
median final recovery:

1%:
0.9135.

2%:
0.8895.

5%:
0.9246.

Absolute difference
from:
JOINT-RESID24:

1%:
approximately 0.0249.

2%:
approximately 0.0376.

5%:
approximately 0.0152.

The frozen within-0.03 gate
passes:
1%
and:
5%.

But:

48 observations
often reduce:
final held-out recovery

while:
increasing:
T90 reach.

This reinforces:
the sanity warning:

MORE LOCAL FEEDBACK
CAN:
OVERFIT
THE LOCAL QUERY SUPPORT.

The problem is:
measurement design / conditioning,

not:
simple feedback quantity.

UNCERTAINTY ROUTING COMPARISON

JOINT-RESID24
does NOT:
match or exceed
JOINT-UNCERT24
T90 fraction

in:
any of:
MIXED 1%,
2%,
5%.

FAIL.

SMOOTH CONTEXT

JOINT-RESID24
median final recovery:

1%:
0.9968.

2%:
0.9950.

5%:
0.9961.

SMOOTH safety / quality:
PASS.

SCRAMBLED CONTEXT

JOINT-RESID24
median final recovery:

1%:
0.6455.

2%:
0.4677.

5%:
0.6393.

10%:
0.6720.

Thus:

feedback plus harmonic prior
still recovers:
some arbitrary-state function,

consistent with:
H152's generic-regularization warning.

ORACLE

CHECKPOINT-ORACLE
final recovery:
1.0.

It remains:
the ceiling.

PREREGISTERED GATE REVIEW

PASS:

- FOUR-PATCH median-T90 penalty
  <=20%
  in:
  two of three
  MIXED small-lesion groups;

- JOINT-RESID24
  within 0.03 median final recovery
  of:
  JOINT-RESID48
  in:
  two of three
  small-lesion groups;

- SMOOTH 1%..5%
  median recovery >=0.95;

- CHECKPOINT-ORACLE
  remains:
  the ceiling.

FAIL:

- MIXED 1%..5%
  median >=0.94;

- MIXED T90 reliability;

- >=10-point reliability gain
  over:
  H152 fixed feedback;

- residual-routing gain
  over:
  fixed component routing;

- residual-routing gain
  over:
  uncertainty routing;

- FOUR-PATCH reliability improvement.

FINAL INTERPRETATION

H155 is:

NEGATIVE.

The negative result is:
informative.

H154 showed:

do NOT:
solve wound components
independently.

H155 now shows:

even when:
all wound parameters
are solved jointly,

routing queries
toward:
the largest observed wound residual

does NOT:
solve:
the reliability limit.

The best 24-observation policies
in H155 are:
the simpler:

JOINT-FIXED24
and:
JOINT-UNCERT24.

Therefore:

the remaining bottleneck
is not primarily:

WHICH WOUND
GETS THE NEXT QUERY?

It is:

WHETHER
THE 24-QUERY
MEASUREMENT SET
SUFFICIENTLY CONDITIONS
THE JOINT
LOST-STATE
INVERSE PROBLEM.

NEXT SCOPED DIRECTION

GLOBAL INFORMATION-DESIGN
FOR:
LOCAL MICRO-PATCH FEEDBACK.

Use:
the same 24-observation cap,

but choose queries
to maximize:
joint information
about:
all missing coefficients,

rather than:
first allocating by:
wound identity.

Candidate directions:

- global posterior leverage;
- D-optimal log-determinant gain;
- diversity / conditioning penalty;
- explicit rank / effective-dimension tracking;
- feedback stopping
  based on:
  measurement sufficiency
  rather than:
  wound residual.

Do NOT:

increase:
the primary observation cap
as:
the first response.

H155 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- global retraining;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
