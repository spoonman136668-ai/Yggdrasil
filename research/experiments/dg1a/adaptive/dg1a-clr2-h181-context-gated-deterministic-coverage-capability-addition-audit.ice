TITLE: DG-1A-CLR2-H181 — Context-Gated Deterministic Coverage Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h180-context-gated-distributed-capability-addition-audit.ice

PURPOSE

H180 established:

- context routing works;
- a six-parameter learned context gate can almost eliminate A interference;
- the broad 64-cell daughter substrate has enough B representational capacity;
- world-level B reliability remains below target because random broad morphology is high variance;
- even the hard-gate ceiling fails the 90% B-reliability gate under random 64-cell morphology.

H181 asks:

CAN A DETERMINISTIC,
TARGET-BLIND
B-CONTEXT COVERAGE MORPHOLOGY

make the SAME:

64 daughter cells,
8 micro-patches,
learned context gate,
B-only daughter fit

reliably B-capable

without increasing:
active structure,
gate complexity,
or:
functional supervision?

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
A/B context domains,
smooth nonlinear teachers,
A context-silence training,
frozen A coefficients,
daughter basis,
daughter micro-offset,
B-residual daughter fit,
learned six-parameter context gate,
hard-gate ceiling,
hibernation/reactivation.

K remains:
64 daughter cells.

Micro-patches:
8.

Approximately:
8 daughter cells / patch.

No:
A functional replay.

No:
B validation or B held-out outputs
enter morphology selection.

MORPHOLOGY INPUT

Morphology may use:

B TRAINING INPUT COORDINATES ONLY.

It may NOT use:

- B training target values;
- B residual values;
- A target values;
- validation outputs;
- held-out outputs.

Thus:

the morphology learns:
WHERE
the B context lives,

not:
WHAT
B computes.

B-CONTEXT DENSITY SCORE

For every right-half parent cell j:

D_j
=
mean over B training inputs:
phi_j(x)^2.

This is:
target-blind.

It measures:
how strongly
that parent location
covers:
the B input distribution.

DETERMINISTIC K-CENTER SEEDS

Candidate parent cells:

x >=0.

Seed 1:

the candidate cell
nearest:
the mean
B-training input coordinate.

For seed 2..8:

for every unselected candidate cell j,

coverage distance:

d_j
=
minimum Euclidean distance
from:
cell center j

to:
any existing seed.

Select:
the candidate maximizing:

D_j
*
d_j.

Tie:

lower cell index.

Thus:

seed selection balances:

B-context density
and:
spatial separation.

No:
B target value
enters:
seed selection.

LOCAL COVERAGE GROWTH

After:
8 seeds

grow:
8 Moore-connected patches
round-robin

until:
64 total sites.

For each patch turn:

among:
unclaimed boundary cells
with:
x>=0,

select:
the cell
with:
largest D_j.

Tie:

lower cell index.

If:
a patch frontier is empty,

reconstruct:
the frontier
from:
all cells
already in:
that patch.

If:
still empty,

choose:
the unclaimed right-half cell

maximizing:

D_j
/
(
1
+
distance
to:
that patch centroid
).

All:
64 daughter coefficients
are:
fit jointly.

POLICIES

A — H180_LEARNED_RANDOM64

Exact H180 learned-gated random broad morphology.

Comparator.

B — H180_HARD_RANDOM64

Exact H180 hard-gated random ceiling.

C — H180_LEARNED_RESIDUAL64

Exact H180 learned-gated residual-driven MULTI8_64.

Comparator.

D — KCOVER_LEARNED64

PRIMARY CANDIDATE.

K=64.

8 deterministic target-blind
coverage patches.

Same:
learned context gate.

E — KCOVER_HARD64

Hard-gate ceiling
for:
the same deterministic
coverage morphology.

F — KCOVER_LEARNED32

Same deterministic
8-patch morphology

but:
K=32.

Strong-support / lower-structure diagnostic.

G — KCOVER_UNGATED64

Same deterministic morphology

without:
context gate.

Tests:
whether morphology alone
can:
avoid A interference.

H — GLOBAL_DAUGHTER

Same raw-capacity ceiling
and:
interference warning.

LEARNED GATE

Exact H180 gate:

features:

[1,x,y,x^2,x*y,y^2].

64 A-context
and:
64 B-context coordinates.

No:
functional targets.

L2:
0.01.

Deterministic IRLS.

One:
shared learned gate
per world.

PRIMARY METRICS

Per policy:

- A baseline R^2;
- pre-add B R^2;
- post-add A R^2;
- post-add B train / validation / test R^2;
- A loss;
- normalized A-output drift;
- B gain;
- B world reliability;
- active-cell count;
- permanent parameter growth;
- gate quality;
- seed centroid spread;
- patch-union radius / area;
- B-context coverage error;
- minimum / median B-input distance
  to:
  nearest daughter center;
- deterministic compute proxy;
- hibernation/reactivation error.

COVERAGE METRIC

For:
B held-out INPUT coordinates only,

report:

mean:
minimum Euclidean distance

to:
the nearest daughter center.

This is:
geometry-only.

No:
held-out target
enters:
selection.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
8.

Policy evaluations:
160.

PRIMARY ACCEPTANCE SHAPE

H181 supports:
DETERMINISTIC
TARGET-BLIND
COVERAGE MORPHOLOGY

if:

1.
A baseline:
median held-out R^2 >=0.90.

2.
KCOVER_LEARNED64:

median B held-out R^2 >=0.90.

3.
KCOVER_LEARNED64:

>=90%
of worlds

finish:
B held-out R^2 >=0.85.

4.
A preservation:

median A R^2 loss <=0.03.

5.
World-level A preservation:

>=90%
of worlds
lose:
<=0.05 A R^2.

6.
A-output drift:

median <=0.05.

7.
LEARNED GATE:

same H180 quality gates:

median context classification accuracy >=0.95;

median A-context activation <=0.10;

median B-context activation >=0.90.

8.
RELIABILITY VALUE:

KCOVER_LEARNED64

world fraction:
B>=0.85

must be:
at least:
10 percentage points
above:
H180_LEARNED_RANDOM64

OR:

reach:
the frozen:
>=90%
target directly.

9.
MORPHOLOGY VALUE:

KCOVER_LEARNED64

median B held-out R^2

must be:
>=0.03
above:
H180_LEARNED_RESIDUAL64

with:
no:
>0.01
additional median A loss.

10.
HARD-GATE CEILING:

KCOVER_HARD64

must:
reach:
>=90%
world-level
B>=0.85.

If:
the hard-gate ceiling
still fails,

then:
64-cell coverage
remains:
insufficiently reliable

even:
with:
ideal routing.

11.
GENERALIZATION:

KCOVER_LEARNED64:

median validation-test gap <=0.05;

median train-test gap <=0.10.

12.
ACTIVE STRUCTURE:

64 daughter cells
<=2%
of:
parent cell count.

13.
PERMANENT PARAMETER GROWTH:

64 daughter coefficients
+
6 gate parameters

<=2.25%
of:
parent coefficient count.

14.
COMPUTE:

median compute
<25%
of:
GLOBAL_DAUGHTER.

15.
HIBERNATION / REACTIVATION:

exact-return gates
from:
H180.

16.
GLOBAL_DAUGHTER
remains:
the raw-capacity ceiling
and:
interference warning.

STRONG SUPPORT

H181 receives:
STRONG support

if:

KCOVER_LEARNED32

also:

- median B R^2 >=0.90;
- >=90%
  world-level B>=0.85;
- median A loss <=0.03.

This would add:
a full new capability

with:
approximately 1%
new active cells

plus:
six routing parameters.

MIXED / NEGATIVE CONDITIONS

Treat H181 as:
mixed / negative
if:

- deterministic coverage
  does not:
  reduce:
  world-level B variance;

- learned gate passes
  but:
  hard-gate ceiling
  still fails:
  90% B reliability;

- geometry-only coverage
  suppresses:
  useful B residual structure;

- K=64
  remains:
  insufficient
  despite:
  deterministic coverage
  and:
  ideal routing;

- the coverage morphology
  improves B
  only by:
  increasing A interference.

NEXT

If H181 succeeds:

proceed directly to:

CLR2-H182 —
SEQUENTIAL CAPABILITY ACCUMULATION.

A
->
add B
->
add C

using:
the accepted:
64-cell routed
coverage morphology.

Measure:

capability growth
versus:

- permanent active cells;
- routing parameters;
- memory;
- compute;
- interference;
- hibernation / reactivation;
- developmental reuse.

If H181 fails
but:
KCOVER_HARD64
passes:

routing learning
is:
still the blocker.

If:
KCOVER_HARD64
also fails:

the next question is:
representational reuse /
shared daughter basis,

not:
more routing tuning.

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
K,
micro-patch count,
density score,
seed-selection rule,
growth rule,
gate,
daughter ridge,
sample count,
or:
acceptance gate

may change
after:
the first held-out H181 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_CONTEXT_GATED_DETERMINISTIC_COVERAGE_CAPABILITY_ADDITION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
