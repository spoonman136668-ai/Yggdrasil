TITLE: DG-1A-CLR2-H181 — Coverage-Balanced Context-Gated Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h180-context-gated-distributed-capability-addition-audit.ice

PURPOSE

H180 established:

- a six-parameter learned context router can preserve A while keeping high B competence;
- the 64-cell distributed daughter budget is representationally sufficient in most worlds;
- learned-gated RANDOM8_64 reaches median B R^2 approximately 0.95 with negligible A damage;
- even the hard-gate ceiling reaches only 85% world-level B>=0.85 reliability.

Therefore:

the remaining failure is not:
routing,
cell count,
or task-output supervision.

It is:
WORLD-TO-WORLD SPATIAL COVERAGE VARIANCE.

H181 asks:

CAN THE SAME
64 DAUGHTER CELLS

with:
the SAME
six-parameter learned context router

reach:
>=90%
world-level B competence

if:
their developmental growth sites
are chosen:
deterministically
to cover:
B input geometry

rather than:
randomly
or:
residual-only?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H180 exactly:

g=.25.

N=3209 parent cells.

Same:
A/B contexts,
teachers,
A context-silence training,
parent ridge,
learned six-parameter context gate,
daughter basis,
daughter micro-offset,
B-residual daughter fitting,
64-cell total daughter budget,
hibernation / reactivation.

Parent A coefficients:
remain frozen.

No:
A task-output replay
inside:
candidate B addition.

COVERAGE INPUTS

Use:
B TRAINING INPUT COORDINATES ONLY

for:
coverage geometry.

B training targets
are:
NOT
used:
to determine:
coverage centroids.

B residual targets
may:
still be used:
inside:
within-patch frontier growth,
as:
already accepted in:
H178/H179.

No:
B validation
or:
B held-out
input / target
enters:
coverage selection.

DETERMINISTIC 8-CENTROID COVERAGE

Run:
deterministic k-means
on:
the 768 B training input coordinates.

Kmeans K:
8.

Initialization:

farthest-point deterministic:

1.
first center:
training point
with:
largest x-coordinate.
Tie:
smallest row index.

2.
each next center:
training point
with:
maximum:
minimum squared distance
to:
existing centers.

Tie:
smallest row index.

Lloyd iterations:

maximum:
50.

Stop if:
assignments unchanged.

Empty cluster:

replace its center
with:
the training point
having:
largest squared distance
to:
its assigned center.

Tie:
smallest row index.

No:
randomness.

MAP CENTROIDS TO PARENT SEEDS

For each:
of:
the 8 k-means centroids,

choose:
the nearest:
right-half parent cell

x>=0.

If:
two centroids
map:
to:
the same parent cell,

resolve:
the later centroid

by choosing:
the nearest:
unused
right-half parent cell.

Tie:
lower parent-cell index.

Thus:

eight:
deterministic,
coverage-balanced
seed locations

span:
the observed B input distribution.

MICRO-PATCH GROWTH

From:
the eight fixed coverage seeds,

grow:
eight:
Moore-connected
micro-patches

round-robin

to:
a total:
64 cells.

Within:
each patch frontier,

choose:
the cell
with:
highest:
H179 B-residual score:

C_j
=
abs(
mean(
phi_j(X_B_train)
*
r_B
)
).

Tie:
lower cell index.

Thus:

COVERAGE
chooses:
WHERE
each micro-patch begins.

RESIDUAL ERROR
chooses:
HOW
each local patch expands.

All:
64 daughter coefficients

are:
fit JOINTLY

to:
B training residual

through:
the frozen H180
learned context gate.

PRIMARY CANDIDATE

LEARNED_GATE_COVER8_64.

HARD-GATE CEILING

HARD_GATE_COVER8_64

uses:
identical
coverage-balanced
64-cell morphology

with:
the H180 hard context gate.

This determines:
whether:
remaining failure
is:
learned-gate leakage

or:
coverage / daughter function capacity.

LOWER-BUDGET DIAGNOSTIC

LEARNED_GATE_COVER8_48.

Same:
8 coverage seeds.

Total:
48 cells.

Six cells / patch.

Tests:
whether:
coverage balance
can reduce:
active-structure growth

below:
the current:
~2% budget.

COMPARATORS

A — LEARNED_GATE_COVER8_64

PRIMARY.

B — HARD_GATE_COVER8_64

Routing ceiling.

C — LEARNED_GATE_COVER8_48

Lower-budget diagnostic.

D — LEARNED_GATE_RANDOM8_64

Exact H180 broad-random
learned-gate comparator
on:
the H181 worlds.

E — HARD_GATE_RANDOM8_64

Exact H180 hard-gate
random comparator.

F — LEARNED_GATE_RESIDUAL8_64

Exact H180
residual-driven
learned-gate comparator.

G — HARD_GATE_RESIDUAL8_64

Hard-gate residual comparator.

H — CONN256

Large connected
ungated reference.

I — GLOBAL_DAUGHTER

Raw-capacity / interference ceiling.

GATE

Exact H180:
one shared
six-parameter
learned context gate
per world.

64 A-context coordinates.

64 B-context coordinates.

No:
task outputs
enter:
gate training.

All learned-gate policies
inside:
one world

reuse:
the exact same
learned gate.

CAPABILITY METRICS

Report:

- A baseline R^2;
- pre-add B R^2;
- post-add A R^2;
- B train / validation / test R^2;
- A R^2 loss;
- normalized A-output drift;
- B gain;
- active daughter cells;
- growth fraction;
- total permanent parameters;
- parameter growth fraction;
- micro-patch count;
- centroid coverage radius;
- maximum B-train-point distance
  to:
  nearest coverage seed;
- mean B-train-point distance
  to:
  nearest coverage seed;
- patch centroid spread;
- B gain / cell;
- deterministic compute proxy;
- gate metrics;
- hibernation / reactivation error.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
9.

Policy evaluations:
180.

PRIMARY ACCEPTANCE SHAPE

H181 supports:
COVERAGE-BALANCED
CONTEXT-GATED
64-CELL CAPABILITY ADDITION

if:

1.
A baseline:
median held-out R^2 >=0.90.

2.
LEARNED_GATE_COVER8_64:

median B held-out R^2 >=0.90.

3.
LEARNED_GATE_COVER8_64:

>=90%
of:
worlds

finish:
B held-out R^2 >=0.85.

This is:
the decisive H180 reliability correction.

4.
A preservation:

median A R^2 loss <=0.03.

5.
World-level A preservation:

>=90%
of worlds

lose:
<=0.05
A R^2.

6.
A output drift:

median <=0.05.

7.
Learned gate quality:

median context classification accuracy >=0.95.

median A-context activation <=0.10.

median B-context activation >=0.90.

8.
COVERAGE VALUE:

LEARNED_GATE_COVER8_64

has:
world-level B>=0.85
rate

at least:
10 percentage points
above:
LEARNED_GATE_RANDOM8_64

OR:

if:
the random comparator
already reaches:
>=90%
inside:
the new H181 primary,

coverage must:
increase:
median B R^2
by:
>=0.03
or:
reduce:
B R^2 standard deviation
by:
>=20%.

9.
Coverage morphology:

must:
reduce:
median
maximum B-training-point
distance
to:
nearest:
daughter seed

relative to:
RANDOM8_64.

10.
GENERALIZATION:

validation-test B R^2 gap <=0.05.

train-test gap <=0.10.

11.
ACTIVE STRUCTURE:

64 daughters
<=2%
of:
parent cell count.

12.
PERMANENT PARAMETER GROWTH:

64 daughter coefficients
+
6 gate parameters

<=2.25%
of:
parent coefficient count.

13.
COMPUTE:

median compute proxy
<25%
of:
GLOBAL_DAUGHTER.

14.
HIBERNATION / REACTIVATION:

exact-return gates
from:
H178-H180.

15.
HARD_GATE_COVER8_64:

must NOT:
have:
lower
world-level B reliability
than:
LEARNED_GATE_COVER8_64
by:
>5 points.

If:
hard coverage
passes
but:
learned coverage fails,

classify:
coverage morphology
as:
supported
but:
learned routing
as:
still insufficient.

16.
GLOBAL_DAUGHTER
remains:
raw-capacity ceiling.

STRONG SUPPORT

H181 receives:
STRONG support

if:

all primary gates pass

AND:

LEARNED_GATE_COVER8_48

also achieves:

median B R^2 >=0.90,

>=90%
world B>=0.85,

median A loss <=0.03.

That would reduce:
new active cells

from:
~1.99%

to:
~1.50%.

MIXED / NEGATIVE CONDITIONS

Treat H181 as:
mixed / negative
if:

- deterministic input coverage
  does not:
  improve:
  world-level B reliability;

- coverage improves:
  mean / median B
  but:
  creates:
  A interference;

- hard coverage
  still:
  fails:
  90%
  B reliability;

- 64 cells
  remain:
  insufficient
  despite:
  routing
  and:
  balanced input coverage;

- the k-means morphology
  overfits:
  B training-input density
  and:
  fails:
  held-out B generalization.

NEXT

If H181 passes:

proceed immediately to:

CLR2-H182 —
SEQUENTIAL CAPABILITY ACCUMULATION.

A
->
add B
->
add C

with:
the accepted:
64-cell
coverage-balanced
context-gated
growth mechanism.

If H181 fails:

do NOT:
immediately increase:
new-cell count.

The next cognitive question becomes:

whether:
capability B
requires:
multiple:
context-specific
subroles / gates

or:
reuse:
of:
parent cellular features

rather than:
more:
new active structure.

SANITY WORLD SEEDS

20260923090000...

PRIMARY WORLD SEEDS

20260923000000
through:
20260923000019.

Sanity:
NON-EVIDENCE.

No:
parent task,
B task,
gate,
daughter K,
k-means K,
k-means initialization,
coverage mapping,
growth rule,
daughter ridge,
sample count,
or:
acceptance gate

may change
after:
the first held-out H181 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_COVERAGE_BALANCED_CONTEXT_GATED_CAPABILITY_ADDITION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
