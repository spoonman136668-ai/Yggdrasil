TITLE: DG-1A-CLR1-H176 — Fine-Scale Cognitive Lesion Boundary / Minimal Repair-Budget Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / COGNITIVE LESION-REGENERATION
BRANCH: dg1a-ar
PARENT: dg1a-clr1-h175-dual-function-cognitive-lesion-regeneration-audit.ice

PROGRAM ROLE

H175 established the first direct proof-of-cognition signal:

a shared fine-grained cellular phenotype can learn two nonlinear functions,
support selective functional lesions,
and restore one damaged function using only target-task local feedback
while preserving the unrelated learned function.

H176 does not revisit whether cognitive micro-patching is possible.

It maps the operating boundary.

PRIMARY QUESTION

At the accepted fine cell scale:

g = 0.25,

what is the largest bounded selective cognitive lesion
that can be repaired reliably,

and what is the minimum target-task functional observation budget
required to do so,

under both repeated same-region damage
and moving responsibility-following damage?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological tissue.
No production model repair.
No canonical scientific execution.
No STAB-18-R1 execution.
No runtime activation.

PARENT COGNITIVE MODEL

Reuse H175 exactly unless explicitly changed below.

Cell scale:

g = 0.25 only.

Body:

unit-disk cellular population,
R = round(8/g),
N approximately 3209.

Two learned nonlinear functions:

A and B.

Teacher class:

same H175 two-layer random nonlinear continuous teachers.

Task-specific training distributions:

same H175 left-lobe / right-lobe 70% local + 30% uniform mixture.

Training / validation / held-out test:

same H175 sample counts and disjointness.

Student:

shared cellular RBF phenotype,
two learned coefficient heads.

Scale-aware ridge:

alpha(g) = 0.01 * g^2.

At g=.25:

alpha = 0.000625.

No task-specific cell identity is hard-coded.

RESPONSIBILITY / SELECTIVE GROWTH PATH

Reuse the H175 responsibility energy and target/other selectivity score.

For each target task T:

seed the cell maximizing:

E[j,T] / (E[j,U] + 1e-12).

Grow one Moore-connected selective path by repeatedly adding the boundary cell
with maximum:

E[j,T] / (E[j,U] + 1e-12).

For the pre-turnover learned state,
define k_star as the first patch size satisfying:

target held-out R^2 loss >= 0.20

AND

unrelated held-out R^2 loss <= 0.05

AND

k_star / N <= 0.10.

If no such k_star exists:

the world is a localization failure.

Do not discard or replace it.

Repair-boundary analysis is conditioned on localization-success worlds,
while the localization-success rate itself remains a reported primary metric.

LESION MAGNITUDE LEVELS

For each localization-success world:

M0 — HALF:
k = max(1, round(0.5 * k_star)).

M1 — BASE:
k = k_star.

M2 — DOUBLE:
k = min(round(2.0 * k_star), floor(0.10*N)).

M3 — TRIPLE:
k = min(round(3.0 * k_star), floor(0.10*N)).

Use the first k cells on the frozen selective growth path.

Record:

- cells;
- body fraction;
- target R^2 loss;
- collateral R^2 loss;
- macro RMS radius;
- macro area proxy.

TRAJECTORY MODES

SAME

Cycle 1:

use the frozen pre-turnover selective patch at the declared magnitude.

Cycles 2..5:

lesion the same cell IDs again.

This tests repeated destruction / regeneration of one cognitive micro-organ.

FOLLOW

At the beginning of every cycle:

recompute responsibility from the policy's CURRENT mutable state.

Rebuild the target-selective connected growth path using the same frozen rule.

Define current k_star_current using the same H175 causal thresholds when possible.

The lesion magnitude uses the ORIGINAL pre-turnover multiplier,
applied to the current k_star_current,
bounded to 10% of body.

If no current causal k_star exists:

use the current path size equal to the previous cycle's lesion-cell count,
bounded to 10%.

This tests whether repair remains stable when functional responsibility reorganizes
and the damaged cognitive patch moves with it.

Report cycle-to-cycle patch Jaccard and centroid displacement.

LESION

Erase both learned coefficient heads inside the selected patch.

Surviving cells and both surviving coefficient heads remain fixed.

No whole-model retraining.

DEVELOPMENTAL REPAIR

Membership regeneration:

same H175 local Moore-frontier rule.

p = 0.50.

Returning cells initialize both heads from live-neighbor means.

After full membership return:

four synchronous context-refinement steps.

FUNCTIONAL REPAIR BUDGETS

All functional observations are from the TARGET task only.

B0 — CONTEXT0:
0 observations / cycle.

B1 — TARGET1:
1 maximum-leverage target-task local observation / cycle.

B2 — TARGET2:
2 maximum-leverage target-task local observations / cycle.

B4 — TARGET4:
4 maximum-leverage target-task local observations / cycle.

No unrelated-task observation is allowed in B0/B1/B2/B4.

Local functional solve:

- target head lesion coefficients only;
- lambda = 0.01;
- current developmental target-head state as prior;
- surviving target coefficients fixed.

The unrelated head receives developmental context repair only.

CONTROL

ORACLE:

restore exact pre-lesion local two-head coefficients
for the current lesion cells.

Local-state ceiling only.

No global retraining candidate is included in H176;
H175 already established the conventional retrain cost comparison.

REPEATED REPAIR

Five lesion / repair cycles per lifetime.

For every cycle report:

- pre-lesion target and unrelated R^2;
- post-lesion target and unrelated R^2;
- post-repair target and unrelated R^2;
- target loss recovered fraction;
- collateral loss;
- patch size / radius / area;
- patch Jaccard to previous cycle;
- patch centroid displacement;
- local validation error;
- global held-out R^2;
- repair observations;
- context neighbor operations;
- local solve dimension;
- deterministic compute proxy.

GENERALIZATION TELEMETRY

H175 omitted a direct repair-query versus held-out generalization-gap field.

H176 corrects that telemetry before primary.

For every cycle create:

1. repair query set:
the actual 0/1/2/4 acquired target observations;

2. local validation set:
128 deterministic target-task points
centered around the lesion macro centroid,
Gaussian jitter sd=0.15,
disjoint from repair queries and global held-out test;

3. global held-out test:
the frozen H175 test set.

Report:

- repair-query target MSE;
- local-validation target MSE;
- global target R^2.

The local validation set is evaluation-only
and cannot enter repair.

PRIMARY FACTORIAL

Worlds:

12 base learned worlds.

Targets:

A, B.

Target-lesion worlds:

24.

Lesion magnitudes:

4.

Trajectory modes:

SAME, FOLLOW.

Repair policies:

CONTEXT0, TARGET1, TARGET2, TARGET4, ORACLE.

Total policy lifetimes:

24 * 4 * 2 * 5
=
960.

Repair cycles:

5.

Total policy repair cycles:

4,800.

PRIMARY METRICS

1. baseline held-out R^2 per learned function;
2. localization-success rate;
3. k_star cells / body fraction / macro radius;
4. lesion target loss;
5. lesion collateral loss;
6. cycle-1 target recovery fraction;
7. cycle-1 world-level joint success;
8. cycle-5 target and unrelated R^2;
9. cycle-5 world-level joint success;
10. local-validation MSE;
11. global held-out R^2;
12. repair-query MSE;
13. patch Jaccard / centroid movement;
14. cells recruited;
15. observation cost;
16. local coefficient updates;
17. deterministic compute proxy;
18. same-versus-follow interaction;
19. magnitude-versus-budget interaction;
20. oracle gap.

JOINT REPAIR SUCCESS

A repaired cycle succeeds iff:

target post-repair held-out R^2
is within:
0.05
of that policy lifetime's original pre-turnover target baseline

AND

unrelated post-repair held-out R^2
is within:
0.05
of its original pre-turnover unrelated baseline.

BOUNDARY QUALIFICATION

For one:

magnitude x trajectory x budget

condition,

call it RELIABLE iff:

1. at least 90% of localization-success worlds
   achieve JOINT REPAIR SUCCESS at cycle 1;

2. at least 90%
   achieve JOINT REPAIR SUCCESS at cycle 5;

3. median unrelated-function loss after repair
   <=0.03 at cycle 1 and cycle 5;

4. median target held-out R^2
   does not decline by >0.03
   from cycle 1 to cycle 5;

5. median local-validation normalized error
   does not exceed:
   1.25x
   the corresponding ORACLE-local-validation error
   after adding a floor of 1e-8 to numerator and denominator.

Because ORACLE error can be numerically tiny,
also report absolute local-validation MSE.
The 1.25x ratio is diagnostic only when ORACLE MSE >1e-6.

PRIMARY ACCEPTANCE SHAPE

H176 supports a robust bounded cognitive repair regime if:

1.
Baseline learning reproduces H175:
median held-out R^2 >=0.90
for both tasks.

2.
Localization success:
>=85%
of target-lesion worlds.

3.
TARGET2 is RELIABLE
for BASE magnitude
under BOTH SAME and FOLLOW.

4.
At least one budget <=2 observations/cycle
is RELIABLE
for DOUBLE magnitude
under SAME.

5.
At least one budget <=2 observations/cycle
is RELIABLE
for DOUBLE magnitude
under FOLLOW.

6.
TARGET1 is RELIABLE
for HALF magnitude
under BOTH SAME and FOLLOW.

7.
CONTEXT0 is NOT allowed to define success.
If CONTEXT0 happens to qualify,
report it as a stronger-than-expected result.

8.
TARGET4 must not produce:
>0.02 median collateral degradation
relative to TARGET2
in any magnitude/trajectory cell.

9.
Repeated repair:
for every condition declared RELIABLE,
cycle-5 joint success remains >=90%.

10.
FOLLOW:
for at least BASE magnitude,
reliable repair must survive
median patch Jaccard <=0.75
OR
median centroid displacement >=0.05.
This prevents a trivial "moving" condition
that never meaningfully moves.

11.
Generalization:
for every RELIABLE target-observation condition,
median global held-out target R^2
remains within 0.05
of original baseline
and
median local-validation MSE does not increase
by >50%
from cycle 1 to cycle 5.

12.
ORACLE remains the local-state ceiling.

MINIMUM BUDGET RESULT

For each:
magnitude x trajectory,

report the lowest observation budget
among:
0,1,2,4

that is RELIABLE.

MAXIMUM LESION RESULT

For each:
trajectory mode

report the largest magnitude level
for which some budget <=2
is RELIABLE.

This is the main H176 cognitive repair boundary.

RESOURCE RESULT

For every reliable boundary point report:

- median lesion cells;
- median body fraction;
- median macro radius;
- median local compute proxy;
- median observations/cycle;
- ratio to H175 whole-model retrain proxy.

MIXED / NEGATIVE CONDITIONS

Treat H176 as mixed / negative if:

- localization success falls below 85%;
- TARGET2 fails BASE under SAME or FOLLOW;
- moving responsibility requires >2 observations;
- unrelated behavior degrades during repeated repair;
- repair-query fit looks good while local validation or held-out generalization degrades;
- larger lesions require near-wholesale local re-estimation;
- FOLLOW responsibility diffuses until selective lesions cease to exist;
- TARGET4 improves target recovery only by increasing collateral interference.

NEXT INFLECTION

If H176 identifies a stable repair boundary
with <=2 observations / cycle
and repeated generalization preservation,

do NOT spend another long block optimizing repair.

Proceed to:

CLR2 — DEVELOPMENTAL CAPABILITY ADDITION

learn A
->
preserve A
->
grow bounded patch for new capability B
->
integrate B
->
preserve A+B.

SANITY WORLD SEEDS

20260922590000...

PRIMARY WORLD SEEDS

20260922500000
through:
20260922500011.

Sanity:
NON-EVIDENCE.

No:
teacher class,
training distribution,
ridge scaling,
localization threshold,
magnitude multiplier,
trajectory definition,
repair budget,
repair policy,
cycle count,
or:
acceptance gate

may change
after:
the first held-out H176 primary world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_COGNITIVE_LESION_REPAIR_BOUNDARY

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — FINE-SCALE COGNITIVE REPAIR-BOUNDARY HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H176 HELD-OUT PRIMARY EXECUTION.

FINAL H176 SANDBOX HARNESS

File:

h176_clr1_boundary_v4.py

SHA-256:

4951c521d2582965b79b4c3026e847189bacf0fd41c2ec1bbecc1d350c786875.

PRE-PRIMARY TASK-DIFFICULTY CALIBRATION

The first reconstructed H176 teacher
was:
too easy.

Representative sanity
held-out R^2:

approximately:
0.9999.

This was:
materially easier
than:
the accepted H175
learned-function band
around:
0.97..0.98.

Two:
NON-EVIDENCE
teacher variants

were also tested
before:
primary.

One:
overshot
and:
underfit severely.

One:
remained:
too easy
and:
weakened:
functional localization.

Neither:
entered:
held-out primary.

FINAL TEACHER

Retains:
the original smooth
H175-style:

- random tanh field;
- low-frequency sinusoid;

and adds:

a small:
high-frequency
deterministic residual

with:
three random Fourier components

and:
amplitude:
0.12.

This yields:

sanity median
held-out R^2:

approximately:
0.9763.

Representative:
sanity held-out R^2

ranges:

approximately:
0.904
to:
0.987.

All remain:
above:
the frozen
world-level competence floor
used by:
the parent cognitive program.

No:
lesion,
repair,
budget,
trajectory,
or:
acceptance rule

was tuned
from:
repair outcomes.

REPRESENTATION

g=0.25.

R=32.

N=3209.

RBF sigma:

0.22.

Student ridge:

alpha =
0.01 * g^2
=
0.000625.

LEARNED FUNCTIONS

Two:
independent nonlinear teachers

A
and:
B.

Training:

768 samples / task.

Validation:

256.

Held-out global test:

512.

Localization geometry:

256
task-distributed
input points

disjoint from:
training
and:
global held-out test.

RESPONSIBILITY / K-STAR

Exact frozen H176 rule.

One:
Moore-connected
selective path

is grown
from:
the highest
target / unrelated
responsibility ratio.

k_star:

first patch
with:

target held-out
R^2 loss >=0.20,

unrelated loss <=0.05,

and:
body fraction <=0.10.

No localization-success world
is discarded.

LESION MAGNITUDES

HALF:
0.5*k_star.

BASE:
1.0*k_star.

DOUBLE:
2.0*k_star.

TRIPLE:
3.0*k_star.

All:
bounded by:
10%
of:
the body.

TRAJECTORIES

SAME:

repeat:
the original
selected cell IDs.

FOLLOW:

recompute:
current responsibility

and:
the connected
target-selective path

at:
every cycle.

If:
a current causal k_star
cannot be found,

preserve:
the previous cycle
lesion-cell count
on:
the current selective path.

REPAIR BUDGETS

CONTEXT0:
0.

TARGET1:
1
target-task
maximum-leverage
local observation / cycle.

TARGET2:
2.

TARGET4:
4.

ORACLE:
local exact
pre-lesion
two-head state restore.

No:
unrelated-task
functional observation

is available
to:
TARGET1,
TARGET2,
or:
TARGET4.

DEVELOPMENTAL REPAIR

Membership:

local Moore-frontier.

Return probability:

0.50.

Returning cell:

live-neighbor mean
for:
both heads.

Then:

4
synchronous
context-refinement steps.

Functional local solve:

target head only.

lambda:
0.01.

Surviving coefficients:

fixed.

GENERALIZATION TELEMETRY

Per cycle:

- actual repair-query MSE;
- 128-point
  lesion-local
  evaluation-only
  validation MSE;
- global held-out
  target R^2.

The local validation set:

is:
disjoint
from:
repair observations

and:
cannot:
enter repair.

SANITY

Disjoint family:

20260922590000
and:
20260922590001.

2 base learned worlds.

4 target-lesion worlds.

4 lesion magnitudes.

2 trajectory modes.

5 policies.

160 policy lifetimes.

Accepted sanity-output SHA-256:

ce2ff5f924b742c26e13ba17847d21e1837664f5b3f9221396ca5bd1e08b2183.

Mechanical checks:

- exact 160 rows;
- exact 5 policies
  in:
  every target / magnitude / mode cell;
- 4 / 4
  target conditions
  localize successfully;
- TARGET1 / TARGET2 / TARGET4
  use:
  exactly:
  1 / 2 / 4
  target observations
  per cycle;
- zero:
  unrelated-task
  observations;
- FOLLOW
  responsibility patches
  move:
  materially
  in:
  sanity.

Representative FOLLOW
median previous-patch Jaccard:

often:
approximately:
0..0.27.

Representative
centroid displacement:

approximately:
0.4..0.7
normalized macro units.

NON-EVIDENCE REPAIR SIGNAL

HALF:

1 observation
is:
generally sufficient
in:
sanity.

BASE:

1..2
observations
are:
strong.

DOUBLE:

2 observations
are:
strong
for:
cycle 1,

while:
FOLLOW repeated repair
begins:
to separate:
2 versus 4
observations.

TRIPLE:

4 observations
is:
materially more reliable
than:
1..2.

This creates:
the intended
nontrivial
budget / lesion boundary.

These values are:

NON-EVIDENCE.

No:
teacher parameter,
magnitude,
trajectory,
repair budget,
threshold,
sample size,
or:
acceptance gate

may change
after:
this freeze.

PRIMARY FAMILY

20260922500000..20260922500011.

12 held-out
base learned worlds.

24 target-lesion worlds.

960 policy lifetimes.

4,800
policy repair cycles.

H176 ACCEPTED PRIMARY STATUS

NOT STARTED.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
