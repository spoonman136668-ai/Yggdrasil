TITLE: DG-1A-CLR2-H179 — Distributed Micro-Patch Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h178-bounded-developmental-capability-addition-audit.ice

PURPOSE

H178 established a clear capability-addition boundary:

- small connected daughter patches preserve A but underfit B;
- a much larger connected patch learns B but begins to interfere with A;
- error-driven location matters;
- global daughter capacity learns B but catastrophically disturbs A.

H179 asks:

IS THE H178 FAILURE A COVERAGE PROBLEM?

Can the SAME total number of new active cells,
distributed across multiple small developmental micro-patches,

learn a broad new capability B
more effectively than:
one spatially compact daughter colony,

while preserving:
already learned capability A?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H178 exactly:

g=.25.

N=3209 parent cells.

Same:
A / B capability domains,
smooth learned teacher family,
A silence/context constraint,
A ridge training,
B residual target,
daughter-cell basis,
daughter offset,
B-only daughter plasticity,
A frozen parent coefficients,
hibernation / reactivation mechanics.

No:
A replay
inside:
candidate addition.

RESIDUAL SCORE

Reuse H178:

C_j
=
abs(
mean(
phi_j(X_B_train)
*
r_B
)
)

with:

r_B
=
y_B
-
f_A_frozen(X_B_train).

All candidate growth sites:

parent centers
with:
x >=0.

No:
B validation
or:
B held-out
target
enters:
growth selection.

CONNECTED-1 CONTROL

Exact H178:
single connected
error-driven growth path.

MULTI-PATCH SEED SELECTION

For M micro-patches:

1.
seed 1:

highest residual score C_j.

2.
for each next seed:

among:
unselected right-half cells

prefer:
cells with:
Euclidean center distance
>=0.20

from:
every prior seed.

Within:
that admissible set,

select:
maximum residual score C_j.

If:
no cell satisfies:
0.20 separation,

choose:
the cell maximizing:

C_j
*
(
minimum distance
to:
existing seeds
+
1e-6
).

Thus:

seed selection is:

residual-driven
and:
spatially distributed.

No:
target value beyond:
B training residual

enters:
selection.

MICRO-PATCH GROWTH

After seeds are selected:

grow:
M connected patches

round-robin.

Each patch frontier:

Moore-connected.

At:
each patch's turn,

add:
its highest-C_j
boundary cell

that:
is not already claimed
by another patch.

Continue until:
the declared TOTAL
new-cell budget K

is reached.

Budget is split:
as evenly as possible
across:
patches.

All daughter coefficients
across:
all micro-patches

are:
fit JOINTLY

to:
the B training residual.

Thus:

the only changed architectural variable
is:

SPATIAL DISTRIBUTION
OF:
THE SAME
NEW ACTIVE-CELL BUDGET.

POLICIES

A — CONN64

One connected patch.

K=64.

Exact H178 morphology.

B — MULTI4_64

4 distributed patches.

Total K=64.

Approximately:
16 cells / patch.

C — MULTI8_64

8 distributed patches.

Total K=64.

Approximately:
8 / patch.

D — MULTI4_32

4 distributed patches.

Total K=32.

E — MULTI8_32

8 distributed patches.

Total K=32.

F — MULTI4_128

4 distributed patches.

Total K=128.

G — MULTI8_128

8 distributed patches.

Total K=128.

H — RANDOM_MULTI8_64

8 distributed
random right-half seeds

with:
random connected
round-robin growth.

Total K=64.

Training:
identical.

I — CONN256

H178 large connected reference.

K=256.

J — GLOBAL_DAUGHTER

H178 full-capacity ceiling.

K=N.

PRIMARY METRICS

For every policy:

- A baseline R^2;
- pre-add B R^2;
- post-add A R^2;
- post-add B train / validation / held-out R^2;
- A R^2 loss;
- normalized A-output drift;
- B gain;
- new active cells;
- active-cell growth fraction;
- number of micro-patches;
- per-patch cell counts;
- patch centroid spread;
- union macro RMS radius;
- union area proxy;
- daughter coefficient count;
- selection operations;
- fit compute proxy;
- total deterministic compute proxy;
- B gain / active cell;
- B gain / compute;
- hibernation A recovery;
- reactivation B recovery.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
10.

Policy evaluations:
200.

PRIMARY ACCEPTANCE SHAPE

H179 supports:
DISTRIBUTED
DEVELOPMENTAL CAPABILITY ADDITION

if:

1.
A baseline:

median held-out R^2 >=0.90.

2.
At least one:
DISTRIBUTED
K<=64 policy

from:

MULTI4_32,
MULTI8_32,
MULTI4_64,
MULTI8_64

achieves:

median B held-out R^2 >=0.90.

3.
The same policy:

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
<=0.05
A R^2.

6.
A-output drift:

median <=0.05.

7.
SAME-BUDGET MORPHOLOGY VALUE:

at K=64,

at least one:
MULTI4_64
or:
MULTI8_64

has:
median B held-out R^2

>=0.15
above:
CONN64

with:
median A loss
no more than:
0.02 worse.

8.
ERROR-DRIVEN DISTRIBUTION VALUE:

the qualifying distributed policy

has:
median B R^2
>=0.10
above:
RANDOM_MULTI8_64

OR:

uses:
strictly fewer cells
to reach:
median B R^2 >=0.90.

9.
GENERALIZATION:

qualifying policy:

median:
validation-test R^2 gap
<=0.05

and:
train-test gap
<=0.10.

10.
ACTIVE STRUCTURE:

qualifying policy
adds:
<=2%
new active cells.

11.
COMPUTE:

qualifying policy
median compute proxy

<25%
of:
GLOBAL_DAUGHTER.

12.
HIBERNATION / REACTIVATION:

same:
exact-return
gates
as:
H178.

13.
GLOBAL_DAUGHTER
remains:
the B-capacity ceiling.

STRONG SUPPORT

H179 receives:
STRONG support

if:

a K=32
distributed policy

passes:
all:
quality,
A-preservation,
generalization,
compute,
and:
structure gates.

That would add:

approximately:
1%
new active cells

for:
a full new capability.

MIXED / NEGATIVE CONDITIONS

Treat H179 as:
mixed / negative
if:

- distributed patches
  do not:
  improve B coverage
  at:
  the same K;

- distribution improves B
  only by:
  increasing A interference;

- K<=64
  still cannot:
  reach:
  B R^2 0.90;

- connected K=256
  remains:
  necessary;

- random distribution
  performs:
  as well as:
  error-driven distribution;

- multiple patches
  create:
  unstable / redundant
  daughter fits.

NEXT

If H179 succeeds:

proceed to:

CLR2-H180 —
SEQUENTIAL CAPABILITY ACCUMULATION.

A
->
add B
->
add C

using:
the accepted
distributed growth morphology.

Measure:

total capability gain
versus:

- permanent active-cell growth;
- memory;
- compute;
- interference;
- hibernation / reactivation;
- reuse.

If H179 fails:

the next cognition question
should become:

whether:
new capability needs:
TASK-ROUTED
or:
CONTEXT-GATED
cellular specialization

rather than:
more spatial growth.

SANITY WORLD SEEDS

20260922890000...

PRIMARY WORLD SEEDS

20260922800000
through:
20260922800019.

Sanity:
NON-EVIDENCE.

No:
parent task,
B task,
residual score,
seed-separation rule,
micro-patch count,
total K,
growth rule,
daughter fit,
sample count,
or:
acceptance gate

may change
after:
the first held-out H179 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_DISTRIBUTED_DEVELOPMENTAL_CAPABILITY_ADDITION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — DISTRIBUTED CAPABILITY-GROWTH HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H179 HELD-OUT PRIMARY EXECUTION.

FINAL H179 SANDBOX HARNESS

File:

h179_distributed_add_v1.py

SHA-256:

f5a7da30a44a4017b18f9e6df018bfd9346090e775607d426ba65f6c3d36f083.

PARENT CAPABILITY MODEL

Exact H178
accepted capability-addition substrate:

- g=.25;
- N=3209;
- A context-silence training;
- smooth learned A/B teachers;
- frozen parent A coefficients;
- B-residual daughter fitting;
- same daughter basis / offset;
- same B training / validation / test;
- same hibernation / reactivation mechanics.

ONLY CHANGED VARIABLE

Spatial morphology
of:
the new daughter-cell budget.

Residual score:

identical to H178.

MULTI-PATCH SEEDS

Seed 1:

maximum B-residual correlation.

Later seeds:

prefer:
right-half cells

at least:
0.20
normalized macro distance

from:
all previous seeds,

then:
choose:
highest residual score.

If:
the 0.20
separation constraint
cannot be met,

use:
residual score
times:
minimum seed distance.

No:
B validation
or:
B held-out
target
enters:
seed selection.

GROWTH

Each micro-patch:

Moore-connected.

Patches:

grow:
round-robin.

Each patch:
takes:
its highest-residual-score
unclaimed boundary cell.

All:
daughter coefficients

across:
all patches

are:
fit JOINTLY

to:
the same:
B training residual.

Thus:

multi-patch policies

are:
one capability substrate

with:
distributed morphology,

not:
separately trained
ensembles.

POLICIES

CONN64.

MULTI4_64.

MULTI8_64.

MULTI4_32.

MULTI8_32.

MULTI4_128.

MULTI8_128.

RANDOM_MULTI8_64.

CONN256.

GLOBAL_DAUGHTER.

SANITY

Disjoint family:

20260922890000
and:
20260922890001.

2 worlds.

10 policies.

20 evaluations.

Accepted sanity-output SHA-256:

5f8abbbeec8ff7ff72da99c4bece20f4589889dc89244a973486212da9b97271.

Mechanical checks:

- exact 10 policies / world;
- total daughter-cell counts:
  match:
  each frozen budget;
- multi-patch counts:
  exact:
  4 or 8;
- joint daughter solve:
  spans:
  all micro-patches;
- parent A coefficients:
  frozen;
- no:
  A replay;
- no:
  B validation / test
  leakage;
- hibernation / reactivation:
  unchanged.

NON-EVIDENCE SIGNAL

Median sanity
B held-out R^2:

CONN64:
approximately 0.808.

MULTI4_64:
approximately 0.807.

MULTI8_64:
approximately 0.891.

Thus:

8-way distribution

improves:
B coverage

at:
the same:
64-cell budget.

MULTI8_32:

B:
approximately 0.879.

MULTI8_128:

approximately 0.902.

A preservation:

MULTI8_64
median A loss:

approximately 0.0277.

MULTI8_32:

approximately 0.0260.

MULTI8_128:

approximately 0.0311.

Thus:

distribution creates:
a genuine:
coverage / interference
trade-off.

RANDOM_MULTI8_64:

B:
approximately 0.958

but:
median A loss:
approximately 0.139.

Therefore:

broad coverage alone
can:
learn B

while:
badly interfering:
with A.

Residual-driven placement
appears:
important
for:
preservation.

These values are:

NON-EVIDENCE.

No:
seed-separation rule,
patch count,
cell budget,
residual score,
daughter fit,
sample size,
or:
acceptance gate

was changed.

PRIMARY FAMILY

20260922800000..20260922800019.

20 held-out worlds.

10 policies.

200 policy evaluations.

H179 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H179 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
