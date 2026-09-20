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


PRE-PRIMARY IMPLEMENTATION FREEZE 01 — BOUNDED CAPABILITY-ADDITION HARNESS

DATE:
2026-09-20.

STATUS:
FROZEN BEFORE H178 HELD-OUT PRIMARY EXECUTION.

FINAL H178 SANDBOX HARNESS

File:

h178_cap_add_v2.py

SHA-256:

e7f0c006a1e6b340373e448667dcc8dfa5d3b53a02554d8e3fe48572aa4394d2.

PRE-PRIMARY CONTEXT-SEPARATION CORRECTION

The first H178 sanity harness
trained:
capability A

only on:
A-domain examples.

Because:
the same scalar phenotype
was then evaluated
on:
the previously unseen B domain,

the frozen A model
extrapolated:
large arbitrary outputs

into:
the B context.

Representative:
pre-add B R^2

was:
hundreds of points
below zero.

That made:
the candidate daughter patch

spend:
most of:
its capacity

canceling:
out-of-domain
A extrapolation

rather than:
learning:
new capability B.

This was:
a task-routing
confound,

not:
a developmental
capability-addition result.

No:
H178 held-out primary world
was executed
under:
that harness.

CORRECTION

Capability A
is now trained with:

768:
A-domain
functional examples

plus:

256:
B-domain
SILENCE examples

with:
target output:
0.

Interpretation:

the developmental phenotype
learns:

A is active
in:
its own context

and:
silent
in:
the reserved
B context.

This is:
a context-routing constraint,

not:
B capability information.

The silence examples:

contain:
no B teacher output.

They do NOT:
teach:
capability B.

They only prevent:
arbitrary
A extrapolation
into:
an unseen
capability context.

TEACHER CALIBRATION

H178 uses:
the smooth learned teacher
component:

- random tanh field;
- low-frequency sinusoid.

The small:
H176/H177
high-frequency residual

is omitted
for:
the first
capability-addition proof.

This keeps:
the experiment focused
on:

bounded developmental
capability growth

rather than:
high-frequency
function reconstruction.

No:
teacher parameter
was tuned
from:
held-out primary.

PARENT BODY

g=.25.

N=3209.

Parent:
Gaussian RBF cells.

Parent A ridge:

alpha=.000625.

DAUGHTER GROWTH

Exact:
preregistered
error-driven
connected right-half
growth path.

Growth levels:

8,
16,
32,
64,
128,
256.

Daughter micro-offset:

0.25
parent-grid spacing.

Daughter basis width:

same:
sigma=.22.

Parent A coefficients:

frozen.

Daughter coefficients:

fit:
B training residual only.

No:
A replay
inside:
candidate addition.

CONTROLS

NO-GROW.

RANDOM64.

GLOBAL-DAUGHTER.

GLOBAL-DAUGHTER:

adds:
one daughter
at:
every parent site

and:
is:
a high-capacity
addition ceiling,

not:
a candidate architecture.

SANITY

Disjoint family:

20260922790000
and:
20260922790001.

2 learned worlds.

9 policies.

18 policy evaluations.

Accepted sanity-output SHA-256:

71f76b3a795885af30c4259795c1234d374a7eb3a41a70a446a2e819943ab3c9.

Mechanical checks:

- exact 9 policies / world;
- parent A coefficients:
  frozen
  after stage-1 learning;
- daughter training:
  B residual only;
- no:
  A held-out,
  B validation,
  or:
  B held-out
  targets
  enter:
  growth-site selection;
- hibernation:
  daughter contribution
  removable
  without:
  coefficient change;
- reactivation:
  exact daughter state
  restored
  without:
  retraining.

NON-EVIDENCE SIGNAL

A baseline:

approximately:
0.999
held-out R^2
in:
both sanity worlds.

Pre-add B:

approximately:
-0.45
to:
-0.96.

Thus:

B is:
genuinely absent
before:
addition.

Small connected patches:

preserve:
A
more strongly

but:
underfit:
B.

Representative:
GROW32

B R^2:

approximately:
0.50..0.58.

GROW64:

approximately:
0.74..0.76.

Larger patches:

GROW256

B R^2:

approximately:
0.92..0.94.

A loss:

varies:
by world

from:
approximately:
0.01
to:
0.06.

Therefore:

the sanity result
shows:
a real:
capability / interference
growth trade-off.

RANDOM64:

is:
high-variance
and:
sometimes:
less interfering

but:
less consistently
B-capable.

GLOBAL-DAUGHTER:

learns:
B
near:
the ceiling

but:
can:
severely disturb:
A,

confirming:

capacity alone
does NOT:
guarantee
non-interfering
integration.

These values are:

NON-EVIDENCE.

No:
growth level,
growth-site score,
daughter ridge,
silence count,
sample size,
or:
acceptance gate

was changed
from:
these outcomes.

PRIMARY FAMILY

20260922700000..20260922700019.

20 held-out worlds.

9 policies.

180 policy evaluations.

H178 ACCEPTED PRIMARY STATUS

NOT STARTED.

No execution-semantic change
is permitted
after:
the first held-out H178 world.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.


FINAL ACCEPTED PRIMARY CLOSURE — BOUNDED DEVELOPMENTAL CAPABILITY ADDITION

DATE:
2026-09-20.

STATUS:
ACCEPTED PRIMARY COMPLETE / NEGATIVE FOR SINGLE CONNECTED <=2% GROWTH / POSITIVE CAPACITY-INTERFERENCE BOUNDARY.

FINAL H178 HARNESS SHA-256

e7f0c006a1e6b340373e448667dcc8dfa5d3b53a02554d8e3fe48572aa4394d2.

ACCEPTED PRIMARY MATRIX SHA-256

c93f67fc4f441e1aa88ee03dfebb157027345f90e4be6674ee3e20014b8c2323.

ACCEPTED PRIMARY FAMILY

20260922700000..20260922700019.

PRIMARY MATRIX

20 held-out capability-addition worlds.

9 policies.

180 policy evaluations.

Validation:

- exact 20 primary seeds;
- exact 9 policies / world;
- no missing evaluations;
- no post-primary growth tuning.

CAPABILITY A BASELINE

Median held-out A R^2:

approximately:
0.99815.

100%
of:
worlds

finish:
stage-1 A learning
above:
R^2 0.85.

PASS.

CAPABILITY B IS ABSENT PRE-ADD

Median:
pre-add B R^2

approximately:
-1.81.

Thus:

B is:
not:
already present

before:
developmental addition.

BOUNDED CONNECTED GROWTH

Median B held-out R^2:

GROW8:
approximately 0.417.

GROW16:
0.462.

GROW32:
0.523.

GROW64:
0.644.

GROW128:
0.827.

GROW256:
0.917.

The first:
median B R^2 >=0.90

appears only at:
GROW256.

That adds:

approximately:
7.98%
new active cells.

Frozen target:

some:
K<=64

with:
median B R^2 >=0.90.

FAIL.

WORLD-LEVEL B COMPETENCE

GROW64:

10%
of worlds
reach:
B R^2 >=0.85.

GROW128:

40%.

GROW256:

95%.

Thus:

the capability threshold
is:
not:
a median-only artifact.

A PRESERVATION

Median A R^2 loss:

GROW8:
approximately 0.0025.

GROW16:
0.0101.

GROW32:
0.0083.

GROW64:
0.0086.

GROW128:
0.0159.

GROW256:
0.0521.

Small patches:

preserve:
A

but:
underfit:
B.

Large patch:

learns:
B

but:
crosses:
the frozen
median A-loss
limit
of:
0.03.

This establishes:

a real:
CAPACITY / INTERFERENCE
trade-off.

A OUTPUT DRIFT

Median normalized
A-output drift:

GROW64:
approximately 0.0111.

GROW128:
0.0165.

GROW256:
0.0497.

The interference
grows:
with:
new daughter capacity.

RANDOM64 CONTROL

Median B R^2:

approximately 0.282.

Median A loss:

approximately 0.039.

Error-driven GROW64:

B:
approximately 0.644.

A loss:
approximately 0.0086.

Thus:

error-driven
growth placement

is:
materially better

than:
random connected growth.

PASS:
mechanism value.

GLOBAL-DAUGHTER CONTROL

B R^2:

approximately 0.9992.

But:

median A R^2:

approximately:
-11.39.

Global daughter capacity:

learns:
B

while:
catastrophically
interfering:
with A.

Therefore:

CAPACITY ALONE

does NOT:
solve:
capability integration.

GENERALIZATION

For:
GROW256,

median:

B validation / test
R^2 gap:

approximately 0.023.

B train / test gap:

approximately 0.016.

Thus:

the B-capable
large patch

does:
generalize.

Its failure is:

A interference
and:
active-structure size,

not:
B overfitting.

RESOURCE COST

Median compute ratio
to:
GLOBAL-DAUGHTER:

GROW64:
approximately 0.0028.

GROW128:
approximately 0.0077.

GROW256:
approximately 0.0286.

Thus:

bounded local growth

is:
orders of magnitude
cheaper

than:
the global-daughter
capacity ceiling.

HIBERNATION / REACTIVATION

All:
daughter policies

return:
exactly
to:
the frozen A phenotype

when:
daughter outputs
are hibernated.

Reactivation:

restores:
the integrated
B predictions

without:
retraining.

PASS:
mechanically exact.

PRIMARY GATE REVIEW

PASS:

1.
A baseline learning.

2.
World-level A competence.

8.
Error-driven growth
materially outperforms:
random connected growth.

9.
B generalization
for:
the B-capable
large patch.

11.
Bounded-growth compute
well below:
GLOBAL-DAUGHTER.

12.
Hibernation.

13.
Reactivation.

14.
GLOBAL-DAUGHTER
is:
the B-capacity ceiling.

FAIL:

3.
No:
K<=64
reaches:
median B R^2 >=0.90.

4.
No:
K<=64
has:
>=90%
world-level B R^2 >=0.85.

5-7.
The only:
median B>=0.90
connected patch
is:
GROW256,

which:
exceeds:
the A-preservation
and:
A-drift
limits.

10.
The B-capable:
GROW256

adds:
approximately 8%
new active cells,

not:
<=2%.

STRONG SUPPORT:

FAIL.

FINAL INTERPRETATION

H178 is:

NEGATIVE

for:

ONE
BOUNDED
CONNECTED
<=2%-OF-BODY
CAPABILITY PATCH.

But:

the failure is:
highly informative.

A broad new capability
is:
not naturally represented
by:
one tiny
spatially compact
daughter colony.

The B-capacity curve
improves steadily
as:
the connected patch expands.

At the same time:

A interference
also rises.

This suggests:

CAPABILITY ADDITION
SHOULD NOT:
BE MODELED AS:

ONE BIGGER
COGNITIVE PATCH.

The prior repair research
already showed:

multiple:
small,
distributed
micro-patches

can:
gain:
parallel coverage
without:
one large wound.

The capability-addition
analogue is:

DISTRIBUTED
DEVELOPMENTAL GROWTH.

NEXT:

CLR2-H179 —
DISTRIBUTED
MICRO-PATCH
CAPABILITY ADDITION.

Keep:
the SAME
total new-cell budget.

Compare:

- one connected patch;
- 4 distributed
  connected micro-patches;
- 8 distributed
  connected micro-patches;

selected:
from:
B residual geometry.

Primary question:

can:
distributed
64-cell growth

achieve:
the B coverage
of:
a much larger
single patch

while:

preserving:
A
and:
retaining:
the <=2%
active-structure
budget?

If:
distributed growth succeeds,

proceed to:
sequential:
A -> B -> C
capability accumulation.

H178 DOES NOT AUTHORIZE

- production use;
- live model modification;
- biological claims;
- whole-model retraining
  as:
  the candidate architecture;
- canonical scientific claims;
- STAB-18-R1 execution.

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
