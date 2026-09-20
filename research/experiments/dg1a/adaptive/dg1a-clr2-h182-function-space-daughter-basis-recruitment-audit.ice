TITLE: DG-1A-CLR2-H182 — Sparse Function-Space Daughter-Basis Recruitment Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h181-context-gated-deterministic-coverage-capability-addition-audit.ice

PURPOSE

H178-H181 established:

- 64 daughter cells can have enough raw B representational capacity;
- context routing can preserve A;
- random broad morphology is high-capacity but unreliable;
- residual-local morphology under-covers B;
- Euclidean input-space coverage is not equivalent to learned function-space coverage.

The remaining question is:

CAN:
B TRAINING TARGETS
BE USED:
DURING CAPABILITY LEARNING

to recruit:
a sparse,
nonredundant,
64-cell daughter basis

that reliably represents B

while:
the already accepted
context gate
protects A?

This is not repair.

Capability B is:
being learned for the first time.

Therefore:

B training targets
are legitimate information
for:
new-capability structure selection.

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H180/H181 exactly:

g=.25.

N=3209 parent cells.

Same:
A/B domains,
smooth nonlinear teachers,
A context-silence training,
frozen A coefficients,
daughter basis width,
daughter micro-offset,
six-parameter learned context gate,
B-only daughter fitting,
hibernation/reactivation.

Parent A:
frozen.

No:
A target replay
inside:
candidate capability addition.

CANDIDATE DAUGHTER SITES

Candidates:

all parent-cell sites
with:
x >=0.

For structural recruitment only,

use:
the parent-site RBF basis
at:
each candidate center.

The final daughter cells
still receive:
the standard:
H178-H181
deterministic daughter micro-offset

after:
site selection.

This avoids:
selection-order-dependent
candidate coordinates.

The micro-offset
is:
small
relative to:
sigma=.22

and:
is applied identically
after:
every selection rule.

LEARNED GATE

Exact H180 gate:

features:
[1,x,y,x^2,x*y,y^2].

64 A-context
and:
64 B-context
coordinate examples.

No:
functional targets.

L2=.01.

Deterministic IRLS.

The gate is:
fit and frozen
before:
daughter-site recruitment.

EFFECTIVE CANDIDATE DESIGN

For B training inputs:

for candidate site j:

x_j
=
gate(X_B_train)
*
phi_j(X_B_train).

Thus:

site recruitment
optimizes:
the basis functions
that will actually be active
under:
the accepted learned router.

B TRAINING RESIDUAL

Initial residual:

r_0
=
y_B
-
f_A_frozen(X_B).

At recruitment step t:

selected set:
S_t.

Fit:
ridge coefficients
on:
the effective candidate columns
for:
S_t.

alpha:
0.01.

Compute:

r_t
=
r_0
-
X_{S_t} w_t.

OMP-STYLE RECRUITMENT

For every:
unselected candidate j,

score:

Q_j
=
(
x_j^T r_t
)^2
/
(
x_j^T x_j
+
0.01
).

Choose:

maximum Q_j.

Tie:

lower parent-cell index.

Then:

add:
j
to:
S.

Refit:
all selected
effective candidate columns
jointly

and:
update residual.

Repeat
until:
K sites
have been selected.

This rule:

uses:
B training targets

only:
through:
the current:
B training residual.

No:
B validation
or:
B held-out
target
enters:
recruitment.

No:
A target
enters:
recruitment.

FINAL DAUGHTER FIT

After:
K parent sites
are selected:

instantiate:
K standard
micro-offset daughter centers.

Fit:
daughter coefficients

using:
the actual gated
daughter-center design

on:
B training residual.

alpha=.01.

Thus:

OMP recruitment
selects:
the developmental sites;

the final learned capability
uses:
the same daughter-cell
mechanics
as:
H180/H181.

POLICIES

A — H180_LEARNED_RANDOM64

Accepted broad-random
learned-gate comparator.

B — H181_KCOVER_LEARNED64

Accepted target-blind
coverage comparator.

C — OMP_LEARNED16

16 recruited daughter sites
plus:
the learned gate.

D — OMP_LEARNED32

32 sites.

E — OMP_LEARNED64

PRIMARY CANDIDATE.

64 sites.

F — OMP_HARD64

Same:
OMP-selected 64 sites

with:
the hard-gate ceiling.

G — OMP_UNGATED64

Same:
OMP sites

without:
context routing.

Tests:
whether:
function-aware recruitment
alone
can:
avoid:
A interference.

H — GLOBAL_DAUGHTER

Raw-capacity ceiling
and:
interference warning.

PRIMARY METRICS

Per policy:

- A baseline R^2;
- pre-add B R^2;
- post-add A R^2;
- post-add B train / validation / test R^2;
- A R^2 loss;
- normalized A-output drift;
- B gain;
- active-cell count;
- parameter growth;
- gate quality;
- recruitment residual trajectory;
- recruitment score trajectory;
- final B-training residual;
- selected-site pairwise spread;
- daughter nearest-neighbor distance;
- deterministic recruitment compute proxy;
- fit compute proxy;
- total compute proxy;
- hibernation / reactivation error.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
8.

Policy evaluations:
160.

PRIMARY ACCEPTANCE SHAPE

H182 supports:
SPARSE
FUNCTION-SPACE
CAPABILITY RECRUITMENT

if:

1.
A baseline:
median held-out R^2 >=0.90.

2.
OMP_LEARNED64:

median B held-out R^2 >=0.90.

3.
OMP_LEARNED64:

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
Gate quality:

same:
H180/H181 gates.

8.
RELIABILITY VALUE:

OMP_LEARNED64

world fraction:
B>=0.85

must be:

>=90%

AND:

at least:
5 percentage points
above:
the matched-primary
H180_LEARNED_RANDOM64
comparator

unless:
that comparator
also reaches:
>=90%.

9.
FUNCTION-SPACE VALUE:

OMP_LEARNED64

median B held-out R^2

must be:
>=0.03
above:
H181_KCOVER_LEARNED64

with:
no:
>0.01
additional median A loss.

10.
HARD-GATE CEILING:

OMP_HARD64

must:
reach:
>=90%
world-level
B>=0.85.

11.
GENERALIZATION:

OMP_LEARNED64:

median validation-test gap <=0.05;

median train-test gap <=0.10.

12.
ACTIVE STRUCTURE:

64 daughters
<=2%
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

median total compute proxy
<25%
of:
GLOBAL_DAUGHTER.

15.
HIBERNATION / REACTIVATION:

same exact-return
gates
as:
H180/H181.

16.
GLOBAL_DAUGHTER
remains:
raw-capacity ceiling
and:
interference warning.

STRONG SUPPORT

H182 receives:
STRONG support

if:

OMP_LEARNED32

also:

- median B R^2 >=0.90;
- >=90%
  world B>=0.85;
- median A loss <=0.03.

This would add:
a new capability

with:
approximately:
1%
new active cells

plus:
six routing parameters.

MIXED / NEGATIVE CONDITIONS

Treat H182 as:
mixed / negative
if:

- OMP recruitment
  overfits:
  B training targets;

- validation/test B performance
  does not:
  improve:
  over:
  random broad morphology;

- hard-gated OMP64
  still:
  fails:
  90%
  world reliability;

- function-aware site selection
  drives:
  daughter geometry
  into:
  severe A interference
  despite:
  routing;

- OMP64
  requires:
  excessive:
  structural-selection compute
  approaching:
  global-daughter fitting.

NEXT

If H182 succeeds:

proceed directly to:

CLR2-H183 —
SEQUENTIAL CAPABILITY ACCUMULATION.

A
->
add B
->
add C

using:
the accepted:
function-space recruited
and:
context-gated
daughter substrate.

If H182 fails:

the next cognitive question is:
REPRESENTATIONAL REUSE,

not:
another site-selection heuristic.

Test:
whether:
new capability B
can reuse:
existing frozen parent basis

through:
new sparse readout / gating

before:
growing:
new daughter cells.

SANITY WORLD SEEDS

20260923190000...

PRIMARY WORLD SEEDS

20260923100000
through:
20260923100019.

Sanity:
NON-EVIDENCE.

No:
parent task,
B task,
K,
candidate domain,
OMP score,
ridge alpha,
gate,
daughter offset,
sample count,
or:
acceptance gate

may change
after:
the first held-out H182 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_FUNCTION_SPACE_DAUGHTER_BASIS_RECRUITMENT

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — FUNCTION-SPACE DAUGHTER RECRUITMENT HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H182 HELD-OUT PRIMARY EXECUTION.

FINAL H182 SANDBOX HARNESS

File:

h182_omp_recruit_v1.py

SHA-256:

80bbb44c4fff4abfb384df534bfe55f0a8076db2c9c3c4b041642f9f1648a64c.

PARENT MODEL

Reuse:
H180/H181
context-gated
capability-addition
substrate.

No:
task,
gate,
daughter-cell budget,
daughter fit,
or:
active-structure
change.

ONLY SCIENTIFIC CHANGE

Daughter sites
are recruited:

sequentially

from:
B TRAINING FUNCTION
residuals.

Candidate sites:

all parent sites
with:
x>=0.

For selection geometry:

use:
parent-site RBF columns.

After:
selection,

instantiate:
the standard:
micro-offset daughter cells

and:
perform:
the same:
actual daughter fit
as:
H180/H181.

LEARNED GATE

Exact:
H180/H181
six-parameter
context-only router.

The gate is:

fit and frozen

before:
site recruitment.

No:
A or B
functional target

enters:
gate fitting.

EFFECTIVE CANDIDATE COLUMN

x_j =
gate(X_B_train)
*
phi_j(X_B_train).

INITIAL B RESIDUAL

r0 =
y_B
-
f_A_frozen(X_B_train).

OMP RECRUITMENT

At:
each step t,

for:
every unselected
candidate j,

Q_j =
(
x_j^T r_t
)^2
/
(
x_j^T x_j
+
0.01
).

Select:
maximum Q_j.

Tie:
lower parent index.

Then:

jointly ridge-fit:
all selected columns

with:
alpha=.01,

update:
the B training residual,

and:
continue.

B validation
and:
B held-out
targets

never enter:
recruitment.

A functional targets:

never enter:
recruitment.

FINAL FIT

After:
K sites
are recruited,

instantiate:
K standard
daughter centers.

Fit:
the actual
gated daughter design

to:
the same:
B training residual

with:
alpha=.01.

POLICIES

H180_LEARNED_RANDOM64.

H181_KCOVER_LEARNED64.

OMP_LEARNED16.

OMP_LEARNED32.

OMP_LEARNED64.

OMP_HARD64.

OMP_UNGATED64.

GLOBAL_DAUGHTER.

SANITY

Disjoint family:

20260923190000
and:
20260923190001.

2 worlds.

8 policies.

16 evaluations.

Accepted sanity-output SHA-256:

49d860b645ced7f847b9fd607381f00d87879f31a1b9baec7834fda363b1c3de.

Mechanical checks:

- exact 8 policies / world;
- exact:
  16 / 32 / 64
  OMP site counts;
- one shared:
  learned context gate
  per world;
- parent A coefficients:
  frozen;
- no:
  validation target,
  held-out target,
  or:
  A target replay
  enters:
  OMP recruitment;
- final daughter fit:
  uses:
  actual micro-offset
  daughter centers;
- hibernation / reactivation:
  unchanged.

NON-EVIDENCE FUNCTION-SPACE SIGNAL

OMP_LEARNED64
B held-out R^2:

approximately:

0.991
and:
0.998.

OMP_LEARNED32:

approximately:

0.984
and:
0.997.

OMP_LEARNED16:

approximately:

0.839
and:
0.991.

Thus:

sequential:
function-space recruitment

can:
materially outperform:
the prior:
random,
residual-local,
and:
Euclidean-coverage
morphologies

inside:
sanity.

A preservation
under:
learned routing

remains:
strong.

UNGATED OMP64:

learns:
B strongly

but:
again:
materially interferes:
with A.

Thus:

function-space recruitment
does NOT:
remove:
the need for:
context routing.

GENERALIZATION WARNING

One:
sanity world

shows:
a large:
learned-gate
B validation / held-out
difference

despite:
high:
B held-out R^2.

This is:
NON-EVIDENCE.

No:

- gate;
- OMP score;
- ridge alpha;
- K;
- candidate domain;
- final daughter fit;
- sample size;
- threshold;
- acceptance gate

was changed
from:
this warning.

PRIMARY FAMILY

20260923100000..20260923100019.

20 held-out worlds.

8 policies.

160 policy evaluations.

H182 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H182 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
