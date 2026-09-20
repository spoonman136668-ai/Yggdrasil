TITLE: DG-1A-CLR2-H178 — Bounded Developmental Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION
BRANCH: dg1a-ar
PARENT: dg1a-clr1-h177-local-function-coverage-query-design-audit.ice

PURPOSE

H175 demonstrated:
fine-scale learned cognitive micro-patching.

H176-H177 showed:
perfect reconstruction of the lesion-local learned function
is underdetermined by a tiny observation set,
even when global task behavior is restored.

The program now advances to the next cognitive inflection:

CAPABILITY ADDITION.

Question:

CAN A DEVELOPMENTAL CELLULAR PHENOTYPE

learn capability A,

freeze / preserve A,

grow a bounded new connected cellular patch
for previously unseen capability B,

learn B using only local new-patch plasticity,

and integrate A+B

without:
global retraining
or:
material degradation of A?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

CELLULAR BODY

Fine cognitive scale only:

g = 0.25.

Unit-disk parent body:

R = 32.

N approximately 3209
existing active parent cells.

Parent basis:

same Gaussian RBF family
as CLR1.

sigma = 0.22.

CAPABILITY DOMAINS

A and B are:
different learned nonlinear functions
on:
different but nearby input domains.

This prevents:
logical target contradiction
while still permitting:
RBF-tail interference.

Capability A domain:

left unit-disk lobe.

Sampling center:
(-0.45, 0).

sd:
0.25.

Reject:
outside unit disk
or:
x > -0.05.

Capability B domain:

right unit-disk lobe.

Sampling center:
(+0.45, 0).

sd:
0.25.

Reject:
outside unit disk
or:
x < +0.05.

No:
task-specific cell identity
is preassigned.

TEACHERS

A and B:

independent learned nonlinear teachers.

Use:
the accepted H176/H177
smooth-plus-small-high-frequency
teacher family.

The student does NOT:
receive teacher parameters.

It receives:
training input / target examples only.

STAGE 1 — LEARN A

Train:
the existing parent-cell phenotype

on:
capability A only.

Samples:

768 train.

256 validation.

512 held-out test.

Ridge:

alpha =
0.01 * g^2
=
0.000625.

All:
existing parent coefficients

are:
then frozen

for:
the remainder
of:
the candidate capability-addition policies.

Record:

A baseline R^2,
A validation MSE,
parent coefficient RMS,
training compute proxy.

STAGE 2 — PRESENT UNSEEN B

Generate:
capability B data

from:
the independent B teacher.

Samples:

768 train.

256 validation.

512 held-out test.

Before:
any growth,

evaluate:

the frozen A phenotype
on:
B.

This is:
PRE-ADD B competence.

No:
A coefficient
may:
change
inside:
the bounded-growth candidates.

DAUGHTER-CELL GROWTH

A new daughter cell:

inherits:
the spatial center
of:
one selected parent cell

plus:
a deterministic
micro-offset

of:
0.25
parent-grid spacing

in:
a direction
derived from:
world seed
and:
daughter index.

Reject / reflect
the offset
to:
remain:
inside unit disk.

Daughter basis width:

same sigma=0.22.

Daughter cells:

are:
NEW
active computational cells.

They have:
their own
scalar output coefficient.

Parent coefficients:
remain frozen.

The integrated phenotype output is:

f_total(x)
=
f_A_frozen(x)
+
f_daughter(x).

Thus:

B is learned
as:
a residual developmental addition

on top of:
the preserved A phenotype.

Because:
daughter cells also emit:
on A-domain inputs,

A preservation is:
NOT:
hard-coded.

Collateral interference
must be:
measured.

ERROR-DRIVEN CONNECTED PATCH

On:
B training data,

compute:

residual:

r_B
=
y_B
-
f_A_frozen(X_B).

For:
each parent cell j,

score:

C_j
=
abs(
mean(
phi_j(X_B) * r_B
)
).

Patch seed:

argmax C_j

subject to:
parent center x >=0.

Grow:
one Moore-connected
parent patch

by repeatedly adding:
the boundary parent cell
with:
maximum C_j.

The selected parent cells
define:
daughter growth sites.

No:
B validation
or:
B held-out test
target

enters:
patch selection.

GROWTH LEVELS

K:

8,
16,
32,
64,
128,
256.

All:
well below:
10%
of:
the parent-cell count.

For:
each K,

grow:
K daughter cells
on:
the first K
growth sites.

DAUGHTER TRAINING

Parent A coefficients:

frozen.

Fit:
daughter coefficients

to:
B training residual

using:

ridge alpha:
0.01.

Only:
daughter coefficients
are:
plastic.

No:
A training example
is:
replayed
inside:
the primary candidate.

This is:
B-ONLY
developmental capability addition.

POLICIES / CONTROLS

A — NO-GROW

Frozen A phenotype only.

No daughter cells.

B — GROW8.

C — GROW16.

D — GROW32.

E — GROW64.

F — GROW128.

G — GROW256.

H — RANDOM64

Grow:
64
connected daughter cells

from:
a deterministic random
right-half seed

with:
random connected frontier growth.

Train:
the same way.

This tests:
whether:
error-driven growth location matters.

I — GLOBAL-DAUGHTER

Control ceiling.

Grow:
one daughter cell
at:
EVERY parent-cell site.

K=N.

Fit:
all daughter coefficients
to:
B residual.

Parent A coefficients:
remain frozen.

This is:
NOT:
a candidate efficient architecture.

It is:
a high-capacity
addition ceiling.

No:
whole-parent retraining
is performed.

CAPABILITY METRICS

After:
B addition,

evaluate:

A held-out R^2.

B held-out R^2.

A validation MSE.

B validation MSE.

A output drift:

MSE(
post-add A outputs,
pre-add A outputs
)
/
Var(
pre-add A outputs
).

B error reduction
relative to:
NO-GROW.

GENERALIZATION

B train,
validation,
and:
held-out test

remain:
disjoint.

Report:

train R^2,
validation R^2,
held-out R^2.

A test set:

never enters:
B patch selection
or:
daughter fitting.

HIBERNATION / REACTIVATION

After:
training the daughter patch:

HIBERNATE:

set:
all daughter outputs
to zero

without:
changing:
daughter coefficients.

Verify:

A output
returns:
to:
the frozen A phenotype.

Then:

REACTIVATE:

restore:
the stored daughter coefficients.

Verify:

B held-out performance
returns:
to:
the integrated value

without:
retraining.

Report:

A hibernation recovery error.

B reactivation recovery error.

RESOURCE METRICS

For each policy report:

- new active cells K;
- active-cell growth fraction K/N;
- daughter patch macro radius;
- daughter patch macro area proxy;
- B training sample count;
- daughter coefficient count;
- patch-selection operations;
- ridge solve dimension;
- deterministic compute proxy;
- B R^2 gained per:
  new active cell;
- B R^2 gained per:
  compute proxy.

PRIMARY FACTORIAL

Held-out worlds:

20.

Policies:

9.

Policy evaluations:

180.

No repeated lesion cycle
is part of H178.

This is:
capability-addition proof
rather than:
repair stress.

PRIMARY ACCEPTANCE SHAPE

H178 supports:
BOUNDED DEVELOPMENTAL CAPABILITY ADDITION

if:

1.
A baseline learning:

median A held-out R^2
>=0.90.

2.
World-level A competence:

>=90%
of worlds
A R^2 >=0.85.

3.
There exists:
a bounded growth level

K <=64

with:

median B held-out R^2
>=0.90.

4.
The same K<=64:

>=90%
of worlds
finish:
B held-out R^2 >=0.85.

5.
A preservation:

for:
the qualifying K,

median A held-out R^2 loss
<=0.03.

6.
World-level A preservation:

>=90%
of worlds
lose:
<=0.05
A R^2

under:
the qualifying K.

7.
A output drift:

median normalized
A-output drift
<=0.05

for:
the qualifying K.

8.
Error-driven growth value:

the qualifying
error-driven K
has:
median B held-out R^2

at least:
0.10
above:
RANDOM64

OR:

if:
RANDOM64
already achieves:
B R^2 >=0.90,

the error-driven policy
must use:
strictly fewer
new active cells

to reach:
the same:
0.90 threshold.

9.
Generalization:

for:
the qualifying K,

median B validation-to-test
R^2 gap
<=0.05

and:

median B train-to-test
R^2 gap
<=0.10.

10.
Active structure:

qualifying K
adds:
<=2%
new active cells

relative to:
the original N.

K=64:

approximately:
1.99%.

11.
Compute:

qualifying bounded-growth
median compute proxy

is:
<25%
of:
GLOBAL-DAUGHTER.

12.
HIBERNATION:

after:
daughter deactivation,

A outputs return
to:
the frozen A phenotype

with:
normalized error
<=1e-10.

13.
REACTIVATION:

restoring:
daughter coefficients

returns:
B held-out predictions

with:
normalized error
<=1e-10

relative to:
pre-hibernation
integrated B predictions.

14.
GLOBAL-DAUGHTER
remains:
the high-capacity
B-addition ceiling.

STRONG SUPPORT

H178 receives:
STRONG support

if:

all primary gates pass

AND:

some:
K<=32

achieves:

median B held-out R^2
>=0.90

with:
median A R^2 loss
<=0.02.

NORTH-STAR TELEMETRY

Report:

capability gain:

Delta_B =
B_R2_post
-
B_R2_pre.

Permanent active-structure gain:

K / N.

Compute gain:

bounded-growth compute
/
GLOBAL-DAUGHTER compute.

This does NOT:
yet establish:
sublinear structure growth
over:
many capabilities.

It is:
the first:
developmental addition
measurement.

MIXED / NEGATIVE CONDITIONS

Treat H178 as:
mixed / negative
if:

- B requires:
  >64 daughter cells
  to generalize;

- B learning materially degrades:
  A;

- error-driven connected growth
  does not outperform:
  random connected growth;

- training B overfits:
  the B training examples;

- hibernation / reactivation
  requires:
  retraining;

- bounded patch compute
  approaches:
  the global-daughter control.

NEXT

If H178 succeeds:

proceed to:
CLR2-H179
SEQUENTIAL CAPABILITY ACCUMULATION.

Add:
A,
then B,
then C

with:
bounded new growth
for:
each capability.

Measure:

total capability
versus:

- permanently active cells;
- memory;
- compute;
- cross-capability interference;
- hibernation / reactivation;
- reuse of:
  previously learned
  developmental structure.

SANITY WORLD SEEDS

20260922790000...

PRIMARY WORLD SEEDS

20260922700000
through:
20260922700019.

Sanity:
NON-EVIDENCE.

No:
domain definition,
teacher,
student ridge,
growth-site score,
connected-growth rule,
daughter offset,
growth levels,
daughter ridge,
sample count,
or:
acceptance gate

may change
after:
the first held-out H178 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_DEVELOPMENTAL_CAPABILITY_ADDITION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
