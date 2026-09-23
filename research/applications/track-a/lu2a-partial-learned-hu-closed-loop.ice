TITLE: LU-2A — PARTIAL LEARNED CLOSED-LOOP H/U SUBSTITUTION
DATE: 2026-09-23
STATUS: PREREGISTERED / NO CLOSED-LOOP PRIMARY EXECUTION
TRACK: DG-1 / LEARNED-UPDATER TRANSITION

PURPOSE

Test whether the two transition families
that repeatedly satisfy frozen imitation bars

H RELEASE

and

U RECRUITMENT

can participate causally in the developmental organism
under fresh closed-loop Task-1 trajectories

while retaining the exact trusted V0.2
C/S STAY-DEFECT mechanism.

This is the first learned-updater closed-loop experiment.

It is not a promotion.

It does not replace the unresolved commitment law.

PARENTS

Developmental Substrate V0.2:

e2d8b780a0e09ef5ca52a179cf8240ae70b0c4d2

Independent NO_POOL confirmation:

f77fa375e484859628081f67c54c734cf7eb41d5

Executable LU0DF1 parent:

f23888e37fce4b19a65403dafe27f8a8848b8600

Task-1F LOCAL_HEDGE parent lineage:

1b05bc066314138a0eae05c02c31ba8b84f5f063

LU-1E frozen implementation:

f459273c897a7bd889b6de2ec2d9720374215327

LU-1E duplicate training gate:

2ce6a39af7b69211efd78d6cd5f2e884bc247495

LU-1E closure:

6681d1abdbfc30a3d8e8171fa5ec6b006426d25f

LU-1E residual audit:

3daa014b67c0b67920ac77be2a15154fc759ea8e

FROZEN LEARNED MODEL

Architecture:

LU-1E STATE_CONDITIONED_EQUIVARIANT_RELATIONAL_V1.

Trainable parameters:

13694.

Canonical weight SHA256:

b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023

The LU-2A implementation must refuse execution
if the loaded learned-weight bytes do not match this SHA exactly.

No retraining is permitted inside LU-2A.

No online adaptation.

No optimizer.

No gradient step.

No weight mutation.

SCIENTIFIC QUESTION

Can a partially learned developmental cell
take over the already-qualified H and U transition families
without materially degrading
the validated V0.2 Task-1 functional envelope?

ARMS

Exactly two scientific arms.

ARM A:

TEACHER_V02

Exact executable V0.2 semantics.

This is the LU0DF1 NO_POOL organism
with all inherited Task-1F / V0.2 mechanisms unchanged.

ARM B:

HYBRID_HU

Identical to TEACHER_V02 except:

for a focal H cell,

use the frozen LU-1E model's H RELEASE probability;

for a focal U cell,

use the frozen LU-1E model's
[C,S,H,U] recruitment distribution.

For focal C or S:

use the exact V0.2 C/S STAY-DEFECT probability.

The learned model must not control
committed-cell stay / defect in LU-2A.

REFRACTORY / HARD LIFECYCLE

FC / FS and all hard lifecycle semantics
remain exact V0.2.

No learned model output may alter them.

OBSERVATION BOUNDARY

Learned H/U inference receives exactly OBS-V1.

No global information.

No phase id.

No request id.

No task id.

No absolute position.

No future request.

No future lesion.

No future anchor.

No global C/S count.

No teacher-derived quantity.

No:

mode;

challenge flag;

pressure;

opposition;

own aligned B;

qraw;

qecho;

qeff;

support margin;

teacher probability;

teacher class.

FOCAL-SIDE CANONICALIZATION

For H and U:

identity.

Therefore LU-2A H/U inference
does not require a committed-cell mirror transform.

The model must still use
the exact frozen LU-1E forward path.

V0.2 MECHANISMS PRESERVED

Exactly preserve:

64-cell ring;

D2;

LOCAL_HEDGE;

ECHO_PHASE;

NO_POOL recruitment semantics;

G5_FULL OFF;

request-bound task handoff;

neutral sensing;

Task-1 scheduler;

request expiry;

phase schedule;

demand reversal;

anchor relocation;

distributed lesion;

corruption / verification / repair semantics;

common-random discipline;

and all safety/integrity probes.

No topology change.

No resource-budget change.

No scheduler change.

No task-interface change.

NO NEW RNG

LU-1E inference is deterministic.

HYBRID_HU must consume
exactly the same transition random variates
as TEACHER_V02.

Inference may not introduce an RNG draw.

COMMON RANDOMNESS

For each paired world:

same manifest;

same arrivals;

same programs;

same corruption schedule;

same lesion;

same anchors;

same initial state;

same base RNG identity.

Transition decisions use
the same pre-bound uniform variates
for both arms.

Only the relevant H/U probability law differs.

IMPLEMENTATION FREEZE

Implement as:

LU2AF1.

Before LU2AF1 freeze,
run a mechanical gate only.

No fresh scientific primary worlds
may be derived before LU2AF1 exists.

MECHANICAL GATE

Before LU2AF1 prove:

1.
exact V0.2 / LU0DF1 parent source identity;

2.
exact LU-1E source identity;

3.
canonical weight SHA exactly
b1bc60b16ad9262cf1cb3e661084f55fd87ef809be0a46d7692e58e628c20023;

4.
TEACHER_V02 reproduces parent NO_POOL behavior
byte-identically on the mechanical fixture;

5.
HYBRID_HU and TEACHER_V02 are identical
for every focal C/S transition probability
on the mechanical fixture;

6.
HYBRID_HU and TEACHER_V02 are identical
for every FC/FS hard lifecycle operation;

7.
learned model is queried only for focal H/U;

8.
H output mapping is exactly inherited LU-1E H-release mapping;

9.
U output mapping is exactly inherited LU-1E [C,S,H,U] mapping;

10.
OBS-V1 width / semantics unchanged;

11.
no forbidden global/future/position/teacher-derived feature;

12.
no model RNG;

13.
no optimizer / training code invoked;

14.
common-random transition variates identical across paired arms;

15.
all learned probabilities finite;

16.
H learned probability in [0,1];

17.
U learned probabilities each in [0,1]
and sum to 1 within 1e-6;

18.
D2 preserved;

19.
G5_FULL OFF;

20.
NO_POOL semantics preserved;

21.
LOCAL_HEDGE preserved;

22.
ECHO_PHASE preserved;

23.
request-bound handoff preserved;

24.
duplicate mechanical evidence byte-identical.

POST-FREEZE PRIMARY MANIFESTS

After LU2AF1:

derive exactly five fresh paired Task-1 worlds.

Seed namespace:

LU2A-PRIMARY|LU2AF1|replicate

for replicate 1..5.

Worlds must be derived only after freeze.

No world replacement.

No rejection sampling based on scientific outcome.

Bind all five manifest identities
before any primary arm executes.

PRIMARY EXECUTION

For each of five worlds:

run TEACHER_V02;

run HYBRID_HU.

Run the complete five-world paired sweep twice.

Require raw sweep bytes
to be byte-identical
before scientific qualification opens.

PARENT PARITY

TEACHER_V02 must retain exact parent semantics.

If parent parity fails:

stop.

Do not interpret learned-arm science.

CAUSAL LEARNED-PARTICIPATION TELEMETRY

For every H evaluation record:

teacher probability;

learned probability;

absolute delta;

shared random variate;

teacher outcome;

hybrid outcome.

For every U evaluation record:

teacher [C,S,H,U];

learned [C,S,H,U];

TV distance;

shared random variate;

teacher outcome;

hybrid outcome.

Report:

H evaluation count;

H nonzero-probability-delta count;

H realized differing-transition count;

U evaluation count;

U nonzero-TV count;

U realized differing-transition count;

first causal divergence epoch;

number of epochs with different state vector;

whether trajectories later reconverge.

CAUSAL-ACTIVITY GATE

LU2A_LEARNED_PARTICIPATION_CAUSAL = TRUE iff:

H is evaluated at least once;

U is evaluated at least once;

at least one H evaluation
has absolute learned-vs-teacher probability delta > 1e-6;

at least one U evaluation
has learned-vs-teacher TV > 1e-6;

and across the five-world suite
at least one learned-controlled H or U transition
has a different realized outcome
under the shared random variate.

This gate prevents a preservation result
from being called learned closed-loop evidence
if the learned policy never causally changes a transition.

FUNCTIONAL PRESERVATION GATES

LU2A_FUNCTIONAL_PRESERVATION = TRUE iff
all of the following pass.

PHASE 0

HYBRID_HU Phase-0 completion
>=95% of paired TEACHER_V02
in all five worlds.

PHASE 4 ABSOLUTE

HYBRID_HU Phase-4 final-window completion
>=85%
in all five worlds.

PHASE 4 PAIRED

HYBRID_HU Phase-4 final-window completion
no more than 10 percentage points below
paired TEACHER_V02
in all five worlds.

CORRECT-COMPLETION AREA

Phases 1-4 HYBRID_HU area
>=90% of paired TEACHER_V02
in all five worlds.

Median paired area ratio
>=95%.

BACKLOG

HYBRID_HU final-16 total backlog
<=125% of paired TEACHER_V02
in all five worlds.

ANCHOR RELOCATION

HYBRID_HU anchor-rotation recovery latency
<=8 epochs
in all five worlds.

DEMAND REVERSAL

HYBRID_HU demand-reversal recovery latency
<=8 epochs
in all five worlds.

LESION

HYBRID_HU satisfies
the inherited V0.2 lesion criterion
in all five worlds.

SAFETY

incorrect DONE:
0
in every HYBRID_HU world.

No forbidden direct safety regression.

OPERATION COST

HYBRID_HU operations per correct completion
<=125% of paired TEACHER_V02
in all five worlds.

REPAIR / CORRUPTION

Retain inherited corruption / verification / repair integrity.

Report learned-vs-teacher
detection and repair outcomes.

No relaxation of existing zero-incorrect-DONE rule.

OVERALL SCIENTIFIC STATUS

LU2A_PARTIAL_LEARNED_CLOSED_LOOP_QUALIFIED = TRUE iff:

duplicate-primary gate passes;

parent parity passes;

all integrity probes pass;

LU2A_LEARNED_PARTICIPATION_CAUSAL = TRUE;

and

LU2A_FUNCTIONAL_PRESERVATION = TRUE.

INTERPRETATION

IF QUALIFIED

This establishes:

a frozen learned local updater
can causally control
H release and U recruitment
inside the developmental organism

while preserving the validated Task-1 envelope
when the unresolved committed-cell law
remains exact.

This does not authorize
replacing C/S stay-defect.

This does not authorize
V0.2 architecture promotion automatically.

Next:

replicate on a second fresh five-world set
before any architecture promotion
or expansion of learned authority.

IF FUNCTIONALLY PRESERVED BUT NOT CAUSAL

Result is scientifically inconclusive
for learned closed-loop participation.

Do not promote.

Use fresh worlds designed only
to increase natural H/U transition exposure
without changing the task law,
if justified before execution.

IF CAUSAL BUT FUNCTIONAL PRESERVATION FAILS

The learned H/U approximations
are not yet safe closed-loop substitutes
despite held-out imitation success.

Diagnose distribution shift.

Do not retune from the failed worlds.

IF BOTH FAIL

Close this substitution attempt
and revisit the learning target / training distribution.

NO POST-RESULT TUNING

After LU2AF1 freeze do not change:

weights;

model;

OBS-V1;

which heads are learned;

C/S teacher retention;

D2;

NO_POOL;

LOCAL_HEDGE;

ECHO_PHASE;

G5 setting;

Task-1 load;

scheduler;

expiry;

phase schedule;

lesion;

anchor relocation;

manifest count;

qualification bars;

or common-random policy.

PLAIN-SPEAK QUESTION

We already know the neural cell
can imitate two jobs well:

when an uncertain cell should release;

and what an uncommitted cell should become.

The third job,
holding or abandoning an existing commitment,
is still not learned accurately enough.

So LU-2A does not give the neural network that job.

Instead:

the neural cell controls uncertainty and recruitment;

the proven hand-written rule still controls commitment.

Then we put that hybrid cell
back into the actual organism
on five completely new worlds.

Because both versions use
the same random numbers,
we can see exactly when
the learned probabilities
cause the organism to make a different transition.

If the learned parts really change decisions
and the organism still develops,
adapts,
moves its work site,
handles demand reversal,
survives damage,
and stays correct,

then we have crossed an important boundary:

learned cell behavior is no longer
just imitating examples offline.

It is participating causally
inside the developmental system.

canonical_scientific_execution = false.
stab18_r1_touched = false.
DG1R05_CANONICAL_PRIMARY_CONSUMED = false.
