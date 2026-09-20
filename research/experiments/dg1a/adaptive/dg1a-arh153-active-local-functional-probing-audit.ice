TITLE: DG-1A-AR-H153 — Active Local Functional Probing / Uncertainty-Bounded Micro-Patch Feedback Audit
DATE: 2026-09-19
STATUS: PREREGISTERED / SYNTHETIC / PRIMARY NOT STARTED
TRACK: DG-1A / ADAPTIVE-RULE RESEARCH
BRANCH: dg1a-ar
PARENT: dg1a-arh152-context-functional-feedback-micropatch-audit.ice

PURPOSE

H152 established:

LOCAL DEVELOPMENTAL PRIOR
+
BOUNDED LOCAL FUNCTIONAL FEEDBACK

can:
raise MIXED
1%..5%
median functional recovery

above:
0.90

without:
restoring lost mutable coefficients.

H152 also failed:

- world-level T90 reliability;
- 24-observation efficiency versus 48 observations;
- FOUR-PATCH functional-feedback non-interference.

The next question is:

CAN
THE SAME LOCAL FEEDBACK BUDGET
BE SPENT
MORE INTELLIGENTLY?

H153 tests:

ACTIVE LOCAL PROBING

where:
the controller chooses
which local functional query
to request next

from:
an already-local candidate pool

using only:
known basis geometry
and:
posterior uncertainty.

It does NOT use:

- lost original coefficients;
- held-out evaluation targets;
- latent repair labels;
- global retraining.

BOUNDARY

Synthetic research only.

No:
production model repair,
biological claim,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

PARENT MODEL

Reuse H152 exactly:

- R=8 lattice disk;
- N=197;
- sigma=0.22 RBF readout;
- SMOOTH / MIXED / SCRAMBLED state classes;
- 1%,2%,5%,10% damage;
- COMPACT / FOUR-PATCH lesion geometry;
- H150/H151 membership regeneration;
- repair p=0.50;
- 12 post-membership maturation steps;
- ridge lambda=0.10;
- 64 local candidate feedback queries;
- 256 disjoint held-out evaluation queries.

ACTIVE QUERY RULE

For lesion-cell coefficient vector w_R,
let selected feedback design matrix be P.

Posterior geometry proxy:

A =
P^T P
+
lambda I.

For each unqueried candidate feedback row p_j:

u_j =
p_j^T A^-1 p_j.

Select:
the candidate with maximum u_j.

IMPORTANT:

query selection may read:
candidate query coordinates,
basis responses,
lesion geometry,
and previously selected query identities.

It may NOT read:
the target output of an unselected query.

The target:
becomes available only after:
the query is selected.

COMPONENT-BALANCED ACTIVE QUERY

Map each lesion member
to:
its initial Moore-connected wound component.

Each candidate feedback query
inherits:
the component of
the lesion member
around which it was generated.

For:
multi-component lesions,

allocate successive query slots:
round-robin across components
that still have:
unselected candidate queries.

Inside:
the selected component,

choose:
maximum posterior uncertainty u_j.

This tests:

whether:
explicit information allocation
across wounds

removes:
the H152 FOUR-PATCH interference.

FUNCTIONAL POLICIES

A — RANDOM24

Frozen H152-style:
2 local feedback observations / maturation step.

Maximum:
24.

Candidate queries consumed:
in deterministic generated order.

B — ACTIVE24

Context prior.

2 observations / step.

Maximum:
24.

Global:
maximum posterior-uncertainty selection.

C — COMPONENT24

Context prior.

2 observations / step.

Maximum:
24.

Component-balanced uncertainty selection.

D — COMPONENT-STOP24

Same as:
COMPONENT24

but:
may stop acquiring feedback early
from:
a frozen posterior-uncertainty rule
selected only on:
disjoint sanity seeds.

Maximum:
24.

No held-out functional metric
may drive:
stopping.

E — COMPONENT48

Context prior.

4 observations / step.

Maximum:
48.

Component-balanced uncertainty selection.

Budget-ceiling comparator.

F — FBONLY-ACTIVE24

No developmental context prior.

Zero prior.

2 observations / step.

Maximum:
24.

Uses:
the same active uncertainty rule.

Isolates:
developmental-prior value.

G — CHECKPOINT-ORACLE

Exact lost coefficient restore.

Evaluation ceiling only.

EARLY-STOP SANITY SELECTION

Candidate normalized uncertainty thresholds:

0.50,
0.25,
0.10.

Let:

rho =
max candidate posterior uncertainty
/
initial max candidate uncertainty.

Minimum observations before stopping:
4.

Using only:
disjoint sanity worlds,

choose:
the LARGEST threshold

that keeps:
COMPONENT-STOP24

within:
0.03
median final functional recovery
of:
COMPONENT24

on every declared MIXED sanity cell.

If:
no candidate qualifies,

use:
0.10.

Freeze:
the chosen threshold
before:
held-out primary execution.

PRIMARY FACTORIAL

Context:
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

100 underlying worlds / cell.

2,400 underlying worlds.

7 policies.

16,800 policy-world evaluations.

COMMON-WORLD DISCIPLINE

All policies in one world share:

- colony;
- coefficient field;
- lesion;
- membership schedule;
- candidate feedback pool;
- feedback targets;
- evaluation queries.

Only:
query allocation,
feedback budget,
prior,
or oracle access
differs.

PRIMARY METRICS

1. final functional recovery;
2. functional T50/T90/T99;
3. T90 world fraction;
4. functional downtime;
5. feedback observations consumed;
6. feedback observations per missing coefficient;
7. held-out MSE ratio;
8. lesion-weight RMSE, analysis only;
9. context value versus FBONLY-ACTIVE24;
10. active value versus RANDOM24;
11. component-balance value versus ACTIVE24;
12. COMPONENT24 versus COMPONENT48 gap;
13. early-stop savings;
14. FOUR-PATCH T90 interaction;
15. oracle gap;
16. posterior uncertainty trajectory.

PRIMARY ACCEPTANCE SHAPE

H153 supports:
ACTIVE LOCAL FUNCTIONAL PROBING

if:

1.
MIXED 1%..5%,
COMPONENT24 median final recovery >=0.92.

2.
MIXED 1%..5%,
COMPONENT24 T90 world fraction >=0.85
for all three damage fractions

and:
>=0.90
for at least two of three.

3.
Relative to RANDOM24,
COMPONENT24 improves:
T90 world fraction
by:
>=10 percentage points

in at least:
two of:
MIXED 1%,2%,5%.

4.
FOUR-PATCH
does not incur:
>20%
median functional-T90 penalty
versus:
COMPACT

for:
MIXED 1%..5%.

5.
COMPONENT24
is within:
0.03
median final recovery
of:
COMPONENT48

for:
at least two of:
MIXED 1%,2%,5%.

6.
COMPONENT-STOP24
uses:
<=16
median feedback observations

while remaining:
within 0.03
median final recovery
and:
within 10 percentage points
T90-world fraction
of:
COMPONENT24

for:
at least two of:
MIXED 1%,2%,5%.

7.
For:
SMOOTH and MIXED
1%..5%,

COMPONENT24
beats:
FBONLY-ACTIVE24
by:
>=0.05
median final recovery

in:
at least four of six groups.

8.
CHECKPOINT-ORACLE
remains:
the ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H153 as:
mixed / negative
if:

- active selection does not improve reliability;
- component balancing does not improve FOUR-PATCH behavior;
- early stopping saves little or causes material recovery loss;
- only 48 observations produce reliable recovery;
- active feedback without context matches context+active feedback;
- query selection needs hidden target values;
- surviving original coefficients must change.

SANITY CELLS

Disjoint sanity family:

20260920090000...

20 worlds each:

MIXED 1% COMPACT;
MIXED 1% FOUR;
MIXED 2% FOUR;
MIXED 5% COMPACT;
MIXED 5% FOUR;
SMOOTH 5% FOUR;
SCRAMBLED 5% COMPACT.

Sanity outputs:
NON-EVIDENCE.

PRIMARY SEEDS

20260920000000
through:
20260920002399.

No primary threshold
or policy parameter
may change
after:
the first held-out H153 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_SANDBOX_ACTIVE_LOCAL_FUNCTIONAL_PROBING

canonical_scientific_execution = false
canonical_r1_execution_spent = false
stab18_r1_touched = false


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — ACTIVE QUERY REALIZATION / EARLY-STOP THRESHOLD

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H153 HELD-OUT PRIMARY EXECUTION.

No H153 held-out primary world
has been executed.

ACTIVE POSTERIOR GEOMETRY

For selected query set S:

A =
Phi_S,R^T Phi_S,R
+
0.10 I.

Candidate uncertainty:

u_j =
phi_j,R^T A^-1 phi_j,R.

Selection uses:
u_j only.

The target output
of:
an unselected query
is not:
available to selection.

ACTIVE24

Two query slots / maturation step.

Each slot selects:
the currently unqueried
maximum-u_j
candidate.

COMPONENT24 / COMPONENT48

Each feedback query is tagged by:
the initial Moore-connected lesion component
of:
the lesion member
that generated its local candidate point.

Successive query slots:
round-robin across components
with:
remaining candidates.

Inside the selected component:

choose:
maximum u_j.

RANDOM24

Consumes:
the same candidate pool
in:
deterministic generated order.

FBONLY-ACTIVE24

Uses:
the ACTIVE24 query sequence

with:
zero coefficient prior.

Surviving original coefficients:
remain fixed
for:
all non-oracle policies.

EARLY-STOP THRESHOLD SELECTION

Declared sanity candidates:

rho:
0.50,
0.25,
0.10.

Minimum observations:
4.

Selection rule:

choose:
the largest rho

whose STOP24
median final recovery
remains:
within 0.03
of:
COMPONENT24

on:
every declared MIXED sanity cell.

SANITY RESULT — NON-EVIDENCE

rho=0.50:

fails.

Representative deficits:

MIXED 1% COMPACT:
approximately 0.141.

MIXED 5% COMPACT:
approximately 0.336.

rho=0.25:

fails.

MIXED 5% COMPACT deficit:
approximately 0.0394.

rho=0.10:

passes.

Observed sanity median deficits:
0
on:
all declared MIXED sanity cells.

Therefore:

PRIMARY STOP THRESHOLD

rho =
0.10.

Sanity also shows:

rho=0.10
usually consumes:
the full 24-observation budget.

Thus:

early stopping
is:
a live hypothesis,

but:
pre-primary evidence does not suggest:
large savings.

This observation does not:
change:
the primary acceptance criteria.

FROZEN SANDBOX HARNESS SHA-256

36965c4de5c491aa64da06397f78fb484c88f0ffd640b72c2a5b687aafbe450d.

PRIMARY FAMILY REMAINS

20260920000000..20260920002399.

No execution-semantic change
is permitted
after:
the first held-out H153 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY HARNESS CORRECTION 02 — RESTORED HARNESS HASH / SANITY REPLAY

DATE:
2026-09-19.

STATUS:
FROZEN BEFORE H153 HELD-OUT PRIMARY EXECUTION.

The sandbox copy
of:
the first H153 harness

was overwritten
before:
any held-out H153 primary world
was successfully executed.

The exact prior source bytes
could not be recovered
byte-for-byte.

Therefore:

the prior sandbox harness hash
36965c4de5c491aa64da06397f78fb484c88f0ffd640b72c2a5b687aafbe450d

is:
SUPERSEDED
for:
primary execution.

No H153 primary result
exists
under:
that hash.

The active-query semantics
were reconstructed
from:
the frozen H153 preregistration.

The restored harness was:
recompiled
and:
the complete declared sanity-threshold procedure
was rerun
on:
the same non-evidence sanity family.

RESTORED HARNESS SHA-256

fb8cb34ba01ddb2508dde2f4056f8fac14226d2f3d7640af9ca6908f6900bd45.

SANITY REPLAY

rho candidates:

0.50,
0.25,
0.10.

Under:
the restored harness,

STOP24 consumed:
the full 24-observation maximum

for:
every declared MIXED sanity cell

at:
all three rho values.

Therefore:

all three candidates
produce:
the same final result
as:
COMPONENT24

on:
the declared sanity cells.

By:
the preregistered deterministic selection rule,

choose:
the LARGEST qualifying threshold.

FINAL PRIMARY STOP THRESHOLD

rho =
0.50.

Interpretation:

the current posterior-uncertainty rule
does not:
cross even the 0.50 threshold
inside:
24 observations
on:
the declared sanity cells.

Thus:

the early-stop policy
is expected to:
behave like:
fixed COMPONENT24

unless:
some held-out geometries
close uncertainty faster.

No:
acceptance threshold,
query budget,
ridge lambda,
primary seed,
or:
policy identity
is changed.

HELD-OUT PRIMARY STATUS

NOT STARTED.

Primary family remains:

20260920000000..20260920002399.

No execution-semantic change
is permitted
after:
the first accepted primary world
under:
the restored harness hash.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — ACTIVE LOCAL FUNCTIONAL PROBING

DATE:
2026-09-19.

STATUS:
ACCEPTED PRIMARY COMPLETE / MIXED-NEGATIVE.

FROZEN RESTORED HARNESS SHA-256

fb8cb34ba01ddb2508dde2f4056f8fac14226d2f3d7640af9ca6908f6900bd45.

FINAL STOP THRESHOLD

rho =
0.50.

ACCEPTED PRIMARY FAMILY

20260920000000..20260920002399.

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

MIXED PRIMARY TARGET

COMPONENT24
median final recovery:

1%:
0.9504.

2%:
0.9411.

5%:
0.9370.

10%:
0.9639.

Thus:

active component-balanced probing
preserves:
strong median recovery

and:
passes:
the >=0.92
1%..5%
median gate.

However:

T90 world fraction:

1%:
73.5%.

2%:
67.0%.

5%:
70.5%.

These remain:
below:
the frozen reliability target.

ACTIVE VERSUS RANDOM

RANDOM24
T90 world fraction:

MIXED 1%:
65.5%.

2%:
63.0%.

5%:
62.5%.

COMPONENT24:

1%:
73.5%.

2%:
67.0%.

5%:
70.5%.

Absolute improvement:

1%:
+8.0 percentage points.

2%:
+4.0.

5%:
+8.0.

This is:
real but:
below:
the frozen >=10-point
two-of-three gate.

ACTIVE24
and:
COMPONENT24
are:
very similar.

Therefore:

posterior geometric uncertainty
contains:
some useful query-allocation signal,

but:

component round-robin
does not add:
a large reliability gain.

FOUR-PATCH INTERFERENCE

MIXED COMPONENT24:

1%:

COMPACT:
median T90 5,
reach 83%.

FOUR:
median T90 5,
reach 64%.

2%:

COMPACT:
median T90 5,
reach 90%.

FOUR:
median T90 6,
reach 44%.

5%:

COMPACT:
median T90 6.5,
reach 68%.

FOUR:
median T90 11,
reach 73%.

At:
5%,

FOUR-PATCH
median T90 penalty
is:
approximately 69%.

Thus:

component-balanced query counting
does NOT solve:
multi-wound functional interference.

This gate:
FAILS.

24 VERSUS 48 OBSERVATIONS

COMPONENT48
minus:
COMPONENT24
median final-recovery gap:

MIXED 1%:
approximately 0.0210.

2%:
approximately 0.0148.

5%:
approximately 0.0263.

All three:
are within:
0.03.

Therefore:

24 intelligently allocated observations
capture:
most of:
the 48-observation
median recovery value.

This gate:
PASSES.

The remaining failure
is:
reliability,
not:
median capacity.

EARLY STOPPING

STOP24:

median feedback observations:
24

for:
MIXED 1%,
2%,
5%.

Primary early-stop rate:

0%
across:
those groups.

Median final posterior
uncertainty ratio:

1%:
approximately 0.464.

2%:
approximately 0.447.

5%:
approximately 0.341.

Thus:

the posterior geometry
does not:
close enough uncertainty
inside:
24 observations

to support:
safe early stopping
under:
the frozen rule.

This gate:
FAILS.

DEVELOPMENTAL PRIOR VALUE

COMPONENT24
minus:
FBONLY-ACTIVE24
median final recovery:

SMOOTH:

1%:
+0.508.

2%:
+0.684.

5%:
+0.444.

MIXED:

1%:
+0.453.

2%:
+0.631.

5%:
+0.416.

Thus:

the developmental prior
remains:
strongly useful

even when:
query placement
is active.

This gate:
strongly PASSES.

ORACLE

CHECKPOINT-ORACLE
final recovery:
1.0.

It remains:
the ceiling.

PREREGISTERED GATE REVIEW

PASS:

1.
MIXED 1%..5%
COMPONENT24
median final recovery
>=0.92.

2.
COMPONENT24
within 0.03
of:
COMPONENT48

for:
all three
MIXED small-lesion groups.

3.
Developmental-prior value
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
T90 reliability
>=0.85
for all three
and:
>=0.90
for two.

Observed:
0.670..0.735.

2.
COMPONENT24
>=10 percentage-point
T90 improvement
over:
RANDOM24

in:
two of three.

Observed:
+4..+8 points.

3.
FOUR-PATCH
<=20%
median T90 penalty.

Fails:
most clearly
at:
MIXED 5%.

4.
COMPONENT-STOP24
median feedback
<=16.

Observed:
24.

FINAL INTERPRETATION

H153 is:

MIXED-NEGATIVE.

The useful result is:

QUERY PLACEMENT
MATTERS SOMEWHAT,

and:

24 ACTIVE OBSERVATIONS
ARE ALREADY CLOSE
TO:
THE 48-OBSERVATION
MEDIAN CEILING.

Therefore:

the H152 reliability problem
is NOT primarily:
insufficient total feedback.

It is:

FEEDBACK
NOT BEING CONDITIONED
ON:
THE ACTUAL FUNCTIONAL ERROR
OF:
EACH WOUND.

Posterior parameter uncertainty
is:
a geometry signal.

It does not tell:
which wound currently contributes:
the largest task error.

NEXT SCOPED DIRECTION

RESIDUAL-DIRECTED
COMPONENT-LOCAL
FUNCTIONAL FEEDBACK.

Use:
observed feedback residuals

to:
estimate:
which wound component
still carries:
functional error.

Allocate:
future queries
toward:
that component.

Update:
only:
the selected wound's
regenerated coefficients
per:
local solve,

while:
holding:
surviving cells
and:
other wound estimates
fixed.

The target is:

convert:
the current
~67%..74%
MIXED T90 reliability

toward:
>=90%

without:
increasing:
the 24-observation cap.

H153 DOES NOT AUTHORIZE

- live model repair;
- production thresholds;
- global retraining;
- biological claims;
- STAB-18-R1 execution;
- canonical scientific claims.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
