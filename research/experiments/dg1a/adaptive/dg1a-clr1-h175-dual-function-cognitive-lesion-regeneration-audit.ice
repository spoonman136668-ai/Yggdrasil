TITLE: DG-1A-CLR1-H175 — Dual Learned Function Localization / Selective Cognitive Lesion-Regeneration Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / COGNITIVE LESION-REGENERATION
BRANCH: dg1a-ar
PARENT: dg1a-arh173-non-ratcheting-learned-state-amplitude-envelope-audit.ice

PROGRAM ROLE

This is the first experiment in:
Cognitive Lesion-Regeneration 1.

Research allocation from this point:

approximately 80%:
proof-of-cognition

and:
20%:
substrate de-risking
only when:
the substrate directly constrains
cognitive results.

H174 substrate-only continuation
was:
superseded before primary.

PRIMARY QUESTION

Can one developmental cellular phenotype:

1.
learn:
two separable functions;

2.
develop:
measurably different
cellular responsibility maps
for:
those functions;

3.
suffer:
a bounded selective lesion
that damages:
one learned function
more than:
the other;

4.
restore:
the damaged function
through:
bounded local developmental repair;

5.
preserve:
the unrelated learned function;

6.
repeat:
that lesion / repair process

without:
global retraining
or:
checkpoint restoration?

BOUNDARY

Synthetic computational research only.

No:
wetware,
biological tissue,
production model repair,
STAB-18-R1 execution,
canonical scientific execution,
or runtime activation.

CELLULAR BODY

Reuse:
the accepted Yggdrasil
unit-disk cellular body
and:
Gaussian local readout basis.

Compare:

COARSE:
g=1.00.

FINE:
g=0.25.

Expected body sizes:

approximately:
197
and:
3209
cells.

Each cell carries:
two learned functional coefficients:

w_A[j],
w_B[j].

The:
cell position,
neighborhood,
and:
developmental repair graph

are:
shared
between:
both learned functions.

No:
task-specific cells
are:
hard-coded.

LEARNED FUNCTIONS

Two:
continuous nonlinear
regression functions

are:
learned from examples.

They are NOT:
implemented
as:
lookup tables.

One world contains:
two independent
teacher functions:

A
and:
B.

Teacher form:

two-layer random nonlinear
continuous function
on:
normalized x,y

using:
tanh features
plus:
a small sinusoidal component.

Teacher parameters:
world-seed deterministic.

The student:

does NOT:
receive:
teacher parameters.

It receives only:
training input / target pairs.

TASK-SPECIFIC TRAINING DISTRIBUTIONS

Function A
is trained on:

70%
samples from:
a broad left-lobe distribution

center:
(-0.35, 0.00)

sd:
0.32

truncated:
to unit disk,

plus:

30%
uniform unit-disk samples.

Function B:

70%
from:
a broad right-lobe distribution

center:
(+0.35, 0.00)

sd:
0.32,

plus:
30%
uniform.

This:

induces:
a plausible pressure
for:
different spatial responsibility

without:
assigning:
any cell
to:
a task.

The 30%:
global component

prevents:
complete domain disjointness

and:
creates:
shared / overlapping responsibility.

TRAINING

Per:
function
and:
world:

768 training samples.

256 validation.

512 held-out test.

Student fit:

ridge regression
over:
the cellular RBF basis.

Ridge alpha:

0.01.

A
and:
B

are:
fit independently
but:
share:
the same cell population.

BASELINE METRICS

Per function:

- R^2;
- normalized RMSE;
- output variance;
- coefficient RMS;
- generalization gap.

Baseline competence:

R^2
on:
held-out test.

FUNCTIONAL RESPONSIBILITY MAP

For:
each cell j
and:
task t,

define:
target-blind-to-other-task
contribution energy:

E[j,t]
=
mean_test(
(
phi_j(x)
*
w_t[j]
)^2
).

This uses:
the learned student
and:
held-out input geometry

but:
not:
the other task target.

Selectivity for:
target T
against:
other U:

S[j,T]
=
E[j,T]
/
(
E[j,T]
+
E[j,U]
+
1e-15
).

LOCALIZATION MEASURES

Report:

1.
top-10%
A/B
importance Jaccard;

2.
weighted responsibility centroid;

3.
weighted RMS spatial radius;

4.
largest connected-component fraction
inside:
top-10%
importance;

5.
task-selectivity distribution;

6.
causal connected-patch lesion curve.

CAUSAL PATCH SEARCH

For:
each target task
T
in:
{A,B},

construct:
one connected target-selective patch.

Seed:

cell maximizing:

E[j,T]
/
(
E[j,U]
+
1e-12
).

Grow:
one Moore-connected patch

by repeatedly adding:
the boundary cell
with:
maximum:
E[j,T]/(E[j,U]+1e-12).

At:
each patch size k,

lesion means:

set BOTH:
w_A
and:
w_B

to:
zero

for:
the patch.

Measure:

target R^2 loss:

Delta_T(k)
=
R2_T_baseline
-
R2_T_lesioned.

Collateral loss:

Delta_U(k)
=
R2_U_baseline
-
R2_U_lesioned.

LOCALIZATION SUCCESS

First k
satisfying:

Delta_T >=0.20

AND:

Delta_U <=0.05

AND:

k/N <=0.10.

If:
none exists,

the world remains:
a localization failure.

Do NOT:
discard
or:
replace
the world.

For downstream repair:

use:
the best connected patch
within:
the 10%-of-body cap,

where:
best =
maximum:
Delta_T
-
2*max(Delta_U,0).

RANDOM PATCH CONTROL

For:
each target lesion,

construct:
one matched-size
random connected patch

from:
a deterministic random seed.

Report:

target / collateral loss

for:
the selective patch
and:
the matched random patch.

TASK-PATCH OVERLAP

Because:
A and B
are:
both localized independently,

report:

Jaccard overlap

between:
the selected A patch
and:
selected B patch.

This measures:
functional separability
rather than:
assuming it.

LESION

A repair cycle:

1.
select:
the frozen target-task patch
from:
the pre-cycle responsibility map;

2.
erase:
both:
w_A
and:
w_B

inside:
that patch;

3.
keep:
all surviving cells
fixed;

4.
regenerate:
only:
the lesioned population.

No:
global coefficient update.

No:
whole-model retraining.

REPAIR MECHANICS

Structural / developmental stage:

- membership returns:
  through:
  local Moore-frontier regeneration;
- p=0.50;
- returning cell:
  initializes:
  each task coefficient
  from:
  live-neighbor mean;
- four:
  synchronous
  context-refinement steps
  after:
  full membership return.

Functional correction:

local only.

Query pool:

64
target-task
lesion-local
queries.

Query selection:

maximum leverage
inside:
the restored lesion.

Local solve:

dual ridge update
around:
the current developmental prior.

lambda:
0.01.

Surviving cells:

fixed.

REPAIR POLICIES

A — CONTEXT-ONLY

No:
functional observations.

Both functions:
developmental context only.

B — TARGET2

PRIMARY CANDIDATE.

Two:
target-task
local functional observations

per:
repair cycle.

Repair:
target-task
lesion coefficients

using:
those observations.

Other learned function:

receives:
context reconstruction only.

This is the key:
selective cognitive micro-patch test.

C — DUAL2

Two:
target-task observations

plus:

two:
other-task observations.

Local functional correction
for:
both heads.

Control for:
whether:
collateral preservation
requires:
explicit supervision.

D — GLOBAL-RETRAIN

Control only.

Refit:
the complete two-head student

from:
its original training examples.

This is:
NOT:
a candidate regenerative mechanism.

Report:
accuracy / cost ceiling
for:
conventional retraining.

E — LOCAL-CHECKPOINT-ORACLE

Restore:
the exact pre-lesion
two-head coefficient state

for:
the lesioned cells.

Evaluation ceiling only.

REPEATED REPAIR

Each policy lifetime:

5 lesion / repair cycles.

The same:
target function
is:
lesioned
for:
all five cycles.

At:
each cycle:

recompute:
the target-selective
connected patch

from:
the policy's CURRENT
mutable state

using:
the same frozen
patch-search rule.

This allows:
responsibility
to:
move
or:
reorganize.

Do NOT:
force:
the original patch location.

Report:

patch overlap
cycle-to-cycle

and:
responsibility-map drift.

GENERALIZATION

Functional observations
used for:
TARGET2 / DUAL2

are:
disjoint

from:
held-out test points.

Evaluate:

held-out
R^2
before lesion,
after lesion,
after repair,
and:
after cycle 5.

RESOURCE METRICS

Report:

- cells lesioned;
- lesion fraction;
- macro patch radius;
- macro patch area proxy;
- target observations;
- other-task observations;
- local coefficient updates;
- active cell count;
- context neighbor operations;
- local solve dimension;
- global-retrain sample count;
- deterministic compute proxy.

COARSE VERSUS FINE

Explicitly compare:

g=1.00
versus:
g=0.25

for:

- minimum cells needed
  for selective target damage;
- lesion fraction;
- macro patch radius;
- collateral function loss;
- repair observations;
- repair compute proxy;
- cycle-5 behavioral drift;
- responsibility-map drift.

PRIMARY FACTORIAL

Cell scale:

2.

Target task:

A,
B.

Worlds / cell:

20.

Underlying target-lesion worlds:

2 x 2 x 20
=
80.

Policies:

5.

Policy lifetimes:

400.

Repair cycles:

5.

Total policy repair cycles:

2,000.

PRIMARY ACCEPTANCE SHAPE

CLR1-H175 supports:
SELECTIVE
COGNITIVE LESION-REGENERATION

if:

1.
BASELINE LEARNING:

median held-out
R^2

>=0.90

for:
both A and B

at:
both scales.

2.
WORLD-LEVEL BASELINE:

>=90%
of:
worlds

have:
both functions
R^2 >=0.85.

3.
MEASURED LOCALIZATION:

>=80%
of:
target-lesion worlds

find:
a connected patch
within:
10%
of body

with:

target R^2 loss
>=0.20

and:

collateral R^2 loss
<=0.05.

4.
CAUSAL SPECIFICITY:

selective-patch
median target damage

is:
>=2x

the:
matched random-patch
target damage

at:
both scales.

5.
TASK SEPARABILITY:

median:
A/B
selected-patch Jaccard

<=0.25

at:
both scales.

6.
ONE-CYCLE TARGET REPAIR:

TARGET2
recovers:
>=90%
of:
the target-function
R^2 loss

in:
median

for:
both scales
and:
both target tasks.

7.
ONE-CYCLE COLLATERAL PRESERVATION:

TARGET2
other-function
post-repair R^2

is:
no more than:
0.03 below:
its pre-lesion baseline

in:
median

for:
both scales
and:
both target tasks.

8.
WORLD-LEVEL REPAIR:

>=90%
of:
localization-success worlds

finish:
cycle 1

with:

target R^2
within:
0.05
of baseline

AND:

other-function R^2
within:
0.05
of baseline.

9.
REPEATED REPAIR:

after:
cycle 5,

TARGET2
median:

target R^2
and:
other-function R^2

remain:
within:
0.05
of:
their original baselines

for:
both scales / targets.

10.
NO WHOLESALE RETRAINING:

TARGET2
uses:

exactly:
2
target functional observations
per:
cycle

and:

zero:
other-task
functional observations.

11.
DUAL2 DIAGNOSTIC:

if:
DUAL2
materially outperforms:
TARGET2
on collateral preservation,

report:
that:
selective repair
still depends on:
explicit supervision
of:
the supposedly unrelated function.

Do NOT:
hide this
behind:
target recovery.

12.
FINE-GRANULARITY TEST:

g=0.25

must NOT:
have:
higher
median collateral damage
than:
g=1.00

and:

must use:
no more:
functional observations.

13.
GENERALIZATION:

TARGET2
post-cycle-5
held-out R^2

must:
track:
repair-query
performance

without:
>0.05
median gap
attributable to:
overfitting
the local repair observations.

14.
ORACLE:

LOCAL-CHECKPOINT-ORACLE
remains:
the local-state ceiling.

MIXED / NEGATIVE CONDITIONS

Treat H175 as:
mixed / negative
if:

- two learned functions
  do not:
  develop:
  measurably separable
  responsibility maps;

- selective lesions
  require:
  >10%
  of:
  the body;

- damaging:
  one function
  substantially damages:
  the other;

- TARGET2
  restores:
  the target
  only by:
  corrupting:
  the unrelated function;

- DUAL2
  is required
  for:
  collateral preservation;

- repeated repair
  causes:
  responsibility maps
  to:
  diffuse
  or:
  drift;

- fine cells
  do not:
  reduce:
  collateral interference
  or:
  repair footprint;

- global retraining
  is:
  the only mechanism
  that reliably restores:
  both functions.

SANITY WORLD SEEDS

20260922490000...

PRIMARY WORLD SEEDS

20260922400000
through:
20260922400079.

Sanity:
NON-EVIDENCE.

No:
teacher class,
training distribution,
ridge alpha,
localization thresholds,
patch-search rule,
repair observation budget,
repair policy,
cycle count,
cell scale,
or:
acceptance gate

may change
after:
the first held-out H175 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_COGNITIVE_DUAL_FUNCTION_LESION_REGENERATION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — CLR1 DUAL-FUNCTION LEARNED COGNITIVE HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE CLR1-H175 HELD-OUT PRIMARY EXECUTION.

FINAL H175 SANDBOX HARNESS

File:

h175_clr1_v2.py

SHA-256:

0d087886ca034c07b808f194de87074991f9e226b683838cadf782a4ac1144be.

PRE-PRIMARY REPRESENTATION-SCALE CORRECTION

Initial sanity harness:

h175_clr1_v1.py

used:

fixed ridge alpha:
0.01

at:
both cell scales.

That caused:

fine g=0.25
learned-task underfitting

despite:
otherwise healthy
localization / repair mechanics.

Representative fine-scale
held-out R^2
under:
the v1 sanity run:

approximately:
0.74..0.92.

This was:
a scale-of-representation
training defect,

not:
a lesion / repair result.

Before:
any held-out H175 primary world
was executed,

the student ridge penalty
was changed to:

alpha(g)
=
0.01
*
g^2.

Thus:

g=1.00:
alpha=0.01.

g=0.25:
alpha=0.000625.

This follows:
the existing small-cell
area-scaling logic

and:
prevents:
finer cellular discretization
from:
receiving:
disproportionately strong
coefficient shrinkage.

No:

- teacher;
- task distribution;
- localization threshold;
- lesion search;
- repair observation budget;
- repair policy;
- cycle count;
- acceptance gate

was changed.

The v1 sanity output
is:

NON-EVIDENCE.

SANITY

Disjoint family:

20260922490000...

8 target-lesion worlds.

5 policies.

40 policy lifetimes.

Accepted sanity-output SHA-256:

f349b2cf52fd0b07b3b6889907f7e103d00050bf773dbcedb5a34e482e474205.

Mechanical checks:

- exactly five policies / sanity world;
- exact eight sanity worlds;
- both learned heads
  share:
  one cell population;
- no task-specific cell identity
  is hard-coded;
- localization uses:
  a dedicated localization set
  disjoint from:
  training
  and:
  held-out test;
- repair observations
  are disjoint from:
  held-out test;
- TARGET2:
  exactly two target-task
  functional observations / cycle;
- TARGET2:
  zero other-task observations;
- GLOBAL-RETRAIN:
  control only;
- LOCAL-CHECKPOINT-ORACLE:
  local-state ceiling only.

NON-EVIDENCE LEARNING SIGNAL

Coarse held-out R^2:

approximately:
0.94..0.99.

Fine held-out R^2:

approximately:
0.96..0.99
in:
the accepted v2 sanity
except:
no target condition
below:
the preregistered world-level
0.85 floor.

NON-EVIDENCE LOCALIZATION SIGNAL

All:
8 / 8
target conditions

find:
a selective
connected target lesion

inside:
the frozen
10%-of-body cap.

Representative target-function
R^2 loss:

approximately:
0.19..0.28.

Representative collateral loss:

approximately:
0..0.004.

Matched random-patch
target loss:

typically:
much smaller

at:
approximately:
0.002..0.031.

Selected A/B patch Jaccard:

0
in:
the eight sanity conditions.

NON-EVIDENCE REPAIR SIGNAL

TARGET2
median cycle-1
recovery fraction

by:
scale / target

is:
approximately:
0.92..0.99
at:
g=1.00

and:
approximately:
0.93..0.94
at:
g=0.25.

Other-task R^2
remains:
near:
pre-lesion baseline

without:
other-task
functional observations.

Repeated:
cycle-5
target / collateral
metrics

remain:
near:
baseline
in:
the sanity matrix.

These outputs are:

NON-EVIDENCE.

No:
scientific threshold,
task,
lesion rule,
repair budget,
or:
acceptance gate

was selected
from:
these values.

PRIMARY FAMILY

20260922400000..20260922400079.

80 held-out
target-lesion worlds.

5 policies.

400 policy lifetimes.

5 repair cycles / lifetime.

2,000
policy repair cycles.

H175 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H175 primary world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
