TITLE: DG-1A-CLR2-H180 — Context-Gated Distributed Capability Addition Audit
DATE: 2026-09-20
STATUS: PREREGISTERED / SYNTHETIC COGNITIVE PRIMARY NOT STARTED
TRACK: DG-1 / DEVELOPMENTAL CAPABILITY ADDITION
BRANCH: dg1a-ar
PARENT: dg1a-clr2-h179-distributed-micropatch-capability-addition-audit.ice

PURPOSE

H179 established:

- 64 distributed daughter cells have substantial capacity for capability B;
- 8-way distribution improves B coverage over one compact colony at the same K;
- broad RANDOM_MULTI8_64 can reach median B R^2 near 0.95;
- but broad ungated growth catastrophically interferes with preserved capability A;
- residual-driven placement protects A but leaves B below the required capability threshold.

Therefore:

the missing variable is not obviously:
raw cell count.

It is:
CAPABILITY ROUTING / CONTEXTUAL ACTIVATION.

H180 asks:

CAN THE SAME
64 DAUGHTER CELLS

learn a broad new capability B

while preserving A

if:
their functional contribution
is context-gated

rather than:
always active?

BOUNDARY

Synthetic computational research only.

No wetware.
No biological claim.
No production model modification.
No canonical scientific execution.
No STAB-18-R1 execution.

PARENT MODEL

Reuse H179 / H178 exactly:

g=.25.

N=3209 frozen parent cells.

Same:
A/B domains,
smooth nonlinear teachers,
A context-silence training,
parent ridge,
B residual target,
daughter basis width,
daughter micro-offset,
64-cell MULTI8 morphology,
B-only daughter coefficient fitting,
hibernation/reactivation.

Parent A coefficients:
remain frozen.

No:
A task-output replay
is allowed
inside:
the primary learned-gate candidate.

CONTEXT IDENTITY

A-context and B-context are:
input contexts,
not capability target values.

A-context samples:
drawn from the same A-domain input distribution.

B-context samples:
drawn from the same B-domain input distribution.

A context label means:
"this input belongs to A context."

B context label means:
"this input belongs to B context."

No:
teacher A value,
teacher B value,
held-out output,
or validation output

enters:
gate fitting.

The gate therefore learns:
WHEN
the daughter capability should be active,

not:
WHAT
the daughter capability should output.

GATE FEATURE MAP

For input:
(x,y),

gate features:

[1,
 x,
 y,
 x^2,
 x*y,
 y^2].

Standardize:
non-bias features

using:
the gate-training set only.

LEARNED CONTEXT GATE

Training set:

64 A-context inputs
with:
gate target 0.

64 B-context inputs
with:
gate target 1.

These input coordinates are:
disjoint from:

- A held-out test;
- B training targets;
- B validation;
- B held-out test.

Fit:
L2-regularized logistic regression.

Gate L2:
0.01.

Optimization:
deterministic Newton / IRLS
to:
convergence
or:
100 iterations.

Soft gate:

g(x)
=
sigmoid(
theta^T z(x)
).

No:
thresholding
inside:
the primary candidate.

DAUGHTER OUTPUT

Ungated:

f_D(x)
=
Phi_D(x) w_D.

Gated:

f_D_gate(x)
=
g(x)
*
Phi_D(x) w_D.

Integrated phenotype:

f_total(x)
=
f_A_frozen(x)
+
f_D_gate(x).

DAUGHTER FIT UNDER GATING

The gate is:
frozen
before:
fitting daughter coefficients.

For B training inputs:

design matrix:

diag(
g(X_B_train)
)
*
Phi_D(X_B_train).

Fit:
daughter coefficients

to:
B residual:

y_B
-
f_A_frozen(X_B_train).

Ridge alpha:

same H178/H179 daughter ridge:
0.01.

No:
A functional targets
are replayed
during:
daughter fitting.

HARD CONTEXT GATE CEILING

Architectural ceiling only.

g_hard(x)
=
0
for:
x <= -0.05.

g_hard(x)
=
1
for:
x >= +0.05.

Linear interpolation:
between:
-0.05
and:
+0.05.

This uses:
the known experimental context boundary.

It is:
NOT:
the candidate architecture.

It answers:

if:
routing were perfect,

is:
the existing:
64-cell distributed daughter morphology

sufficient
for:
B capability
without:
A interference?

POLICIES

A — UNGATED_MULTI8_64

Exact H179:
residual-driven
8-way distributed
64-cell daughter population.

No gate.

B — LEARNED_GATE_MULTI8_64

PRIMARY CANDIDATE.

Same:
error-driven MULTI8_64
daughter coordinates.

Shared:
learned soft context gate.

C — HARD_GATE_MULTI8_64

Routing ceiling.

Same:
MULTI8_64 daughters.

Hard experimental context gate.

D — LEARNED_GATE_RANDOM8_64

Same:
random distributed
64-cell morphology
as:
H179 RANDOM_MULTI8_64.

Apply:
the same learned gate.

This tests:

whether:
routing rescues:
the high-B-capacity
broad random morphology.

E — HARD_GATE_RANDOM8_64

Hard-gate routing ceiling
for:
the random morphology.

F — LEARNED_GATE_MULTI8_32

32-cell
8-way distributed
daughter population

with:
the learned context gate.

Tests:
whether routing
also lowers:
the active-structure requirement.

G — UNGATED_MULTI8_32

H179 ungated reference.

H — CONN256

H178/H179:
large ungated connected reference.

I — GLOBAL_DAUGHTER

High-capacity ungated ceiling,
retained:
as interference warning.

GATE METRICS

Report:

- gate context classification accuracy;
- gate B-context mean activation;
- gate A-context mean activation;
- A-context 95th percentile activation;
- B-context 5th percentile activation;
- gate entropy;
- gate parameter count;
- gate fit compute proxy.

CAPABILITY METRICS

Report:

- A baseline R^2;
- pre-add B R^2;
- post-add A R^2;
- post-add B train / validation / test R^2;
- A R^2 loss;
- normalized A-output drift;
- B gain;
- daughter active-cell count;
- active-cell growth fraction;
- gate parameter count;
- total permanent parameter growth;
- deterministic compute proxy;
- hibernation / reactivation error.

PRIMARY FACTORIAL

Held-out worlds:
20.

Policies:
9.

Policy evaluations:
180.

PRIMARY ACCEPTANCE SHAPE

H180 supports:
CONTEXT-GATED
BOUNDED CAPABILITY ADDITION

if:

1.
A baseline:
median held-out R^2 >=0.90.

2.
LEARNED_GATE_MULTI8_64:

median B held-out R^2 >=0.90.

3.
LEARNED_GATE_MULTI8_64:

>=90%
of worlds
finish:
B R^2 >=0.85.

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
The learned gate:

median context classification accuracy >=0.95.

8.
The learned gate:

median A-context activation <=0.10

and:

median B-context activation >=0.90.

9.
ROUTING VALUE:

LEARNED_GATE_MULTI8_64

improves:
median B R^2
or:
joint B/A success

relative to:
UNGATED_MULTI8_64

without:
>0.01
additional median A loss.

Because:
ungated residual placement
already protects A,

the expected primary routing gain
may appear mainly as:
greater usable B coverage.

10.
RANDOM-MORPHOLOGY ROUTING DIAGNOSTIC:

LEARNED_GATE_RANDOM8_64

must reduce:
median A loss

by:
>=0.10

relative to:
UNGATED RANDOM_MULTI8_64
from H179

or:
bring:
median A loss
below:
0.05.

This tests:
whether:
the gate directly controls:
the H179 interference mode.

11.
GENERALIZATION:

qualifying learned-gate policy:

validation-test B R^2 gap <=0.05

and:
train-test gap <=0.10.

12.
ACTIVE STRUCTURE:

64-cell candidate
adds:
<=2%
new active cells.

13.
TOTAL PERMANENT PARAMETER GROWTH:

daughter coefficients
+
gate parameters

must:
remain:
<=2.25%
of:
the parent coefficient count.

14.
COMPUTE:

qualifying learned-gate policy
median compute proxy

<25%
of:
GLOBAL_DAUGHTER.

15.
HIBERNATION / REACTIVATION:

same exact-return
mechanical gates
as:
H178/H179.

16.
HARD_GATE_MULTI8_64
and:
HARD_GATE_RANDOM8_64

define:
routing ceilings.

If:
hard gating passes
but:
learned gating fails,

classify:
routing as:
the correct architecture

but:
the learned gate
as:
insufficient.

17.
GLOBAL_DAUGHTER
remains:
the raw-capacity ceiling
and:
interference warning.

STRONG SUPPORT

H180 receives:
STRONG support

if:

all primary learned-gate gates pass

AND:

LEARNED_GATE_MULTI8_32

also achieves:

median B R^2 >=0.90

with:
median A loss <=0.03.

That would mean:

approximately:
1%
new active cells

plus:
a tiny context gate

can:
add:
a new learned capability.

MIXED / NEGATIVE CONDITIONS

Treat H180 as:
mixed / negative
if:

- hard gating rescues:
  the morphology
  but:
  learned gating does not;

- learned gate
  needs:
  task outputs
  rather than:
  context identity;

- learned gating preserves A
  but:
  suppresses B too strongly;

- random distributed growth
  remains:
  catastrophically interfering
  after:
  gating;

- K=64
  still:
  cannot:
  reach:
  reliable B competence
  even:
  under:
  hard routing;

- gate parameters
  become:
  a hidden large
  active architecture.

NEXT

If H180 succeeds:

proceed immediately to:

CLR2-H181 —
SEQUENTIAL CAPABILITY ACCUMULATION.

Learn:
A.

Add:
B
with:
the accepted
bounded routed growth.

Then add:
C

without:
retraining A or B.

Measure:

total capability gain
versus:

- permanent active cells;
- gate parameters;
- memory;
- compute;
- interference;
- hibernation / reactivation;
- developmental reuse.

If:
hard gate passes
but:
learned gate fails:

next:
learn / develop:
the routing mechanism

rather than:
increase:
daughter count.

SANITY WORLD SEEDS

20260922990000...

PRIMARY WORLD SEEDS

20260922900000
through:
20260922900019.

Sanity:
NON-EVIDENCE.

No:
parent task,
B task,
daughter morphology,
K,
gate feature map,
gate sample count,
gate L2,
hard-gate boundary,
daughter ridge,
or:
acceptance gate

may change
after:
the first held-out H180 world.

PROVENANCE

evidence_class_target =
SYNTHETIC_MEASURED_CONTEXT_GATED_DEVELOPMENTAL_CAPABILITY_ADDITION

canonical_scientific_execution = false.
canonical_r1_execution_spent = false.
stab18_r1_touched = false.
